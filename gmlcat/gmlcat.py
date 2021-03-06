# encoding: utf-8

import dxf2gml
reload(dxf2gml)

import extraerentidades
reload(extraerentidades)

from gvsig.libs.formpanel import FormPanel
import os

from gvsig import commonsdialog, currentView, getResource, openStore, currentLayer
from org.gvsig.scripting.app.extension import ScriptingExtension
from org.gvsig.fmap.mapcontext import MapContextLocator

from org.gvsig.tools import ToolsLocator
from org.gvsig.tools.swing.api import ToolsSwingLocator
from java.io import File

from org.gvsig.andami import PluginsLocator
from gvsig import getResource

def visorPDF(rutaAbsoluta):
    formatManagers = ToolsLocator.getExtensionPointManager().get("HyperLinkAction")
    pdfManager = formatManagers.get("PDF_format").create()
    uri = File(str(rutaAbsoluta)).toURI()
    panel = pdfManager.createPanel(uri)
    windowManager = ToolsSwingLocator.getWindowManager()
    windowManager.showWindow(panel,"Visor PDFs",windowManager.MODE.WINDOW)
    
class GMLCatExtension(ScriptingExtension):
    def __init__(self):
      pass
  
    def canQueryByAction(self):
      return True
  
    def isEnabled(self,action):
      return currentView()!=None
  
    def isVisible(self,action):
      return currentView()!=None
      
    def execute(self,actionCommand, *args):
        l = GMLCat()
        l.showTool("GMLCatastro")
    
class GMLCat(FormPanel):
        def __init__(self):
            FormPanel.__init__(self, getResource(__file__, "gmlcat.xml"))
            self.setPreferredSize(450,200)
            
        def btnDXFImport_click(self, *args):
            fc = commonsdialog.filechooser("OPEN_FILE", title="", initialPath=None,  multiselection=False, filter = None, fileHidingEnabled=True, root=None)
            if fc == None:
                return
            if not os.path.exists(fc):
                commonsdialog.msgbox("Ruta de fichero invalida")
                return
            
            filename, file_extension = os.path.splitext(fc)
            
            if file_extension == ".dxf":
                dxf2gml.dxf2gml(dxffile=fc)
            elif file_extension == ".gml" or file_extension == ".GML":
                layer = openGML(gmlfile=fc, p_crs=currentView().getProjectionCode())
                extraerentidades.extraerentidades(layer=layer)
            else:
                commonsdialog.msgbox("Fichero con extension no correspondiente a: gml o dxf")

        def btnOpenGML_click(self, *args):
            fc = commonsdialog.filechooser("OPEN_FILE", title="", initialPath=None,  multiselection=False, filter = None, fileHidingEnabled=True, root=None)

            if fc == None or not os.path.exists(fc):
                return
            layer = openGML(gmlfile=fc, p_crs=currentView().getProjectionCode())
            currentView().addLayer(layer)
            env = layer.getFullEnvelope()
            currentView().centerView(env)
            
        def btnExtraer_click(self, *args):
            extraerentidades.extraerentidades(layer=currentLayer())

        def btnHelp_click(self, *args):
            pdfpath = getResource(__file__, "gmlcatastro_0_1.pdf")
            visorPDF(pdfpath)
            
def openGML(gmlfile, p_crs):
    #if os.path.exists(os.path.splitext(gmlfile)[0]+'.gfs'):
    #    gfs = os.path.splitext(gmlfile)[0]+'.gfs'
    #    print "--usar gfs"
    #else:

    pluginsManager = PluginsLocator.getManager() 
    plugin = pluginsManager.getPlugin("org.gvsig.gdal.app.ogr.gml") 
    f = plugin.getPluginDirectory()
    gfs = getResource(f.getAbsolutePath(), "schemas", "catastro.gfs")
    
    gmlstore = openStore('GMLDataStoreProvider',xsdSchema=None,
                                     gfsSchema=gfs,
                                     file=gmlfile,
                                     CRS=p_crs,
                                     connectionString=None,
                                     layerName="CadastralParcel",
                                     defaultGeometryField=None,
                                     ignoreSpatialFilter=True,
                                     ProviderName="GMLDataStoreProvider")
    layer = MapContextLocator.getMapContextManager().createLayer("CadastralParcel", gmlstore.getStore())
    return layer


def main(*args):
    l = GMLCat()
    l.showTool("GMLCatastro")
    