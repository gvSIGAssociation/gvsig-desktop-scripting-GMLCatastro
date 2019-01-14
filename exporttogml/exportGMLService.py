# encoding: utf-8

import gvsig
from org.gvsig.export.spi import ExportService
from org.gvsig.export import ExportLocator
from org.gvsig.tools import ToolsLocator
from org.gvsig.fmap.dal import DALLocator
from org.gvsig.fmap.mapcontext import MapContextLocator
from java.io import File
from java.util import ArrayList

from gvsig import commonsdialog
from gvsig import currentView
from gvsig import openStore

import os
from itertools import groupby

from libgml.gvsig2gmlcadastral import gvsig2gmlcadastral

class ExportGMLService(ExportService):
  def __init__(self, factory, parameters):
    ExportService.__init__(self)
    self.params = parameters
    self._factory = factory
    self.listeners = set()
    self._attributeNamesTranslator = None
    self._requestCancel = False
    self._taskStatus = ToolsLocator.getTaskStatusManager().createDefaultSimpleTaskStatus("Export")
    #range -> set value -> terminate/abort or cancel segun finalice
    self._openStores = ArrayList()
    
  def getTaskStatus(self):
    return self._taskStatus
  def isCancellationRequested(self):
    return self._requestCancel
    
  def cancelRequest(self):
    self._requestCancel = True
    
  def getFactory(self):
    return self._factory
    
  def getParameters(self):
    return self.params
    
  def addFinishListener(self, listener):
    self.listeners.add(listener)
    
  def getAttributeNamesTranslator(self):
        if self._attributeNamesTranslator == None:
          self._attributeNamesTranslator = ExportLocator.getServiceManager().createAttributeNamesTranslator()
        return self._attributeNamesTranslator
  def getTargetOpenStoreParameters(self): # return List<OpenDataStoreParameters> 
    # lista de parameters que se usan para abrir los ficheros que se han creado
    return self._openStores
    
  def export(self, featureSet):
    self._openStores = ArrayList()
    # exportacion a gml's
    #def gml(self, fpanel, featureStore, projection):
    selection = featureSet # featureStore
    projection = self.getParameters().getTargetProjection() #getProjection() 
    #TODO HACER QUE SE ADAPTE LA GEOMETRIA A LA PROYECCION

    #init
    dup = []
    for feature in selection:
        dup.append(feature.localId)

    cd = 1
    if max([len(list(group)) for key, group in groupby(dup)]) > 1:
      message = u"Se han detectado campos localId duplicados, esto no permite su validacion en el Catastro. Desea asigna un valor localId unico, no asignarselo o cancelar el proceso?"
      cd = commonsdialog.confirmDialog(message, title="", optionType=commonsdialog.YES_NO_CANCEL, messageType=commonsdialog.IDEA, root=None)
      if cd == 2:
        return False

    self.taskStatus.setRangeOfValues(0, selection.getSize())
    n = 0
    #p_cargar = fpanel.chbCargar.isSelected()

    pathresultados = self.getParameters().getFile().getAbsolutePath() #fpanel.txtPath.getText()
    if not os.path.exists(pathresultados) and not pathresultados=='':
      commonsdialog.msgbox("Ruta de carpeta invalida")
      return
    for feature in selection: #.features():
      n+=1
      self.taskStatus.setCurValue(n)
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
      p_unico = self.getParameters().getUseUniqueName() #fpanel.chbUnico.isSelected()
      p_crs = projection.getFullCode()
      #import pdb
      #pdb.set_trace()

      # Conversion del store a GML
      gmlfile = gvsig2gmlcadastral(feature=feature,
                     pathresultados=pathresultados,
                     p_label = p_label,
                     p_crs = p_crs,
                     p_unico = p_unico,
                     n = n
                    )


      #if True:
      """
      openStoreFile = openStore('GMLDataStoreProvider',xsdSchema=None,
                                       gfsSchema=None,
                                       file=gmlfile,
                                       CRS=p_crs,
                                       connectionString=None,
                                       layerName="CadastralParcel",
                                       defaultGeometryField=None,
                                       ignoreSpatialFilter=True,
                                       ProviderName="GMLDataStoreProvider")
      """
      gmlparams = DALLocator.getDataManager().createStoreParameters("GMLDataStoreProvider")
      gmlparams.setCRS(projection)
      gmlparams.setFile(File(gmlfile))
      if p_label!= "":
          layername = p_label
      else:
          layername = "CadastralParcel"
      gmlparams.setLayerName(layername)
      gmlparams.setGfsSchema(None)
      gmlparams.setXsdSchema(None)
      gmlparams.setConnectionString(None)
      gmlparams.setDefaultGeometryField(None)
      #gmlparams.setDynValue("ignoreSpatialFilter", True)
      openStoreFile = DALLocator.getDataManager().openStore("GMLDataStoreProvider",gmlparams)
      #layer = MapContextLocator.getMapContextManager().createLayer(layername, openStoreFile.getStore())
      #gvsig.currentView().addLayer(layer)
      self.getTargetOpenStoreParameters().add(gmlparams)
  
    
def main(*args):

    #Remove this lines and add here your code
    sv = ExportGMLService(None, None)
    print "hola mundo"
    pass
