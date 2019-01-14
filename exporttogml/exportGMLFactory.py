# encoding: utf-8

import gvsig
from org.gvsig.export.spi import AbstractExportServiceFactory
from exportGMLParameters import ExportGMLParameters
from exportGMLService import ExportGMLService

SERVICE_NAME = "ExportGML3"

class ExportGMLFactory(AbstractExportServiceFactory):
  def __init__(self):
    AbstractExportServiceFactory.__init__(
      self,
      SERVICE_NAME,
      "Export GML: CPV3 (Parcela Catastral version 3)",
      "Exportador a version 3"
      )
  def createService(self,parameters):
    return ExportGMLService(self, parameters)
    
  def createParameters(self):
    return ExportGMLParameters()
    
  def hasTabularSupport(self):
        return True
        
  def hasVectorialSupport(self):
        return True
def main(*args):
    egf = ExportGMLFactory()
