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

class CalculationModule(QObject):
    def __init__(
        self,
        layer:QgsVectorLayer,
        layer2:QgsVectorLayer,
        treshold:float, 
        method=0,
        translate=False
        ):
        
        super().__init__()
        self.similarLayer = []
        self.treshold = treshold
        self.layer = layer
        self.layer2 = layer2
        self.method = method
        self.translate = translate

    def getLayer(self):
        return [self.layer, self.layer2]

    def getSimilarLayer(self):
        return self.similarLayer

    def setLayer(self, layer:QgsVectorLayer, layer2:QgsVectorLayer):
        self.layer = layer
        self.layer2 = layer2

    def switchLayer(self):
        layer = QgsVectorLayer(self.layer)
        self.layer = self.layer2
        self.layer2 = layer

    def getMethod(self):
        return self.method

    def setMethod(self, method:int):
        self.method = method

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
        
        treshold = treshold/100

        if self.method == 1:
            score = self.calcMapCurvesGeom(
                        feature.geometry(),
                        self.translateCenterGeom(feature2.geometry(),feature.geometry()) 
                    )
        else:
            score = self.calcMapCurvesGeom(feature.geometry(), feature2.geometry())

        if score >= treshold:
            self.similarLayer.append([feature.id(), feature2.id(), score])

    def calculateWK(self, layer:QgsVectorLayer, layer2:QgsVectorLayer, translate=False):
        
        for i in layer.getFeatures():
            # Querying 
            que = QgsQueryBuilder(layer2)
            queText = ""
            queText += '"PROVNO"' + " LIKE '"
            queText += i.attribute("PROVNO")
            queText += "'"+' AND "KABKOTNO" ' + " LIKE '"
            queText += i.attribute("KABKOTNO")
            queText += "'"+' AND "KECNO" ' + "LIKE '"
            queText += i.attribute("KECNO")
            queText += "'"+' AND "DESANO" ' + "LIKE '"
            queText += i.attribute("DESANO")+"' "
            que.clear()
            que.setSql(queText)
            que.accept()
            if layer2.featureCount() > 0:
                if self.translate:
                    for j in layer2.getFeatures():
                        score = self.calcMapCurvesGeom(
                            i.geometry(),
                            self.translateCenterGeom(i.geometry(), j.geometry())
                        )
                        self.similarLayer.append([i.id(),j.id(), score])
                else:
                    for j in layer2.getFeatures(): 
                        score = self.calcMapCurvesGeom(
                            i.geometry(), j.geometry()
                        )
                        if(score > -1):
                            self.similarLayer.append([i.id(),j.id(), score])
            que.clear()
            que.accept()

        return self.similarLayer

    def calculateSq(self, layer:QgsVectorLayer, layer2:QgsVectorLayer):
        
        for i in layer.getFeatures():
            for j in layer2.getFeatures(i.geometry().boundingBox()):
                if(i.hasGeometry()):
                    self.calcMapCurves(i, j)

        return self.similarLayer

    def calculateKNN(self, layer:QgsVectorLayer, layer2:QgsVectorLayer, radius:float):
        
        for i in layer.getFeatures() :
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

        return self.similarLayer

class TaskCalculate(QgsTask):
    def __init__(self,
        layer:QgsVectorLayer,
        layer2:QgsVectorLayer,
        treshold:float, 
        method=0,
        mergeCenter=False
    ):
        super().__init__('Calculation Task', QgsTask.CanCancel)
        self.similarLayer = []
        self.layer = layer
        self.layer2 = layer2
        self.treshold = treshold
        self.method = method
        self.mergeCenter = mergeCenter
    
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
        
        treshold = treshold/100

        if self.method == 1:
            score = self.calcMapCurvesGeom(
                        feature.geometry(),
                        self.translateCenterGeom(feature2.geometry(),feature.geometry()) 
                    )
        else:
            score = self.calcMapCurvesGeom(feature.geometry(), feature2.geometry())

        if score >= treshold:
            self.similarLayer.append([feature.id(), feature2.id(), score])

    def calculateWK(self, layer:QgsVectorLayer, layer2:QgsVectorLayer, translate=False):
        progress = 0
        
        attrName = layer.dataProvider().fields().names()
        attrName2 = layer2.dataProvider().fields().names()
        
        # pkCheck = self.wilkerstatPKExist(layer, layer2)

        for i in layer.getFeatures():
            # Querying for matching attribute 
            
            que = QgsQueryBuilder(layer2)
            
            queText = ""
            try:
                if("PROVNO" in attrName2):
                    queText += '"PROVNO"' + " LIKE '"
                    if("PROVNO" in attrName):
                        queText += i.attribute("PROVNO")
                    else:
                        queText += i.attribute("provno")
                else:
                    queText += '"provno"' + " LIKE '"
                    if("PROVNO" in attrName):
                        queText += i.attribute("PROVNO")
                    else:
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
                
                queText += "' "
                
                que.clear()
                que.setSql(queText)
                que.accept()

                if layer2.featureCount() > 0:
                    if self.mergeCenter:
                        for j in layer2.getFeatures():
                            score = self.calcMapCurvesGeom(
                                i.geometry(),
                                self.translateCenterGeom(i.geometry(), j.geometry())
                            )
                            self.similarLayer.append([i.id(),j.id(), score])
                    else:
                        for j in layer2.getFeatures(): 
                            score = self.calcMapCurvesGeom(
                                i.geometry(), j.geometry()
                            )
                            if(score > -1):
                                self.similarLayer.append([i.id(),j.id(), score]) 
                que.clear()
                que.accept()
                progress = progress+((1/layer.featureCount())*100)
                self.setProgress(progress)
            except KeyError as identifier:
                # show error message
                self.emit("CALC_ERR", "It might be not Wilkerstat, PROVNO, KABKOTNO, KECNO, DESANO is required")

    def calculateSq(self, layer:QgsVectorLayer, layer2:QgsVectorLayer):
        
        # progress = 0
        for i in layer.getFeatures():
            for j in layer2.getFeatures(i.geometry().boundingBox()):
                if(i.hasGeometry()):
                    self.calcMapCurves(i, j)
            # progress = progress+((1/layer.featureCount())*100)
            # QgsMessageLog.logMessage("Progress : "+str(progress))
            # self.setProgress(progress)

    def calculateKNN(self, layer:QgsVectorLayer, layer2:QgsVectorLayer, radius:float):
    
        progress = 0
        for i in layer.getFeatures() :
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
            progress = progress+((1/layer.featureCount())*100)
            # print("setting progress")
            # self.setProgress(progress)
            # print("progress setted")
    
    def run(self):
        # print("runnnningggg.....!!!")
        # QgsMessageLog.logMessage("runninggggggg..........!!!!", 'TaskFromFunction', Qgis.Success)
        print(datetime.datetime.now())
        if(self.method == 0):
            print("sq method")
            print([self.layer.featureCount(), self.layer2.featureCount()])
            self.calculateSq(self.layer, self.layer2)            
            print("executed")
            print(self.similarLayer)
        elif (self.method == 1):
            self.calculateKNN(self.layer, self.layer2)
        else:
            self.calculateWK(self.layer, self.layer2)
        return True

    def finished(self, result):
        if result:
            # QgsMessageLog.logMessage("finished")
            print("finished")
        else:
            # QgsMessageLog.logMessage("not finished")
            print("not finished")

    def cancel(self):
        super().cancel()

class CalculationThread(QThread):

    def __init__(self,
        layer:QgsVectorLayer,
        layer2:QgsVectorLayer,
        treshold:float, 
        method=0,
        mergeCenter=False
    ):
        super(CalculationThread).__init__()
        self.similarLayer = []
        self.layer = layer
        self.layer2 = layer2
        self.treshold = treshold
        self.method = method
        self.mergeCenter = mergeCenter
        self.similarList = pyqtSignal(list)
        self.progressCalc = pyqtSignal(int)
        self.featureCounter = pyqtSignal(int)
    
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
        
        treshold = treshold/100

        if self.method == 1:
            score = self.calcMapCurvesGeom(
                        feature.geometry(),
                        self.translateCenterGeom(feature2.geometry(),feature.geometry()) 
                    )
        else:
            score = self.calcMapCurvesGeom(feature.geometry(), feature2.geometry())

        if score >= treshold:
            self.similarLayer.append([feature.id(), feature2.id(), score])

    def calculateWK(self, layer:QgsVectorLayer, layer2:QgsVectorLayer, translate=False):
        self.featureCounter.emit("FEATURE_COUNT", layer.featureCount())
        progress = 1/layer.featureCount()
        
        attrName = layer.dataProvider().fields().names()
        attrName2 = layer2.dataProvider().fields().names()
        
        # pkCheck = self.wilkerstatPKExist(layer, layer2)

        for i in layer.getFeatures():
            # Querying for matching attribute 
            
            que = QgsQueryBuilder(layer2)
            
            queText = ""
            try:
                if("PROVNO" in attrName2):
                    queText += '"PROVNO"' + " LIKE '"
                    if("PROVNO" in attrName):
                        queText += i.attribute("PROVNO")
                    else:
                        queText += i.attribute("provno")
                else:
                    queText += '"provno"' + " LIKE '"
                    if("PROVNO" in attrName):
                        queText += i.attribute("PROVNO")
                    else:
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
                
                queText += "' "
                
                que.clear()
                que.setSql(queText)
                que.accept()

                if layer2.featureCount() > 0:
                    if self.mergeCenter:
                        for j in layer2.getFeatures():
                            score = self.calcMapCurvesGeom(
                                i.geometry(),
                                self.translateCenterGeom(i.geometry(), j.geometry())
                            )
                            self.similarLayer.append([i.id(),j.id(), score])
                    else:
                        for j in layer2.getFeatures(): 
                            score = self.calcMapCurvesGeom(
                                i.geometry(), j.geometry()
                            )
                            if(score > -1):
                                self.similarLayer.append([i.id(),j.id(), score]) 
                que.clear()
                que.accept()
                self.progressCalc.emit("CALC_PROGRESS", progress)
                progress = progress+(1/layer.featureCount())
            except KeyError as identifier:
                # show error message
                self.emit("CALC_ERR", "It might be not Wilkerstat, PROVNO, KABKOTNO, KECNO, DESANO is required")
        
        return self.similarLayer

    def calculateSq(self, layer:QgsVectorLayer, layer2:QgsVectorLayer):
        self.featureCounter.emit("FEATURE_COUNT", layer.featureCount())
        progress = 1/layer.featureCount()
        for i in layer.getFeatures():
            for j in layer2.getFeatures(i.geometry().boundingBox()):
                if(i.hasGeometry()):
                    self.calcMapCurves(i, j)
            self.progressCalc.emit("CALC_PROGRESS", progress)
            progress = progress+(1/layer.featureCount())

        return self.similarLayer

    def calculateKNN(self, layer:QgsVectorLayer, layer2:QgsVectorLayer, radius:float):
        self.featureCounter.emit("FEATURE_COUNT", layer.featureCount())
        progress = 1/layer.featureCount()
        for i in layer.getFeatures() :
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
            self.progressCalc.emit("CALC_PROGRESS", progress)
            progress = progress+(1/layer.featureCount())

        return self.similarLayer

    def run(self):
        if self.method == 0:
            self.calculateSq(self.layer, self.layer2)
            self.similarList.emit("CALC_FINISHED", self.similarLayer)
        elif self.method == 1:
            self.calculateKNN(self.layer, self.layer2)
            self.similarList.emit("CALC_FINISHED", self.similarLayer)
        else:
            self.calculateWK(self.layer, self.layer2)
            self.similarList.emit("CALC_FINISHED", self.similarLayer)