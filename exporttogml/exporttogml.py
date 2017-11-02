# -*- coding: utf-8 -*-

import gvsig
reload(gvsig)
from gvsig import *
from gvsig import uselib
from gvsig import commonsdialog
import os

uselib.use_plugin("org.gvsig.exportto.app.mainplugin")
from org.gvsig.exportto.swing.prov.file import AbstractExporttoFileProvider
from org.gvsig.exportto.swing.spi import ExporttoSwingProvider
from org.gvsig.exportto.swing import ExporttoSwingLibrary
from org.gvsig.tools.library import AbstractLibrary
from org.gvsig.exportto.swing.spi import ExporttoSwingProviderLocator

from org.gvsig.exportto.swing.prov.file import AbstractExporttoFileProviderFactory
from org.gvsig.exportto.swing import ExporttoSwingManager
from org.slf4j import LoggerFactory
from org.gvsig.tools.task import AbstractMonitorableTask
from org.gvsig.exportto import ExporttoService
from org.gvsig.exportto import ExporttoServiceFinishAction

#import libgml.crea_gvsig2gml
#reload(libgml.crea_gvsig2gml)

import libgml.gvsig2gmlcadastral
reload(libgml.gvsig2gmlcadastral)

from libgml.gvsig2gmlcadastral import gvsig2gmlcadastral
from gvsig.libs.formpanel import FormPanel
from org.gvsig.exportto.swing.spi import ExporttoSwingProviderPanel
from org.gvsig.fmap.mapcontext import MapContextLocator

from java.io import File
from os import path as ospath
from itertools import groupby

# <div>Icons made by <a href="http://www.flaticon.com/authors/madebyoliver" 
# title="Madebyoliver">Madebyoliver</a> from <a href="http://www.flaticon.com" 
# title="Flaticon">www.flaticon.com</a> is licensed by 
# <a href="http://creativecommons.org/licenses/by/3.0/" title="Creative Commons BY 3.0" target="_blank">CC 3.0 BY</a></div>
#
# Agradecer a sec4qgis la publicacion de un manual detallado
#
""" Abrir gml con formato:

gvsig-desktop-2.3.0-2426-testing-win-x86_64\gvSIG\extensiones\org.gvsig.gdal.app.mainplugin\gdal\bin\gdal-data
### C:\gvdevel\gvsig-desktop-2.3.0-2426-testing-win-x86_64\gvSIG\extensiones\org.gvsig.gdal.app.mainplugin\gdal\bin\gdal-data\inspire_cp_CadastralParcel.gfs """

class ExportName(FormPanel, ExporttoSwingProviderPanel):
    def __init__(self):
        FormPanel.__init__(self, getResource(__file__,"exporttopanel.xml"))
        
    def btnPath_click(self,*args):
        ofolderd = commonsdialog.openFolderDialog(title='', initialPath=None, root=None)
        self.txtPath.setText(ofolderd[0])
        return ofolderd
        
    def getPanelTitle(self):
        return "Panel"
        
    def enterPanel(self):
        print "Panel print"
        
              
    def isValidPanel(self):
        #from org.gvsig.exportto.swing.spi import ExporttoPanelValidationException
        #if not os.path.exists(self.txtPath.getText()) or not '':
        #      print "txtpath: ", self.txtPath.getText()
        #      raise ExporttoPanelValidationException("mensaje de por que no es valido el panel")
        #    commonsdialog.msgbox("La ruta no existe o no es una carpeta")
        #    return False
        return True
        
class ExporttoGMLService(AbstractMonitorableTask, ExporttoService):
    def __init__(self, fpanel, featureStore, projection):
          #logger = LoggerFactory.getLogger(ExporttoGMLService)
          self.MAX_FIELD_NAME_LENGTH = 10
          self.fpanel = fpanel
          self.featureStore = featureStore
          self.projection = projection
          print "\nExporttoGMLService:init.fpanel",fpanel, type(fpanel)
          #r: DefaultExporttoSwingProviderServices
          #taskStatus = super(AbstractMonitorableTask, self)
          self.taskStatus.setTitle("Exporting surfaces")
          #Range en funcion de el numero de entidades en el featureStore
          #self.taskStatus.setRangeOfValues(0, 100)
          #self.taskStatus.setCurValue(0)
          self.exporttoServiceFinishAction = ExporttoServiceFinishAction
        
    def export(self,*args):
          print "\n*** ExporttoGMLService:export"
          print "ExportotoGMLService:export.args ", args, type(args)
          #print "*** fpanel", self.fpanel.selectFileOptionPanel.getSelectedFile()
          #self.gml(self.fpanel, self.featureStore, self.projection)
          self.gml(self.fpanel, args[0], self.projection)
    
    def gml(self, fpanel, featureStore, projection):
        print "FEATURESTORE: ", featureStore, type(featureStore)
        selection = featureStore
        #p_selection = fpanel.chbSelection.isSelected()
        #if p_selection == True:
        #    selection = featureStore.getSelection()
        #else:
        #    selection = featureStore.features()
        
        dup = []
        for feature in selection:
            dup.append(feature.localId)

        cd = 1
        if max([len(list(group)) for key, group in groupby(dup)]) > 1:
            message = "Se han detectado campos localId duplicados, esto no permite su validacion en el Catastro. Desea asignar valor localId unico, no asignarselo o cancelar el proceso?"
            cd = commonsdialog.confirmDialog(message, title="", optionType=commonsdialog.YES_NO_CANCEL, messageType=commonsdialog.IDEA, root=None)
            if cd == 2:
                return False
                
        self.taskStatus.setRangeOfValues(0, selection.getSize())
        n = 0
        p_cargar = fpanel.chbCargar.isSelected()
        
        pathresultados = fpanel.txtPath.getText()
        if not ospath.exists(pathresultados) and not pathresultados=='':
            commonsdialog.msgbox("Ruta de carpeta invalida")
            return
            
        for feature in selection: #.features():
            n+=1
            self.taskStatus.setCurValue(n)
            print "GML SOBRE: ", feature.geometry(), type(feature.geometry())
            if self.taskStatus.isCancellationRequested():
                return
                    
            try:
                p_label = feature.get("localId")
                te = feature.get("nameSpace")
            except:
                commonsdialog.msgbox("La capa debe de contener los campos localId y nameSpace de forma obligatoria")
                return
                
            if cd == 0:
                p_label = ""
            p_unico = fpanel.chbUnico.isSelected()
            p_crs = projection.toString()
    
            # Conversion del store a GML
            gmlfile = gvsig2gmlcadastral(feature=feature, 
                           pathresultados=pathresultados,
                           p_label = p_label, 
                           p_crs = p_crs, 
                           p_unico = p_unico,
                           n = n
                          )
    
            
            if p_cargar == True:
                os = openStore('GMLDataStoreProvider',xsdSchema=None,
                                                 gfsSchema=None,
                                                 file=gmlfile,
                                                 CRS=p_crs,
                                                 connectionString=None,
                                                 layerName="CadastralParcel",
                                                 defaultGeometryField=None,
                                                 ignoreSpatialFilter=True,
                                                 ProviderName="GMLDataStoreProvider")
                if p_label!= "":
                    layername = p_label
                else:
                    layername = "CadastralParcel"
                    
                layer = MapContextLocator.getMapContextManager().createLayer(layername, os.getStore())
                currentView().addLayer(layer)

        print "ExportotoGMLService:gml-done"
        
        return True
        
    def setFinishAction(self, exporttoServiceFinishAction):
        self.exporttoServiceFinishAction = exporttoServiceFinishAction
        
    def finishAction(self):
        #self.taskStatus.setCurValue(99)
        pass
          
class ExporttoGMLProvider(AbstractExporttoFileProvider):
    def __init__(self, providerServices, featureStore, projection):
        AbstractExporttoFileProvider.__init__(self, providerServices, featureStore, projection)
        self.featureStore = featureStore
        self.projection = projection
        #self.selectFileOptionPanel =  AbstractExporttoFileProvider.getPanelAt(self, 0) #providerServices
        self.exportname = ExportName()

    def getPanelAt(self, index):
        #if index == 0:
        #    return AbstractExporttoFileProvider.getPanelAt(self, 0)
        #else:
        return self.exportname

    def getPanelCount(self):
        return 1 #AbstractExporttoFileProvider.getPanelCount(self)+1

    def createExporttoService(self):
        print "ExporttoGMLProvider:createExporttoService"
        return ExporttoGMLService(self.exportname, self.featureStore, self.projection) #self.selectFileOptionPanel, self.featureStore, self.projection)
        
class ExporttoGMLProviderFactory(AbstractExporttoFileProviderFactory):
    def __init__(self,*args):
        AbstractExporttoFileProviderFactory.__init__(self, [ExporttoSwingManager.VECTORIAL_TABLE_WITH_GEOMETRY])
        self.PROVIDER_NAME = "GML Catastro"
        
    def create(self, parameters, services): #, parameters, services):
        print "ExporttoGMLProviderFactory-created"
        print "ExporttoGMLProviderFactory.parameters:",parameters
        print "ExporttoGMLProviderFactory.services:", services
        print "ExporttoGMLProviderFactory.parameters-type", type(parameters)

        featureStore = parameters.getDynValue("FeatureStore")
        projection = parameters.getDynValue("Projection")
        return ExporttoGMLProvider(services, featureStore, projection)
        
    def getName(self):
        return self.PROVIDER_NAME
        
class ExporttoGMLProviderLibrary(AbstractLibrary):
    def __init__(self, *args):
        self.doRegistration()
        self.doPostInitialize()

    def doRegistration(self):
        self.super__registerAsServiceOf(ExporttoSwingLibrary)

    def doInitialize(self):
        pass

    def doPostInitialize(self):
        providerManager = ExporttoSwingProviderLocator.getManager()
        providerManager.addProviderFactory(ExporttoGMLProviderFactory())
        
def main(*args):
    
    #x = ExporttoGMLCatastro()
    ExporttoGMLProviderLibrary()
    
    return

