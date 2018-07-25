# encoding: utf-8

import gvsig
import addons.GMLCatastro.exporttogml
reload(addons.GMLCatastro.exporttogml)

from addons.GMLCatastro import exporttogml

import addons.GMLCatastro.exporttogml4 as addGMLExport4
#reload(addons.GMLCatastro.exporttogml4)

import addons.GMLCatastro.gmlcat
reload(addons.GMLCatastro.gmlcat)

from org.gvsig.andami import PluginsLocator
from org.gvsig.scripting.app.extension import ScriptingExtension
from org.gvsig.tools.swing.api import ToolsSwingLocator

from java.io import File
from org.gvsig.app import ApplicationLocator
import os

from addons.GMLCatastro.gmlcat.gmlcat import GMLCatExtension
    
def selfRegister():

  application = ApplicationLocator.getManager()

  icon_show = File(gvsig.getResource(__file__,"gml-cat.png")).toURI().toURL()

  iconTheme = ToolsSwingLocator.getIconThemeManager().getCurrent()
  iconTheme.registerDefault("scripting.gml-cat", "action", "tools-gml-cat-show", None, icon_show)
  
  extension = GMLCatExtension()

  actionManager = PluginsLocator.getActionInfoManager()
  action_show = actionManager.createAction(
    extension, 
    "tools-gml-cat-show", # Action name
    "GMLCat", # Text
    "show", # Action command
    "tools-gml-cat-show", # Icon name
    None, # Accelerator
    1009000000, # Position 
    "GMLCat" # Tooltip
  )
  action_show = actionManager.registerAction(action_show)
  application.addTool(action_show, "GMLCat")

  
def main(*args):
    selfRegister()
    exporttogml.selfRegister()
    #addons.GMLCatastro.exporttogml4.exporttogml.ExporttoGML4ProviderLibrary()
    addGMLExport4.exporttogml.ExporttoGML4ProviderLibrary()
    pass
