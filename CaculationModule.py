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
        target_new = QgsGeometry(target)
        
        c = target_new.centroid().asQPointF()
        c2 = g_new.centroid().asQPointF()
        transX = c.x() - c2.x()
        transY = c.y() - c2.y()
        g.translate(transX, transY)
        return g

    def calcMapCurvesGeom(self, g:QgsGeometry, g2:QgsGeometry):
        
        inter = g.intersection(g2)
        if(inter.isEmpty()):
            return 0
        else:
            score = (inter.area()/g.area())*(inter.area()/g2.area())
            return round(score, 4)
 
    def calcMapCurves(self, feature:QgsFeature, feature2:QgsFeature):
        
        treshold = self.treshold/100

        if self.method == 1:
            score = self.calcMapCurvesGeom(
                        feature.geometry(),
                        self.translateCenterGeom(feature2.geometry(),feature.geometry()) 
                    )
        else:
            score = self.calcMapCurvesGeom(feature.geometry(), feature2.geometry())

        if score >= treshold and treshold > 0:
            self.similarLayer.append([feature.id(), feature2.id(), score])
            self.progressSim.emit([feature.id(), feature2.id(), score])

    def calculateWK(self, layer:QgsVectorLayer, layer2:QgsVectorLayer, translate=False):
        # print("executed function wk")
        progress = 0

        attrName = layer.dataProvider().fields().names()
        attrName2 = layer2.dataProvider().fields().names()
        
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
                    # print("passed")
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
                    queText += "'"+' AND "KABKOTNO" ' + " LIKE '"
                    if ("KABKOTNO" in attrName):
                        queText += i.attribute("KABKOTNO")
                    else:
                        queText += i.attribute("kabkotno")
                else:
                    queText += "'"+' AND "kabkotno" ' + " LIKE '"
                    if ("KABKOTNO" in attrName):
                        queText += i.attribute("KABKOTNO")
                    else:
                        queText += i.attribute("kabkotno")
                
                if ("KECNO" in attrName2):
                    queText += "'"+' AND "KECNO" ' + "LIKE '"
                    if ("KECNO" in attrName):
                        queText += i.attribute("KECNO")
                    else:
                        queText += i.attribute("kecno")
                else:
                    queText += "'"+' AND "kecno" ' + "LIKE '"
                    if ("KECNO" in attrName):
                        queText += i.attribute("KECNO")
                    else:
                        queText += i.attribute("kecno")
                
                if ('DESANO' in attrName2):
                    queText += "'"+' AND "DESANO" ' + "LIKE '"
                    if('DESANO' in attrName):
                        queText += i.attribute("DESANO")+"' "
                    else:
                        queText += i.attribute("desano")+"' "
                else:
                    queText += "'"+' AND "desano" ' + "LIKE '"
                    if('DESANO' in attrName):
                        queText += i.attribute("DESANO")+"' "
                    else:
                        queText += i.attribute("desano")
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
                        self.progressSim.emit([i.id(),j.id(), score])
                        # print("append similar result")
                    else:
                        score = self.calcMapCurvesGeom(
                            i.geometry(), j.geometry()
                        )
                    # print("calculate geom score")
                    self.progressSim.emit([i.id(),j.id(), score])
            except KeyError as identifier:
                # show error message
                self.error.emit("It might be not Wilkerstat, PROVNO, KABKOTNO, KECNO, DESANO is required")
            except ValueError as identifier:
                # show error message
                self.error.emit("Value error")
            except:
                self.error.emit("unexpected error")
            progress = progress+((1/layer.featureCount())*100)
            # iterL = iterL+1
            # print(iterL)
            # print("progress "+str(progress))
            self.progress.emit(progress)
        return self.similarLayer

    def calculateSq(self, layer:QgsVectorLayer, layer2:QgsVectorLayer):
        # print("executed function sq")
        progress = 0
        for i in layer.getFeatures():
            if self.killed is True:
                # kill request received, exit loop early
                break
            for j in layer2.getFeatures(i.geometry().boundingBox()):
                if(i.hasGeometry()):
                    self.calcMapCurves(i, j)
            progress = progress+(1/layer.featureCount()*100)
            self.progress.emit(progress)

        return self.similarLayer

    def calculateKNN(self, layer:QgsVectorLayer, layer2:QgsVectorLayer, radius:float):
        # print("executed function nn")
        progress = 0
        for i in layer.getFeatures() :
            if self.killed is True:
                # kill request received, exit loop early
                break
            if(i.hasGeometry()):
                centroid = i.geometry().centroid().asQPointF()
                bbFilter = QgsRectangle(
                    centroid.x()-radius,
                    centroid.y()-radius,
                    centroid.x()+radius,
                    centroid.y()+radius
                )
                for j in layer2.getFeatures(bbFilter):
                    self.calcMapCurves(i, j)
            progress = progress+(1/layer.featureCount()*100)
            self.progress.emit(progress)

        return self.similarLayer

    def run(self):
        start = timer()
        if self.killed is False :
            self.similarLayer = []
            # print("duplicatingg")
            # print(self.layer)
            # print(self.layer2)
            # print("suffix :"+  self.suffix)
            # print("score name : "+ self.scoreName)
            self.layerDup = self.duplicateLayer(self.layer, self.suffix, self.scoreName)
            # print("duplicated 1")
            self.layer2Dup = self.duplicateLayer(self.layer2, self.suffix, self.scoreName)
            # print("duplicated 2")
            # print(isinstance(self.layer, QgsVectorLayer))
            # print(isinstance(self.layer2, QgsVectorLayer))
            if(self.method == 0):
                try:
                    self.calculateSq(self.layerDup, self.layer2Dup)
                    self.finished.emit(self.similarLayer)
                    # print(self.similarLayer)
                except NameError as ex:
                    self.error.emit("Not executed")
                except:
                    # print("error")
                    self.error.emit("Not executed")        
            elif (self.method == 1):
                try:
                    # print("nn method")
                    similar = self.calculateKNN(self.layerDup, self.layer2Dup, self.radius)
                    self.finished.emit(similar)
                except NameError as ex:
                    self.error.emit("Not executed")
                except:
                    # print("error")
                    self.error.emit("Not executed")  
                # print(similar)
            else:
                # print("wk method")
                try:
                    similar = self.calculateWK(self.layerDup, self.layer2Dup)
                    self.finished.emit(similar)
                except NameError as ex:
                    self.error.emit(str(ex))
                except:
                    # print("error")
                    self.error.emit("Not executed")
                
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
    progressSim = pyqtSignal(list)