# encoding: utf-8

import gvsig
from gvsig import commonsdialog
from gvsig import geom

def extraerentidades(layer):
    if layer==None:
        gvsig.commonsdialog.msgbox("Ninguna capa seleccionada en la Vista")
        return
    selection = layer.getSelection()
    if selection.getCount() == 0:
        features = layer.features()
    else:
        features = selection

    sch = gvsig.createFeatureType(layer.getSchema())
    if "localId" not in sch.getAttrNames():
        sch.append("localId", "STRING", 30)
        
    if "nameSpace" not in sch.getAttrNames():
        sch.append("nameSpace", "STRING", 30)

    try:
        shp = gvsig.createShape(sch, prefixname="Extraccion")
    except:
        sch = gvsig.createFeatureType()
        sch.append("localId", "STRING", 30)
        sch.append("nameSpace", "STRING", 30)
        sch.append(layer.getSchema().getDefaultGeometryAttribute().getName(), "GEOMETRY")
        sch.getDefaultGeometryAttribute().setGeometryType(geom.MULTIPOLYGON, geom.D2)
        shp = gvsig.createShape(sch, prefixname="ExtractionNewSchema")
        
    store = shp.getFeatureStore()
    shp.edit()
    attr = layer.getSchema().getAttrNames()
    name = "ExtractionNewSchema"
    for feature in features:
        new = store.createNewFeature(feature)
        if "inspireId_localId" in attr:
            name = feature.get("inspireId_localId")
            new.set("localId", feature.get("inspireId_localId")) 
        if "localId" in attr:
            name = feature.get("localId")
        if "inspireId_namespace" in attr:
            new.set("nameSpace", feature.get("inspireId_namespace"))

        
        store.update(new)
       
        #values = f.getValues()
        #shp.append(values)
        
    shp.commit()
    gvsig.currentView().addLayer(shp)

    if features.getSize()==1:
        shp.setName(name)
        
    env = shp.getFullEnvelope()
    gvsig.currentView().centerView(env)
    
def main(*args):

    #Remove this lines and add here your code

    extraerentidades(gvsig.currentLayer())
    pass
