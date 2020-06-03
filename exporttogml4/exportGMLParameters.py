# encoding: utf-8

import gvsig
from org.gvsig.tools.util import HasAFile
from org.gvsig.export.spi import AbstractExportParametersGeometry

class ExportGMLParameters(AbstractExportParametersGeometry,HasAFile):
  def __init__(self, factory):
    AbstractExportParametersGeometry.__init__(self, factory)
    self.factoryName = factory.getName()
    self.useUniqueName = True #boolean
    self.folderFile  = None #file
  def needsSelectTargetProjection(self):
    return True # para que saque el panel de proyeccion
  def getFile(self):
    return self.folderFile
  def setFile(self, folderFile):
    self.folderFile = folderFile
  def getUseUniqueName(self):
    return self.useUniqueName
  def setUseUniqueName(self, uniqueName):
    self.useUniqueName = uniqueName
  def getServiceName(self):
    return self.factoryName
    
def main(*args):

    #Remove this lines and add here your code

    print "hola mundo"
    pass
