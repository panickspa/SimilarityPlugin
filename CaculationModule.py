from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import QIcon, QColor
from qgis.PyQt.QtWidgets import QAction

from qgis.core import (
    QgsProject, 
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
import time

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

    def getTranslate(self):
        return self.translate

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
    
        if (score >= treshold or self.method == 3) and score > 0:
            # print("saving score ...")
            self.similarLayer.append([feature.id(), feature2.id(), score])
            self.addScoreItem(feature.id(), feature2.id(), score)
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

        for i in layer.getFeatures():
            # Querying for matching attribute
            # print(self.killed)
            if self.killed is True:
                # kill request received, exit loop early
                break
            # print("iterated i : "+str(i.id()))
            # que = QgsQueryBuilder(layer2)
            # print("query builder" )
            # print("key cek")
            # print("PROVNO" in attrName)
            # print("provno" in attrName)
            # print("KABKOTNO" in attrName)
            # print("kabkotno" in attrName)
            # print("KECNO" in attrName)
            # print("kecno" in attrName)
            # print("DESANO" in attrName)
            # print("desano" in attrName)
            # print("PROVNO" in attrName2)
            # print("provno" in attrName2)
            # print("KABKOTNO" in attrName2)
            # print("kabkotno" in attrName2)
            # print("KECNO" in attrName2)
            # print("kecno" in attrName2)
            # print("DESANO" in attrName2)
            # print("desano" in attrName2)
            # print("key ceked")
            queText = ""
            try:
                # print("trying..")
                if("PROVNO" in attrName2):
                    # print("PROVNO passed")
                    queText += '"PROVNO"' + " LIKE '"
                    if("PROVNO" in attrName):
                        # print(("PROVNO" in attrName))
                        queText += i.attribute("PROVNO")
                    else:
                        # print("provno" in attrName)
                        queText += i.attribute("provno")
                elif("provno" in attrName2):
                    # print("provno" in attrName)
                    queText += '"provno"' + " LIKE '"
                    if("PROVNO" in attrName):
                        # print(("PROVNO" in attrName))
                        queText += i.attribute("PROVNO")
                    else:
                        # print("provno" in attrName)
                        queText += i.attribute("provno")
                else:
                    # show error message
                    self.error.emit("It might be not Wilkerstat, PROVNO, KABKOTNO, KECNO, and/or DESANO is required")
                    # print("error emit")
                    self.kill()
                    # print("kill task")

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
                elif("kabkotno" in attrName2):
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
                elif("kecno" in attrName2):
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
                elif("desano" in attrName2):
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
                    self.calcMapCurves(i,j)
                    # if self.translate:
                    #     score = self.calcMapCurvesGeom(
                    #             i.geometry(),
                    #             self.translateCenterGeom(i.geometry(), j.geometry())
                    #         )
                    #     # print("calculate geom score")
                    #     # if(score == -1):
                    #     #     self.validityError.emit("Feature with attribute "+ str(i.attributes())+" "+str(j.attributes())+" id "+str([i.id(), j.id()])+" is invalid")
                    #     #     # print("error emit")
                    #     self.progressSim.emit([i.id(),j.id(), score])
                    #     # print("append similar result")
                    #     self.addScoreItem(i.id(), j.id(), score)
                    #     # print("adding score")
                    # else:
                    #     score = self.calcMapCurvesGeom(
                    #         i.geometry(), j.geometry()
                    #     )
                    #     # print("calculate geom score")
                    #     # if(score == -1):
                    #     #     self.validityError.emit("Feature with attribute "+ str(j.attributes())+" "+str(i.attributes())+" id "+str([i.id(), j.id()])+" is invalid")
                    #     #     # print("error emit")
                    #     self.progressSim.emit([i.id(),j.id(), score])
                    #     # print("append similar result")
                    #     self.addScoreItem(i.id(), j.id(), score)
                    #     # print("adding score")
            except KeyError as identifier:
                # show error message
                self.error.emit("It might be not Wilkerstat, PROVNO, KABKOTNO, KECNO, DESANO is required")
                print("error emit")
                self.kill()
                # print("kill task")
            except ValueError as identifier:
                # show error message
                self.error.emit("Value error")
                print("error emit")
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

    def addScoreItem(self, idFeat:int, idFeat2:int, score:float):
        self.layerDup.commitChanges()
        self.layer2Dup.commitChanges()

        scoreFieldIndex = self.layerDup.dataProvider().fieldNameIndex(self.scoreName)
        scoreFieldIndex2 = self.layer2Dup.dataProvider().fieldNameIndex(self.scoreName)

        idIndex = self.layerDup.dataProvider().fieldNameIndex('id')
        idIndex2 = self.layer2Dup.dataProvider().fieldNameIndex('id')

        matchIndex = self.layerDup.dataProvider().fieldNameIndex('match')
        matchIndex2 = self.layer2Dup.dataProvider().fieldNameIndex('match')

        self.layerDup.startEditing()
        self.layer2Dup.startEditing()

        self.layerDup.changeAttributeValue(idFeat, scoreFieldIndex, score)
        self.layerDup.changeAttributeValue(idFeat, idIndex, idFeat)
        self.layerDup.changeAttributeValue(idFeat, matchIndex, idFeat2)
        self.layer2Dup.changeAttributeValue(idFeat2, scoreFieldIndex2, score)
        self.layer2Dup.changeAttributeValue(idFeat2, idIndex2, idFeat2)
        self.layer2Dup.changeAttributeValue(idFeat2, matchIndex2, idFeat)

        self.layerDup.commitChanges()
        self.layer2Dup.commitChanges()

    def addScoreItemLayer(self):
        self.layerDup.commitChanges()
        self.layer2Dup.commitChanges()

        scoreFieldIndex = self.layerDup.dataProvider().fieldNameIndex(self.scoreName)
        scoreFieldIndex2 = self.layer2Dup.dataProvider().fieldNameIndex(self.scoreName)

        idIndex = self.layerDup.dataProvider().fieldNameIndex('id')
        idIndex2 = self.layer2Dup.dataProvider().fieldNameIndex('id')

        matchIndex = self.layerDup.dataProvider().fieldNameIndex('match')
        matchIndex2 = self.layer2Dup.dataProvider().fieldNameIndex('match')

        self.layerDup.startEditing()
        self.layer2Dup.startEditing()

        for sim in self.similarLayer:
            self.layerDup.changeAttributeValue(sim[0], scoreFieldIndex, sim[2])
            self.layerDup.changeAttributeValue(sim[0], idIndex, sim[0])
            self.layerDup.changeAttributeValue(sim[0], matchIndex, sim[1])
            self.layer2Dup.changeAttributeValue(sim[1], scoreFieldIndex2, sim[2])
            self.layer2Dup.changeAttributeValue(sim[1], idIndex2, sim[1])
            self.layer2Dup.changeAttributeValue(sim[1], matchIndex2, sim[0])

        self.layerDup.commitChanges()
        self.layer2Dup.commitChanges()

    def run(self):
        start = time.perf_counter()
        if self.killed is False :
            self.similarLayer = []
            # print("duplicatingg")
            # print(self.layer)
            # print(self.layer2)
            # print("suffix :"+  self.suffix)
            # print("score name : "+ self.scoreName)
            try:
                self.eventTask.emit("Duplicating ....")
                self.layerDup = self.duplicateLayer(self.layer, self.suffix, self.scoreName)
                # print("duplicated 1")
                self.layer2Dup = self.duplicateLayer(self.layer2, self.suffix, self.scoreName)
                # print("duplicated 2")
                self.eventTask.emit("Calculating ....")
                if(self.method == 0):
                    print("sq method")
                    try:
                        self.calculateSq(self.layerDup, self.layer2Dup)
                        # print("similar checked")
                        self.eventTask.emit("adding Score to layer")
                        # self.addScoreItemLayer()
                        # print("score item addded")
                        self.finished.emit(self.similarLayer)
                        self.eventTask.emit("Finished !!")
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
                        print("is translated : "+str(self.translate))
                        # print("nn method")
                        self.calculateKNN(self.layerDup, self.layer2Dup, self.radius)
                        # print("similar checked")
                        self.eventTask.emit("Add score to layer")
                        # self.addScoreItemLayer()
                        # print("score item added")
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
                        # self.addScoreItemLayer()
                        # print("score item added")
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
            except:
                self.error.emit("Error when duplicating")
                # print(isinstance(self.layer, QgsVectorLayer))
                # print(isinstance(self.layer2, QgsVectorLayer))
        elapsed = time.perf_counter()
        elapsed = elapsed-start
        print("Elapsed time "+str(elapsed))

    def kill(self):
        self.killed = True

    def alive(self):
        self.killed = False

    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    progress = pyqtSignal(float)
    progressSim = pyqtSignal(list)
    eventTask = pyqtSignal(str)