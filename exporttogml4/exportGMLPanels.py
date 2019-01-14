# encoding: utf-8

import gvsig
from org.gvsig.export.swing.spi import AbstractExportPanels
from org.gvsig.export.swing import ExportSwingLocator
#from org.gvsig.export.swing.spi import ExportPanelsManager
from org.gvsig.export.swing.spi import ExportPanel
from gvsig.libs.formpanel import FormPanel
from org.gvsig.export.dbf.swing.panels import EncodingPanel
from org.gvsig.tools.swing.api import ToolsSwingLocator
import os
from org.gvsig.andami import Utilities
from java.io import File
from javax.swing.filechooser import FileFilter

class MyFileFilter(FileFilter):
   def accept(self, f):
     return (f.isDirectory())
   def getDescription(self):
     return None
     
class ExportGMLPanels(AbstractExportPanels):
  def __init__(self, factory, processPanel, parameters):
    AbstractExportPanels.__init__(self, factory, processPanel, parameters)
    self.initPanels()
  
  def initPanels(self):
        manager = ExportSwingLocator.getExportPanelsManager()
        
        #self.add(EncodingPanel(
        #        self.getProcessPanel(), 
        #        self.getParameters()
        #    )
        #)
        self.add(GMLPanelOptions(
                 self.getProcessPanel(),
                 self.getParameters()
             )
        )

class GMLPanelOptions(FormPanel, ExportPanel):
  def __init__(self, processPanel, parameters):
    ExportPanel.__init__(self)
    FormPanel.__init__(self, gvsig.getResource(__file__,"exportGMLPanels.xml"))
    # hay un picker para folder
    self.pickerFolder = None
    self.processPanel = processPanel
    self.params = parameters
    self.initComponents()
  def initComponents(self):
    dialogTitle = "_Select_folder"
    fileChooserID = "idPathGMLSelector"
    seticon = True
    self.pickerFolder = ToolsSwingLocator.getToolsSwingManager().createFolderPickerController(
       self.txtPath,
       self.btnPath)
    #   dialogTitle ,
    #   fileChooserID,
    #   None,
    #   seticon)
    pass
  def getIdPanel(self):
    return "GMLPanelOptions"
  def getTitlePanel(self):
    pass
  def validatePanel(self):
    return True
  def enterPanel(self):
    initialPath = File(Utilities.TEMPDIRECTORYPATH)
    self.pickerFolder.set(initialPath)
    self.pickerFolder.setFileFilter(MyFileFilter())
    
  def previousPanel(self):
    pass
  def nextPanel(self):
    #recoger valores del formulario y guardarlos en parameters
    filePicker = self.pickerFolder.get()
    #import pdb
    #pdb.set_trace()
    self.params.setFile(filePicker)
    self.params.setUseUniqueName(self.chbUnico.isSelected())
    pass
    
def main(*args):

    g = GMLPanelOptions(None, None)
    g.asJComponent()
