from qgis.PyQt.QtCore import *
from qgis.core import QgsProject, QgsVectorLayer, QgsGeometry, QgsFeature, QgsField
from qgis.gui import QgsMapCanvas, QgsQueryBuilder
import time
from timeit import default_timer as timer 
import traceback, sys

class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.similarLayer = []
        self.kwargs['progress_callback'] = self.signals.progress

     # manipulating geom
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

    # calculating score
    def calcMapCurvesGeom(self, g, g2):
        inter = g.intersection(g2)
        if(inter.isEmpty()):
            return 0
        else:
            score = (inter.area()/g.area())*(inter.area()/g2.area())
            return round(score, 4)
 
    def calcMapCurves(self, feature, feature2, t):
        if self.dlg.methodComboBox.currentIndex() == 1:
            score = self.calcMapCurvesGeom(
                        feature.geometry(),
                        feature2.geometry()
                    )
            if score <= self.dlg.lineEditTreshold.value():
                score = self.calcMapCurvesGeom(
                        feature.geometry(),
                        self.translateCenterGeom(feature2.geometry(),feature.geometry()) 
                    )
        else:
            score = self.calcMapCurvesGeom(feature.geometry(), feature2.geometry())
        
        treshold = t/100

        if score >= treshold:
            self.similarLayer.append([feature.id(), feature2.id(), score])
    
    def calculateWK(self, layer, layer2):
        ids = [f.id() for f in layer.getFeatures()]
        start = timer()
        for i in ids:
            # Querying 
            que = QgsQueryBuilder(layer2)
            queTemp = que.sql()
            queText = '"PROVNO"' + " LIKE '"
            queText += layer.getFeature(i).attribute("PROVNO")
            queText += "'"+' AND "KABKOTNO" ' + " LIKE '"
            queText += layer.getFeature(i).attribute("KABKOTNO")
            queText += "'"+' AND "KECNO" ' + "LIKE '"
            queText += layer.getFeature(i).attribute("KECNO")
            queText += "'"+' AND "DESANO" ' + "LIKE '"
            queText += layer.getFeature(i).attribute("DESANO")+"' "
            que.clear()
            que.setSql(queText)
            que.accept()
            # getting id
            feat2Id = [f.id() for f in layer2.getFeatures()]
            if layer2.featureCount() > 0:
                if self.dlg.mergeCenterCheck.isChecked():
                    for j in feat2Id:
                        score = self.calcMapCurvesGeom(
                                layer.getFeature(i).geometry(),
                                layer2.getFeature(i).geometry()
                            )
                        # translate if only needed
                        if score <= 0:
                            score = self.calcMapCurvesGeom(
                                layer.getFeature(i).geometry(),
                                self.translateCenterGeom(layer2.getFeature(i).geometry(), layer.getFeature(j).geometry())
                            )
                            self.similarLayer.append([i,j, score])
                        else:
                            self.similarLayer.append([i,j, score])
                else:
                    for j in feat2Id: 
                        score = self.calcMapCurvesGeom(
                            layer.getFeature(i).geometry(), layer2.getFeature(j).geometry()
                        )
                        if(score > -1):
                            self.similarLayer.append([i,j, score])
            que.clear()
            que.setSql(queTemp)
            que.accept()
        
        elapsed = timer() - start

    def calculateSq(self, layer, layer2):
        start = timer()

        longest = layer
        shortest = layer2
        switchState = False

        if longest.featureCount() < shortest.featureCount():
            longest = layer2
            shortest = layer
            switchState = True

        ids = [f.id() for f in longest.getFeatures()]
        ids2 = [f.id() for f in shortest.getFeatures()]
        
        
        for i in range(0, len(ids)):
            for j in range(i, len(ids2)):
                if switchState:
                    self.calcMapCurves(layer.getFeature(ids[j]), layer2.getFeature(ids2[i]))
                else:
                    self.calcMapCurves(layer.getFeature(ids[i]), layer2.getFeature(ids2[j]))
        
        elapsed = timer() - start

    # get nearest neightbour list
    def getCheckPointList(self, layer, layer2):
        
        longest = layer
        shortest = layer2
        switched = False
        
        if(layer.featureCount() < layer2.featureCount()):
            longest = layer2
            shortest = layer   
            switched = True
        
        checkList = []
        ids = [f.id() for f in shortest.getFeatures()]
        ids_ = [f.id() for f in longest.getFeatures()]
        
        for i in range(0, len(ids)):
            nearestI = self.getNearestIter(
                        longest, 
                        ids_,
                        shortest.getFeature(ids[i]),
                        i
                    )
            if (nearestI is not None) :
                if switched:
                    checkList.append(
                        [
                            ids[i], ids_[nearestI] 
                        ]
                    )
                else:
                    checkList.append(
                        [
                            ids_[nearestI], ids[i]
                        ]
                    )

        return checkList

    # get nearest iter
    def getNearestIter(self, layer, ids_, feature, last):
        # count = 101
        nearestDist = QgsGeometry.distance(
            layer.getFeature(ids_[last]).geometry().centroid(),
            feature.geometry().centroid()
        )
        nearestIter = last
        for j in range(last, len(ids_)):
            dist = QgsGeometry.distance(
                    feature.geometry().centroid(),
                    layer.getFeature(ids_[j]).geometry().centroid()
                )
            if(
                abs(dist) < abs(nearestDist)
            ):
                nearestDist = dist
                nearestIter = j

        return nearestIter
 
    def calculateKNN(self, layer, layer2):
        start = timer()
        neightbourList = self.getCheckPointList(layer, layer2)
        
        for i in neightbourList :
            # writing dump on f.txt 
            self.calcMapCurves(layer.getFeature(i[0]), layer2.getFeature(i[1]))
        
        elapsed = timer() - start

    @pyqtSlot()
    def run(self):
        # Your code goes in this function
        self.fn(*self.args, **self.kwargs)
        # for n in range(0, 1000):
        #     progress_callback.emit(n*100/1000)
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit() 

class WorkerSignals(QObject):

    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data
    
    error
        `tuple` (exctype, value, traceback.format_exc() )
    
    result
        `object` data returned from processing, anything

    progress
        `int` indicating % progress 

    '''
    
    finished = pyqtSignal(str)
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)