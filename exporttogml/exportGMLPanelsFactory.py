# encoding: utf-8

import gvsig
from org.gvsig.export.swing.spi import AbstractExportPanelsFactory
from exportGMLFactory import SERVICE_NAME
from exportGMLPanels import ExportGMLPanels

class ExportGMLPanelsFactory(AbstractExportPanelsFactory):
  def __init__(self):
    AbstractExportPanelsFactory.__init__(self, SERVICE_NAME)

  def createPanels(self, processPanel, exportParameters):
    return ExportGMLPanels(self, processPanel, exportParameters)

def main(*args):

    pass
