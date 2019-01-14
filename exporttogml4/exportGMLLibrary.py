# encoding: utf-8

import gvsig
from gvsig import uselib
uselib.use_plugin("org.gvsig.exportto.app.mainplugin")
from org.gvsig.export.swing import ExportSwingLibrary
from org.gvsig.export.swing import ExportSwingLocator
from org.gvsig.tools.library import AbstractLibrary
from org.gvsig.export import ExportLibrary
from org.gvsig.export import ExportLocator
from exportGMLPanelsFactory import ExportGMLPanelsFactory
from exportGMLFactory import ExportGMLFactory



def main(*args):

    ExportGMLLibrary()
    
class ExportGMLLibrary(AbstractLibrary):
  def __init__(self, *args):
      self.doRegistration()
      self.doPostInitialize()
      
  def doRegistration(self):
    self.super__registerAsServiceOf(ExportSwingLibrary)
    self.super__registerAsServiceOf(ExportLibrary)
        
  def doInitialize(self): 
    pass
    
  def doPostInitialize(self):
    manager = ExportLocator.getServiceManager()
    swingManager = ExportSwingLocator.getExportPanelsManager()
    
    manager.register(ExportGMLFactory())
    swingManager.register(ExportGMLPanelsFactory())