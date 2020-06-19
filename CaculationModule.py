from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import QIcon, QColor
from qgis.PyQt.QtWidgets import QAction

from qgis.core import (QgsProject, 
    QgsVectorLayer, 
    QgsGeometry, 
    QgsFeature, 
    QgsField, 
    QgsRectangle
)

class CalculationModule(object):
    def __init__(
        self,
        treshold:double, 
        method=0
        ):
        
        super().__init__()
        similarLayer = []

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
            if(pkCheck.count(False) > 3 ):
                break
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

    def calculateKNN(self, layer:QgsVectorLayer, layer2:QgsVectorLayer, radius:double):
        
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
    


    