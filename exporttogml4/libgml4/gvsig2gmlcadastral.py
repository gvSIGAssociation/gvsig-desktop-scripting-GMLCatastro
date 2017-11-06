import sys
from gvsig import geom
from gvsig import commonsdialog
from gvsig import getTempFile
import os.path
from gvsig import *
from org.gvsig.andami import Utilities
import os

def reProjectBetweenCRS(point, crs_in, crs_out):
    v1 = getCRS(crs_in)
    v2 = getCRS(crs_out)
    ICoordTrans1 = v1.getCT(v2)
    point.reProject(ICoordTrans1)
    return point

    
def gvsig2gmlcadastral(feature, pathresultados='', p_label="Parcela", p_crs="EPSG:25830", p_unico=True, n=1):
    """ Convierte una entidad en un gml """

    sch = createSchema()
    sch.append("GEOMETRY", "GEOMETRY")
    sch.get("GEOMETRY").setGeometryType(geom.POLYGON, geom.D2)

    #selection = currentLayer().getSelection()
    #if selection.getCount() == 0 or selection.getCount() > 1:
    #    commonsdialog.msgbox("None feature selected or more than one feature", "Error", 1)
    #    return
    #    
    #for f in selection:
    #    feature = f
        
    if p_label=="":
        p_label = "Parcela" + str(n)
            

    # Path gml file
    if pathresultados=='':
        pathresultados = Utilities.TEMPDIRECTORYPATH
        if not os.path.isdir(pathresultados):
            os.makedirs(pathresultados)
            
    if p_unico==True:
        tempgml = getTempFile(p_label,".gml", pathresultados)
    elif p_unico==False:
        tempgml = os.path.join(pathresultados, p_label+".gml")

    ############################## PREPARACION DEL GML ##############################

    with open(tempgml, 'w') as filegml:
        ##### PREPARAR GEOMETRIA
        polygon = feature.geometry()
        p_multisurface = ""

        crs_view = currentLayer().getProjectionCode()#.split(":")[1]
        crs_gml = p_crs.split(":")[1]
        if crs_view != crs_gml:
            polygon = reProjectBetweenCRS(polygon, crs_view, p_crs)

        p_area = polygon.area() # Area total del multipoligono
        
        ##### Crear SURFACE MEMBER
        idn = 1
        if polygon.getGeometryType().getName() == "MultiPolygon2D":
            for i in polygon:
                p_multisurface += create_surfaceMember(i,  p_label, crs_gml, idn) #"exterior", listarCoordenadas(i), i.getNumVertices())
                idn += 1
        else:
            p_multisurface += create_surfaceMember(polygon, p_label, crs_gml, idn) #"exterior", listarCoordenadas(i), i.getNumVertices())

        ##### GRABAR SURFACE MEMBER
        filegml.write(plantilla(p_area, p_multisurface, p_label, crs_gml))
        
    filegml.close()

    return tempgml

def create_surfaceMember(polygon, p_label, p_crs, idn):

        ################### POLYGONPATH: p_polygonpath
        p_polygonpath = plantilla_geometria("exterior", listarCoordenadas(polygon), polygon.getNumVertices())
        
        ### Crear coordenadas del los anillos
        numrings = polygon.getNumInteriorRings()
        if numrings >= 1:
            for nr in range(numrings):
                ring = polygon.getInteriorRing(nr)
                p_polygonpath += plantilla_geometria("interior",listarCoordenadas(ring), ring.getNumVertices())
                
        ################### SURFACE MEMBER
        p_surfacemember = plantilla_surfaceMember(p_polygonpath, p_label, p_crs, idn)
        
        return p_surfacemember
    
def listarCoordenadas(geometria):
    """ Devuelve string con el listado de coordenadas """
    vertices = geometria.getNumVertices()
    p_coord = ""
    for i in range(0, vertices):
        pt = geometria.getVertex(i)
        p_coord += "" + str(pt.getX()) + " " + str(pt.getY()) + "\n"
    return p_coord 
  
def plantilla_geometria(p_tipo, p_coord, p_count):
  strcoord = """<gml:%s>
                        <gml:LinearRing>
                        <gml:posList srsDimension="2" count="%s">
%s                        </gml:posList>
                        </gml:LinearRing>
                        </gml:%s>
""" % (p_tipo, p_count, p_coord, p_tipo)
  return strcoord

def plantilla_surfaceMember(p_polygonpath, p_label, p_crs, idn):
    values = {"p_polygonpath":p_polygonpath, "p_label":p_label, "p_crs":p_crs, "idn":idn}
    return """<gml:surfaceMember>
               <gml:Surface gml:id="Surface_ES.LOCAL.CP.{p_label}.Polygon_{idn}" srsName="urn:ogc:def:crs:EPSG:{p_crs}">
                  <gml:patches>
                    <gml:PolygonPatch>
                        {p_polygonpath}
                    </gml:PolygonPatch>
                  </gml:patches>
                </gml:Surface>
             </gml:surfaceMember>
""".format(**values)
              
def plantilla(p_area, p_polygons, p_label, p_crs):
    values = {"p_area":p_area, "p_polygons":p_polygons, "p_label":p_label, "p_crs":p_crs}
    return """<?xml version="1.0" encoding="utf-8"?>
<FeatureCollection xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:gml="http://www.opengis.net/gml/3.2" xmlns:gco="http://www.isotc211.org/2005/gco" xmlns:cp="http://inspire.ec.europa.eu/schemas/cp/4.0" xmlns:gmd="http://www.isotc211.org/2005/gmd" xsi:schemaLocation="http://www.opengis.net/wfs/2.0 http://schemas.opengis.net/wfs/2.0/wfs.xsd  
http://inspire.ec.europa.eu/schemas/cp/4.0 http://inspire.ec.europa.eu/schemas/cp/4.0/CadastralParcels.xsd" xmlns="http://www.opengis.net/wfs/2.0" timeStamp="2017-05-10T17:30:07" numberMatched="1" numberReturned="1">
    <member>
        <cp:CadastralParcel gml:id="ES.LOCAL.CP.{p_label}">
            <cp:areaValue uom="m2">{p_area}</cp:areaValue>
            <cp:beginLifespanVersion xsi:nil="true" nilReason="other:unpopulated"></cp:beginLifespanVersion>
            <cp:endLifespanVersion xsi:nil="true" nilReason="other:unpopulated"/>
            <cp:geometry>
                <gml:MultiSurface gml:id="MultiSurface_ES.LOCAL.CP.{p_label}" srsName="urn:ogc:def:crs:EPSG:{p_crs}"> 
                     {p_polygons}
                </gml:MultiSurface>
            </cp:geometry>
            <cp:inspireId>
                 <Identifier xmlns="http://inspire.ec.europa.eu/schemas/base/3.3">
                     <base:localId>{p_label}</base:localId>
                     <base:namespace>ES.LOCAL.CP.{p_label}</base:namespace>
                 </Identifier>
            </cp:inspireId>
            <cp:label>{p_label}</cp:label>
            <cp:nationalCadastralReference>{p_label}</cp:nationalCadastralReference>
            <cp:validFrom xsi:nil="true" nilReason="other:unpopulated"/>
            <cp:validTo xsi:nil="true" nilReason="other:unpopulated"/>
        </cp:CadastralParcel>
   </member>
</FeatureCollection>
""".format(**values)


def main(*args):
    layer = currentLayer()
    for feature in layer.features():
        gvsig2gmlcadastral(feature, pathresultados='/home/osc/temp/testing5/', p_label="Parcela", p_crs="EPSG:25830", p_unico=True)
