import sys
from gvsig import geom
from gvsig import commonsdialog
from gvsig import getTempFile
import os.path
from gvsig import *
from org.gvsig.andami import Utilities

def reProjectBetweenCRS(point, crs_in, crs_out):
    print "projection.. ", crs_in, crs_out
    v1 = getCRS(crs_in)
    v2 = getCRS(crs_out)
    print v1, v2
    ICoordTrans1 = v1.getCT(v2)
    point.reProject(ICoordTrans1)
    return point
    
def crea_gvsig2gml(featureStore, pathresultados='', p_label="Parcela", p_crs="EPSG:25830", p_unico=True):
    """ Convierte una entidad en un gml """
    print "====== CONVERSOR A GML "
        
    sch = createSchema()
    sch.append("GEOMETRY", "GEOMETRY")
    sch.get("GEOMETRY").setGeometryType(geom.POLYGON, geom.D2)



    #for f in featureStore.features():
    selection = currentLayer().getSelection()
    print "selection count: ", selection.getCount()
    if selection.getCount() == 0 or selection.getCount() > 1:
        commonsdialog.msgbox("None feature selected or more than one feature", "Error", 1)
        return
        
    for f in selection:
        print  "featureStore:feature"
        feature = f #.getCopy()
        
    #p_label = str(commonsdialog.inputbox("Parcela", "Nombre de la parcela"))
    if p_label=="":
        schvalues = currentLayer().getSchema().getAttrNames()
        print schvalues
        if "RefCat" in schvalues:
            p_label = feature.RefCat
        elif "nationalCadastralReference" in schvalues:
            p_label = feature.nationalCadastralReference
        elif "localId" in schvalues:
            p_label = feature.localId
        else:
            p_label = commonsdialog.inputbox("No se ha encontrado campo localId. Introducir manualmente (en blanco se asgina valor 'Parcela'): ")
            if p_label=='':
                p_label = "Parcela"
            

    # Path gml file
    if pathresultados=='':
        pathresultados = Utilities.TEMPDIRECTORYPATH
        if not os.path.isdir(pathresultados):
            os.makedirs(pathresultados)
            
    if p_unico==True:
        tempgml = getTempFile(p_label,".gml", pathresultados)
    elif p_unico==False:
        tempgml = os.path.join(pathresultados, p_label+".gml")
    print tempgml
        
    print "==== PARCELA"
    with open(tempgml, 'w') as filegml:
        #filegml.writelines(PLANTILLA_1)
        
        fgeometry = feature.geometry()
        polygon = fgeometry
        p_polygons = ""
        ### Crear coordenadas del poligono
        #if polygon.getGeometryType().getName() == "MultiPolygon2D":
        #    for i in polygon:
        #        print i, " in ", polygon
        #        p_polygons += plantilla_interior("exterior", listarCoordenadas(i), i.getNumVertices())
        #else:
            

        crs_view = currentLayer().getProjectionCode()#.split(":")[1]
        crs_gml = p_crs
        if crs_view != crs_gml:
            print "Reprojectar: ", crs_view, " a ", crs_gml
            polygon = reProjectBetweenCRS(polygon, crs_view, crs_gml)


        p_polygons += plantilla_interior("exterior", listarCoordenadas(polygon), polygon.getNumVertices())
        
        p_area = polygon.area()
        print('El area del poligono es %.4f m2.' % (p_area))
        ### Crear coordenadas del los anillos
        numrings = polygon.getNumInteriorRings()
        if numrings >= 1:
            for nr in range(numrings):
                ring = polygon.getInteriorRing(nr)
                p_polygons += plantilla_interior("interior",listarCoordenadas(ring), ring.getNumVertices())

        filegml.write(plantilla(p_area, p_polygons, p_label, p_crs.split(":")[1]))
        
    filegml.close()

    return tempgml
    
def listarCoordenadas(geometria):
    """ Devuelve string con el listado de coordenadas """
    vertices = geometria.getNumVertices()
    print('Total de vertices del poligono: %s' % (vertices))
    p_coord = ""
    for i in range(0, vertices):
        pt = geometria.getVertex(i)
        p_coord += "" + str(pt.getX()) + " " + str(pt.getY()) + "\n"
    return p_coord 
  
def plantilla_interior(p_tipo, p_coord, p_count):
  strcoord = """<gml:%s>
<gml:LinearRing>
<gml:posList srsDimension="2" count="%s">%s</gml:posList>
</gml:LinearRing>
</gml:%s>
""" % (p_tipo, p_count, p_coord, p_tipo)
  return strcoord

def plantilla(p_area, p_polygons, p_label, p_crs):
    values = {"p_area":p_area, "p_polygons":p_polygons, "p_label":p_label, "p_crs":p_crs}
    return """<?xml version="1.0" encoding="utf-8"?>
<gml:FeatureCollection xmlns:gml="http://www.opengis.net/gml/3.2" xmlns:gmd="http://www.isotc211.org/2005/gmd" xmlns:ogc="http://www.opengis.net/ogc" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:cp="urn:x-inspire:specification:gmlas:CadastralParcels:3.0" xmlns:base="urn:x-inspire:specification:gmlas:BaseTypes:3.2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="urn:x-inspire:specification:gmlas:CadastralParcels:3.0 http://inspire.ec.europa.eu/schemas/cp/3.0/CadastralParcels.xsd" gml:id="ES.LOCAL.CP">
   <gml:featureMember>
      <cp:CadastralParcel gml:id="ES.LOCAL.CP.{p_label}">
         <cp:areaValue uom="m2">{p_area}</cp:areaValue>
         <cp:beginLifespanVersion xsi:nil="true" nilReason="other:unpopulated"></cp:beginLifespanVersion>
         <cp:geometry>
           <gml:MultiSurface gml:id="MultiSurface_ES.LOCAL.CP.{p_label}" srsName="urn:ogc:def:crs:EPSG::{p_crs}"> 
             <gml:surfaceMember>
               <gml:Surface gml:id="Surface_ES.LOCAL.CP.{p_label}" srsName="urn:ogc:def:crs:EPSG::{p_crs}">
                  <gml:patches>
                    <gml:PolygonPatch>
{p_polygons}
                    </gml:PolygonPatch>
                  </gml:patches>
                </gml:Surface>
              </gml:surfaceMember>
            </gml:MultiSurface>
         </cp:geometry>
            <cp:inspireId xmlns:base="urn:x-inspire:specification:gmlas:BaseTypes:3.2">
            <base:Identifier>
            <base:localId>{p_label}</base:localId>
            <base:namespace>ES.LOCAL.CP.{p_label}</base:namespace>
            </base:Identifier>
            </cp:inspireId>
      <cp:label>{p_label}</cp:label>
      <cp:nationalCadastralReference>{p_label}</cp:nationalCadastralReference>
      </cp:CadastralParcel>
   </gml:featureMember>
</gml:FeatureCollection>
""".format(**values)


def main(*args):
    crea_gvsig2gml(currentLayer().getFeatureStore(), pathresultados='/home/osc/temp/testing3/', p_label="Parcela", p_crs="EPSG:25830", p_unico=True)
