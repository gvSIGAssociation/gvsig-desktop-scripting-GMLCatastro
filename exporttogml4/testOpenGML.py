# encoding: utf-8

import gvsig

from java.io import File
from org.gvsig.fmap.dal import DALLocator
from org.gvsig.fmap.mapcontext import MapContextLocator
import os

def main(*args):
  projection = gvsig.getCRS("EPSG:25830")
  gmlfile = gvsig.getResource(__file__, "testparcela.gml")
  
  gmlparams = DALLocator.getDataManager().createStoreParameters("GMLDataStoreProvider")
  gmlparams.setCRS(projection)
  print gmlfile, type(gmlfile)
  print "*** existe path:", os.path.exists(gmlfile)
  gmlparams.setFile(File(gmlfile))
  layername = "CadastralParcel"
  gmlparams.setLayerName(layername)
  gmlparams.setGfsSchema(None)
  gmlparams.setXsdSchema(None)
  gmlparams.setConnectionString(None)
  gmlparams.setDefaultGeometryField(None)
  gmlparams.setDynValue("ignoreSpatialFilter", True)
  print "isvalid:", gmlparams.isValid()
  openStoreFile = DALLocator.getDataManager().openStore("GMLDataStoreProvider",gmlparams)
  layer = MapContextLocator.getMapContextManager().createLayer(layername, openStoreFile.getStore())
  gvsig.currentProject().getView("mivista").addLayer(layer)