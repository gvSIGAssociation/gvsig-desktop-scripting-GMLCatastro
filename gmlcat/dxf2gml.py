# encoding: utf-8

import gvsig
from gvsig import geom
from gvsig.geom import *
from gvsig import commonsdialog

def main(*args):
    dxf2gml()
    
def dxf2gml(dxffile=None):

    if dxffile==None:
        #dxffile = "/home/osc/gis-data/2016_06_ejemplos_catastro/parcela_huecos/ConsultaMasiva_EPSG_25830.dxf"
        dxffile = gvsig.getResource(__file__, "datos", "ConsultaMasiva_EPSG_25830.dxf")

    crs_view_code = gvsig.currentView().getProjectionCode()
    print crs_view_code
    crs = commonsdialog.inputbox("Introduce CRS del DXF (si se deja en blanco se asigna crs de la vista: {0})".format(str(crs_view_code)), "Importar fichero DXF", 1, str(crs_view_code))

    if crs == None:
        return
    elif crs == '':
        crs = crs_view_code #"EPSG:25830"
    else:
        #Check for a valid epsg
        pass
    dxf = gvsig.openStore('DXF', File=dxffile,
                                 CRS=crs,
                                 ProviderName="DXF")

    #sch = gvsig.createFeatureType() #dxf.getSchema())

    #sch.append("localId", "STRING", 30)
    #sch.append("nameSpace", "STRING", 30)
    #sch.get("GEOMETRY").setGeometryType(geom.POINT, geom.D2)
    #shpref = gvsig.createShape(sch, prefixname="refpoints")
    
    dxfpoints = dxf.features("Layer='RefCatastral'")


    sch = gvsig.createFeatureType() #dxf.getSchema())
    sch.append("localId", "STRING", 30)
    sch.append("nameSpace", "STRING", 30)
    sch.append("GEOMETRY", "GEOMETRY", 30)
    sch.get("GEOMETRY").setGeometryType(geom.MULTIPOLYGON, geom.D2)
    
    shppol= gvsig.createShape(sch, prefixname="parcelas")

    #dxffeatures = dxf.features()
    dxfparcel = dxf.features("Layer='Parcela'")
    for feature in dxfparcel:
        gfeature = feature.geometry().toPolygons()
        values = {"localId": "", "nameSpace":"DGC", "GEOMETRY": gfeature}
        for i in dxfpoints:
            if i.geometry().intersects(gfeature):
                values["localId"] = i.get("Text")

        shppol.append(values)
            
    shppol.commit()
    
    gvsig.currentView().addLayer(shppol)
