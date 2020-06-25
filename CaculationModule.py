from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import QIcon, QColor
from qgis.PyQt.QtWidgets import QAction

from qgis.core import (QgsProject, 
    QgsVectorLayer, 
    QgsGeometry, 
    QgsFeature, 
    QgsField, 
    QgsRectangle,
    QgsTaskManager,
    QgsTask,
    QgsMessageLog,
    Qgis
)

from qgis.gui import QgsQueryBuilder
import datetime
from timeit import default_timer as timer

class CalculationModule(QObject):
    killed = False
    layer : QgsVectorLayer
    layerDup : QgsVectorLayer
    layer2 : QgsVectorLayer
    layer2Dup : QgsVectorLayer
    method : int
    radius : float
    similarLayer = []
    suffix: str
    scoreName: str
    translate : bool
    treshold : float
    
    def __init__(self):
        super().__init__()

    # Set option for calculating
    def setTreshold(self, treshold:float):
        self.treshold = treshold
    def setLayers(self, layer:QgsVectorLayer, layer2:QgsVectorLayer):
        self.layer = layer
        self.layer2 = layer2
    def setMethod(self, method:int):
        self.method = method
    def setTranslate(self, translate:bool):
        self.translate = translate
    def setRadius(self, radius:float):
        self.radius = radius
    def setSuffix(self, suffix:str):
        self.suffix = suffix
    def setScoreName(self, scoreName:str):
        self.scoreName = scoreName

    # get similar layer
    def getSimilarLayer(self):
        return self.similarLayer

    def getLayers(self):
        return [self.layer, self.layer2]

    def getLayersDup(self):
        return [self.layerDup, self.layer2Dup]

    def getSimilarLayer(self):
        return self.similarLayer

    def setLayer(self, layer:QgsVectorLayer, layer2:QgsVectorLayer):
        self.layer = layer
        self.layer2 = layer2

    def duplicateLayer(self, currentLayer:QgsVectorLayer, suffix:str, scoreName:str):
        """
            :params: currentLayer
                The layer will be duplicated
            :params: suffix str
                Suffix name
            :params: scoreName
                Attribute name of score in attribute table
        """
        # print(currentLayer)
        # print(suffix)
        # print(scoreName)
        layername = str(currentLayer.name())+"_"+str(suffix)
        layer = QgsVectorLayer("Polygon?crs=ESPG:4326",
                        layername,
                        'memory')
        # print("layer created")
        layer.setCrs(
            currentLayer.sourceCrs()
        )
        # print("crs set")
        layer.dataProvider().addAttributes(
            currentLayer.dataProvider().fields().toList()
        )
        # print("add field")
        # adding score attributes info
        layer.dataProvider().addAttributes(
            [
                QgsField(scoreName, QVariant.Double),
                QgsField('id', QVariant.Int),
                QgsField('match', QVariant.Int)
            ]
        )
        # print("field updated")
        # update the fields
        layer.updateFields()
        # print("updated fields")
        layer.dataProvider().addFeatures(
            [f for f in currentLayer.getFeatures()]
        )
        # print("features updated")
        return layer

    def translateCenterGeom(self, g, target):
        
        # duplicating
        g_new = QgsGeometry(g)
        # print("g duplicated")
        target_new = QgsGeometry(target)
        # print("target duplicated")

        c = target_new.centroid().asQPointF()
        # print("centroid created")
        c2 = g_new.centroid().asQPointF()
        # print("centroid created")
        transX = c.x() - c2.x()
        # print("translate x calculated")
        transY = c.y() - c2.y()
        # print("translate y calculated")
        g.translate(transX, transY)
        # print("g translated")
        return g

    def calcMapCurvesGeom(self, g:QgsGeometry, g2:QgsGeometry):
        
        
        if(not g.isGeosValid()):
            # print("not valid geom")
            g = QgsGeometry(g.makeValid())
        if(not g2.isGeosValid()):
            # print("not valid geom2")
            g2 = QgsGeometry(g2.makeValid())

        # print(g.makeValid())
        # print(g2.makeValid())
        inter = g.intersection(g2)
        # print("intersection created")
        if(inter.isEmpty()):
            # print("empty geom")
            return 0
        else:
            # print("calculating score")
            score = (inter.area()/g.area())*(inter.area()/g2.area())
            # print("score calculated")
            return round(score, 4)
 
    def calcMapCurves(self, feature:QgsFeature, feature2:QgsFeature):
        
        treshold = self.treshold/100
        # print("treshold hold converted")
        score = 0
        # print("score initialized")
        if self.method == 1:
            # print("calculating")
            score = self.calcMapCurvesGeom(
                        feature.geometry(),
                        self.translateCenterGeom(feature2.geometry(),feature.geometry()) 
                    )
            # print("calculated")
        else:
            # print("calculating")
            score = self.calcMapCurvesGeom(feature.geometry(), feature2.geometry())
            # print("calculated")
        # if(score == -1):
        #     # print("not valid geom")
        #     self.validityError.emit("Feature with attribute "+ str(feature.attributes())+" "+str(feature2.attributes())+" id "+str([feature.id(), feature2.id()])+" is invalid")

        if score >= treshold and score > 0:
            # print("saving score ...")
            self.similarLayer.append([feature.id(), feature2.id(), score])
            # print("saved ...")
            self.progressSim.emit([feature.id(), feature2.id(), score])
            # print("result emited")

    def calculateWK(self, layer:QgsVectorLayer, layer2:QgsVectorLayer, translate=False):
        # print("executed function wk")
        progress = 0
        # print("progress initialized") 
        attrName = layer.dataProvider().fields().names()
        # print("attrnName initialized")
        attrName2 = layer2.dataProvider().fields().names()
        # print("attrnName initialized")

        # pkCheck = self.wilkerstatPKExist(layer, layer2)
        iterL = 0
        for i in layer.getFeatures():
            # Querying for matching attribute
            # print(self.killed)
            if self.killed is True:
                # kill request received, exit loop early
                break
            # print("iterated i : "+str(i.id()))
            que = QgsQueryBuilder(layer2)
            # print("query builder" )

            queText = ""
            try:
                # print("trying..")
                # print("PROVNO" in attrName2)
                # print("provno" in attrName2)
                if("PROVNO" in attrName2):
                    # print("provno passed")
                    queText += '"PROVNO"' + " LIKE '"
                    if("PROVNO" in attrName):
                        # print(("PROVNO" in attrName))
                        queText += i.attribute("PROVNO")
                    else:
                        # print("provno" in attrName)
                        queText += i.attribute("provno")
                else:
                    # print("provno" in attrName)
                    queText += '"provno"' + " LIKE '"
                    if("PROVNO" in attrName):
                        # print(("PROVNO" in attrName))
                        queText += i.attribute("PROVNO")
                    else:
                        # print("provno" in attrName)
                        queText += i.attribute("provno")
                
                if ("KABKOTNO" in attrName2):
                    # print("kabkotno checked")
                    queText += "'"+' AND "KABKOTNO" ' + " LIKE '"
                    # print("query str build "+"'"+' AND "KABKOTNO" ' + " LIKE '")
                    if ("KABKOTNO" in attrName):
                        queText += i.attribute("KABKOTNO")
                        # print("query str build add KABKOTNO")
                    else:
                        queText += i.attribute("kabkotno")
                        # print("query str build kabkotno")
                else:
                    # print("kabkotno checked")
                    queText += "'"+' AND "kabkotno" ' + " LIKE '"
                    # print("query str build "+"'"+' AND "kabkotno" ' + " LIKE '")
                    if ("KABKOTNO" in attrName):
                        queText += i.attribute("KABKOTNO")
                        # print("query str build add KABKOTNO")
                    else:
                        queText += i.attribute("kabkotno")
                        # print("query str build kabkotno")
                
                if ("KECNO" in attrName2):
                    # print("KECNO cheked")
                    queText += "'"+' AND "KECNO" ' + "LIKE '"
                    # print("query str build "+"'"+' AND "KECNO" ' + "LIKE '")
                    if ("KECNO" in attrName):
                        queText += i.attribute("KECNO")
                        # print("query str build add KECNO")
                    else:
                        queText += i.attribute("kecno")
                        # print("query str build add kecno")
                else:
                    # print("kecno cheked")
                    queText += "'"+' AND "kecno" ' + "LIKE '"
                    # print("query str build "+"'"+' AND "kecno" ' + "LIKE '")
                    if ("KECNO" in attrName):
                        queText += i.attribute("KECNO")
                        # print("query str build add KECNO")
                    else:
                        queText += i.attribute("kecno")
                        # print("query str build add kecno")
                
                if ('DESANO' in attrName2):
                    # print("DESANO cheked")
                    queText += "'"+' AND "DESANO" ' + "LIKE '"
                    # print("query str build "+"'"+' AND "DESANO" ' + "LIKE '")
                    if('DESANO' in attrName):
                        queText += i.attribute("DESANO")+"' "
                        # print("query add DESANO")
                    else:
                        queText += i.attribute("desano")+"' "
                        # print("query add desano")
                else:
                    # print("desano cheked")
                    queText += "'"+' AND "desano" ' + "LIKE '"
                    # print("query build "+"'"+' AND "desano" ' + "LIKE '")
                    if('DESANO' in attrName):
                        queText += i.attribute("DESANO")+"' "
                        # print("query add DESANO")
                    else:
                        queText += i.attribute("desano")
                        # print("query add desano")
                # print("id checked")
                queText += "' "
                # print(queText)
                # print(len([j for j in layer2.getFeatures(queText)]))
                for j in layer2.getFeatures(queText):
                    if self.translate:
                        score = self.calcMapCurvesGeom(
                                i.geometry(),
                                self.translateCenterGeom(i.geometry(), j.geometry())
                            )
                        # print("calculate geom score")
                        # if(score == -1):
                        #     self.validityError.emit("Feature with attribute "+ str(i.attributes())+" "+str(j.attributes())+" id "+str([i.id(), j.id()])+" is invalid")
                        #     # print("error emit")
                        self.progressSim.emit([i.id(),j.id(), score])
                        # print("append similar result")
                    else:
                        score = self.calcMapCurvesGeom(
                            i.geometry(), j.geometry()
                        )
                        # print("calculate geom score")
                        # if(score == -1):
                        #     self.validityError.emit("Feature with attribute "+ str(j.attributes())+" "+str(i.attributes())+" id "+str([i.id(), j.id()])+" is invalid")
                        #     # print("error emit")
                        self.progressSim.emit([i.id(),j.id(), score])
                        # print("append similar result")
            except KeyError as identifier:
                # show error message
                self.error.emit("It might be not Wilkerstat, PROVNO, KABKOTNO, KECNO, DESANO is required")
                # print("error emit")
                self.kill()
                # print("kill task")
            except ValueError as identifier:
                # show error message
                self.error.emit("Value error")
                # print("error emit")
                self.kill()
                # print("kill task")
            except:
                self.error.emit("Unexpected error")
                # print("error emit")
                self.kill()
                # print("kill task")
            progress = progress+((1/layer.featureCount())*100)
            # print("progress calculated")
            # iterL = iterL+1
            # print(iterL)
            # print("progress "+str(progress))
            self.progress.emit(progress)
            # print("progress emitted")
        return self.similarLayer

    def calculateSq(self, layer:QgsVectorLayer, layer2:QgsVectorLayer):
        # print("executed function sq")
        progress = 0
        # print("progress initialized")
        for i in layer.getFeatures():
            # print(i)
            # print(i.id())
            # print("Iteration i")
            if self.killed is True:
                # kill request received, exit loop early
                # print("killed")
                # print("task killed")
                break
            for j in layer2.getFeatures(i.geometry().boundingBox()):
                # print(j)
                # print(j.id())
                # print("Iteration j")
                if(i.hasGeometry()):
                    # print("Checking")
                    self.calcMapCurves(i, j)
                    # print("checked")
            progress = progress+(1/layer.featureCount()*100)
            # print("progress add")
            self.progress.emit(progress)
            # print("progress emitted")

        return self.similarLayer

    def calculateKNN(self, layer:QgsVectorLayer, layer2:QgsVectorLayer, radius:float):
        # print("executed function nn")
        progress = 0
        # print("progress initialzed")
        for i in layer.getFeatures() :
            # print(i)
            # print(i.id())
            # print("Iteration i")
            if self.killed is True:
                # kill request received, exit loop early
                # print("killed")
                break
            if(i.hasGeometry()):
                # print("has geometry")
                centroid = i.geometry().centroid().asQPointF()
                # print("centroid created")
                bbFilter = QgsRectangle(
                    centroid.x()-radius,
                    centroid.y()-radius,
                    centroid.x()+radius,
                    centroid.y()+radius
                )
                # print("bounding box created")
                for j in layer2.getFeatures(bbFilter):
                    # print(j)
                    # print(j.id())
                    # print("Iteration j")
                    self.calcMapCurves(i, j)
                    # print("calculated")
            progress = progress+(1/layer.featureCount()*100)
            # print("progress added")
            self.progress.emit(progress)
            # print("progress emitted")

        return self.similarLayer

    def run(self):
        start = timer()
        print(self.killed)
        if self.killed is False :
            self.similarLayer = []
            # print("duplicatingg")
            # print(self.layer)
            # print(self.layer2)
            # print("suffix :"+  self.suffix)
            # print("score name : "+ self.scoreName)
            try:
                self.layerDup = self.duplicateLayer(self.layer, self.suffix, self.scoreName)
                # print("duplicated 1")
                self.layer2Dup = self.duplicateLayer(self.layer2, self.suffix, self.scoreName)
                # print("duplicated 2")
            except:
                self.error.emit("error when duplicating")
                # print(isinstance(self.layer, QgsVectorLayer))
                # print(isinstance(self.layer2, QgsVectorLayer))
            if(self.method == 0):
                print("sq method")
                try:
                    self.calculateSq(self.layerDup, self.layer2Dup)
                    # print("similar checked")
                    self.finished.emit(self.similarLayer)
                    # print(self.similarLayer)
                except NameError as ex:
                    # print("error")
                    self.error.emit("Not executed")
                    # print("error emitted")
                except:
                    # print("error")
                    self.error.emit("Not executed")   
                    # print("error emitted")     
            elif (self.method == 1):
                try:
                    # print("nn method")
                    self.calculateKNN(self.layerDup, self.layer2Dup, self.radius)
                    # print("similar checked")
                    self.finished.emit(self.similarLayer)
                    # print("finished emitted")   
                except NameError as ex:
                    self.error.emit("Not executed")
                    # print("error emitted")   
                except:
                    # print("error")
                    self.error.emit("Not executed")
                    # print("error emitted") 
            else:
                print("wk method")
                try:
                    self.calculateWK(self.layerDup, self.layer2Dup)
                    # print("similar checked")
                    self.finished.emit(self.similarLayer)
                    # print("finished emitted") 
                except NameError as ex:
                    self.error.emit(str(ex))
                    # print("error emitted") 
                except:
                    # print("error")
                    self.error.emit("Not executed")
                    # print("error emitted") 
                    # print(similar)
        elapsed = timer()-start
        print("Elapsed time "+str(elapsed))

    def kill(self):
        self.killed = True

    def alive(self):
        self.killed = False

    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    progress = pyqtSignal(float)
    # validityError = pyqtSignal(str)
    progressSim = pyqtSignal(list)