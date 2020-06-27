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
    """
    Calculation Module for checking the similarity
    
    ..

    Attribute
    -----------
    killed = False
        Killed status object
    layer : QgsVectorLayer
        First original layer
    layerDup : QgsVectorLayer
        First duplicated layer
    layer2 : QgsVectorLayer
        Second original layer
    layer2Dup : QgsVectorLayer
        Second duplicated layer
    method : int
        Method selected
    radius : float
        Determined radius from user
    similarLayer : list=[]
        Similar result
    suffix: str
        Duplicated name suffix layer
    scoreName: str
        Duplicated scoreName attribute
    translate : bool
        Translate status
    treshold : float
        Treshold for calculation

    """
    killed = False
    layer : QgsVectorLayer
    layerDup : QgsVectorLayer
    layerResult : QgsVectorLayer
    layer2 : QgsVectorLayer
    layer2Dup : QgsVectorLayer
    layerResult2 : QgsVectorLayer
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
        """Set the treshold attribute.

        :param treshold float :Determined treshold from user

        """
        self.treshold = treshold
    
    def setLayers(self, layer:QgsVectorLayer, layer2:QgsVectorLayer):
        """Set the original layers.

        :param layer QgsVectorLayer: The first layer
        :param layer2 QgsVectorLayer: The second layer
        
        """
        self.layer = layer
        self.layer2 = layer2
    
    def setMethod(self, method:int):
        """Set the choosen method.

        :param method int: The index of choosen method (determined by user)
        
        """
        self.method = method
    
    def setTranslate(self, translate:bool):
        """Set translate status.

        :param translate bool: Translate status
        
        """
        self.translate = translate
    
    def setRadius(self, radius:float):
        """Set radius.

        :param radius float: Set the radius
        
        """
        self.radius = radius
    
    def setSuffix(self, suffix:str):
        """Set suffix name suffix cloned layer's.

        :param suffix str: Suffix value
        
        """
        self.suffix = suffix
    
    def setScoreName(self, scoreName:str):
        """Set score name attribute cloned layer's.

        :param scoreName str: Score name value

        """
        self.scoreName = scoreName

    def getSimilarLayer(self):
        """Get the similar layer"""
        return self.similarLayer

    def getLayers(self):
        """get the original layer"""
        return [self.layer, self.layer2]

    def getLayersDup(self):
        """get the duplicated layer"""
        return [self.layerDup, self.layer2Dup]

    def getLayersResult(self):
        """Get the results"""
        return [self.layerResult, self.layerResult2]

    def getSimilarLayer(self):
        """get list of the similar layer"""
        return self.similarLayer

    def getTranslate(self):
        """get translate status"""
        return self.translate

    def duplicateLayer(self, currentLayer:QgsVectorLayer, suffix:str, scoreName:str):
        """Duplicate original Layer.
        
        :param currentLayer QgsVectorLayer:The layer will be duplicated
        :param suffix str: Suffix name
        :param scoreName str: Attribute name of score in attribute table
        
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
            currentLayer.getFeatures()
        )
        # print(layer.featureCount())
        # print("features updated")
        return layer

    def duplicateEmptyLayer(self, currentLayer:QgsVectorLayer):
        layer = QgsVectorLayer("Polygon?crs=ESPG:4326",
                        currentLayer.name(),
                        'memory')
        # print("layer created")
        layer.setCrs(
            currentLayer.sourceCrs()
        )
        # print("crs set")
        layer.dataProvider().addAttributes(
            currentLayer.dataProvider().fields().toList()
        )

        layer.updateFields()

        return layer

    def translateCenterGeom(self, g, target):
        """Translate a geometry to the center another geometry
        
        :param g QgsGeometry: Geometry that be translated
        :param target QgsGeometry: The target geometry

        """
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
        """Calculating MapCurve using geometry.
        
        :param g QgsGeometry: First geometry for calculation
        :param g2 QgsGeometry: Second geometry for calculation

        """
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
        """Calculation MapCurve using feature.
        
        :param feature QgsFeature: The first feature
        :param feature2 QgsFeature: The second feature
        
        """

        treshold = self.treshold/100
        # print("treshold hold converted")
        score = 0
        # print("score initialized")
        if self.translate:
            # print("calculating with translate")
            score = self.calcMapCurvesGeom(
                        feature.geometry(),
                        self.translateCenterGeom(feature2.geometry(),feature.geometry()) 
                    )
            # print("calculated")
        else:
            # print("calculating without translate")
            score = self.calcMapCurvesGeom(feature.geometry(), feature2.geometry())
            # print("calculated")

        if (score >= treshold and score > 0) or self.method == 3:
            # print("saving score ...")
            self.similarLayer.append([feature.id(), feature2.id(), score])
            # self.addScoreItem(feature.id(), feature2.id(), score)
            self.addFeatureResult(feature, feature2, score)
            # print("feature added")
            # print("saved ...")
            self.progressSim.emit([feature.id(), feature2.id(), score])
            # print("result emited")

    def calculateWK(self, layer:QgsVectorLayer, layer2:QgsVectorLayer, translate=False):
        """MapCurve calculation using Wilkerstat method.
        
        :param layer QgsVectorLayer: The First layer
        :param layer2 QgsVevtorLayer: The Second Layer
        :param translate bool: calculate with translating the geometry
        
        """
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
        """MapCurve calculation using Squential method.
        
        :param layer QgsVectorLayer: The First layer
        :param layer2 QgsVevtorLayer: The Second Layer
        
        """
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
        """MapCurve calculation using Nearest Neighbour method.
        
        :param layer QgsVectorLayer: The First layer
        :param layer2 QgsVevtorLayer: The Second Layer
        
        """
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
        """Add the core item to layer cloned feature's

        :param idFeat int: the first id feature
        :param idFeat2 int: the second id feature
        :param score float: the similarity score

        """
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

    def addFeatureResult(self, feature:QgsFeature, feature2:QgsFeature, score:float):
        """Add result feature to result layer.
        
            :param feature QgsFeature: The feature will be added on first layer result
            :param feature QgsFeature: The feature will be added on second layer result
            :param score float: the feature score result

        """
        featDup = QgsFeature()
        featDup.setGeometry(feature.geometry())
        featDup.setFields(feature.fields())
        # print("set attribute")
        featDup.setAttributes(feature.attributes())
        featDup.setAttribute(feature.fields().indexOf(self.scoreName), score)
        # print("score 1 set")
        featDup.setAttribute(feature.fields().indexOf("id"), feature.id())
        # print("id 1 set")
        featDup.setAttribute(feature.fields().indexOf("match"), feature2.id())
        # print("match 1 set")
        
        featDup2 = QgsFeature()
        featDup2.setGeometry(feature2.geometry())
        featDup2.setFields(feature2.fields())
        featDup2.setAttributes(feature2.attributes())
        featDup2.setAttribute(feature2.fields().indexOf(self.scoreName), score)
        # print("score 2 set")
        featDup2.setAttribute(feature2.fields().indexOf('id'), feature2.id())
        # print("id 2 set")
        featDup2.setAttribute(feature2.fields().indexOf('match'), feature.id())
        # print("match 2 set")
        # print(featDup)
        # print(featDup.attributes())
        # print(featDup2)
        # print(featDup2.attributes())

        self.layerResult.dataProvider().addFeature(featDup)
        # print(self.layerResult.dataProvider().addFeature(featDup))
        self.layerResult2.dataProvider().addFeature(featDup2)
        # print(self.layerResult2.dataProvider().addFeature(featDup2))
        # print("duplicated")

    def run(self):
        """Run the object"""
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
                self.layerResult = self.duplicateEmptyLayer(self.layerDup)
                # print("duplicate layer result")
                self.layer2Dup = self.duplicateLayer(self.layer2, self.suffix, self.scoreName)
                # print("duplicated 2")
                self.layerResult2 = self.duplicateEmptyLayer(self.layer2Dup)
                # print("duplicate layer result2")
                # print("duplicated 2")
                self.eventTask.emit("Calculating ....")
                if(self.method == 0):
                    # print("sq method")
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
                        self.eventTask.emit("Eror Occured")
                        # print("error emitted")
                    except:
                        # print("error")
                        self.error.emit("Not executed")
                        self.eventTask.emit("Eror Occured")  
                        # print("error emitted")     
                elif (self.method == 1):
                    try:
                        # print("is translated : "+str(self.translate))
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
                        self.eventTask.emit("Eror Occured")
                        # print("error emitted")   
                    except:
                        # print("error")
                        self.error.emit("Not executed")
                        self.eventTask.emit("Eror Occured")
                        # print("error emitted") 
                elif (self.method == 2):
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
                        self.eventTask.emit("Eror Occured")
                        # print("error emitted") 
                    except:
                        # print("error")
                        self.error.emit("Not executed")
                        self.eventTask.emit("Eror Occured")
                        # print("error emitted") 
                        # print(similar)
                else:
                    print("saving")
                    self.eventTask.emit("Saving ....")
                    self.registerToProject()
                    self.eventTask.emit("Layer saved")
            except:
                self.error.emit("Error when duplicating")
                self.eventTask.emit("Eror Occured")
                # print(isinstance(self.layer, QgsVectorLayer))
                # print(isinstance(self.layer2, QgsVectorLayer))
        elapsed = time.perf_counter()
        elapsed = elapsed-start
        # print(self.layerResult.featureCount())
        # print(self.layerResult2.featureCount())
        print("Elapsed time "+str(elapsed))
        # print(self.similarLayer)

    def kill(self):
        """Set the killed status"""
        self.killed = True

    def alive(self):
        """Set the not to be killed"""
        self.killed = False

    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    progress = pyqtSignal(float)
    progressSim = pyqtSignal(list)
    eventTask = pyqtSignal(str)