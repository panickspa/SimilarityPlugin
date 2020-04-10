import threading
from qgis.core import QgsProject, QgsVectorLayer, QgsGeometry
from qgis.gui import QgsMapCanvas

import sys, os
from subprocess import Popen, PIPE


class CheckThread (threading.Thread) : 

    def __init__(self, threadId, layer, layer2, iterLayer, treshold, textEditConsole):
        threading.Thread.__init__(self)
        self.threadId = threadId
        self.layer = layer
        self.layer2 = layer2
        self.similarLayer = []
        self.iter = iterLayer
        self.treshold = treshold
        self.threadLock = threading.Lock()
        self.textEditConsole = textEditConsole

    def calculateScore(self):
        self.similarLayer = []

        # layer = QgsProject.instance().layerTreeRoot().children()[
        #     self.dlg.layerSel1.currentIndex()
        # ].layer()
        # layer2 = QgsProject.instance().layerTreeRoot().children()[
        #     self.dlg.layerSel2.currentIndex()
        # ].layer()

        neightbourList = self.getCheckPointList(self.layer, self.layer2)

        # c = QgsProject.instance().layerTreeRoot().children()[
        #     self.dlg.layerSel1.currentIndex()
        # ].layer().featureCount()
        # c2 = QgsProject.instance().layerTreeRoot().children()[
        #     self.dlg.layerSel1.currentIndex()
        # ].layer().featureCount()
        
        for i in neightbourList :
            
            # writing dump on f.txt
            f = open(self.fileOut, "w")
            f.write(
                QgsProject.instance().layerTreeRoot().children()[
                    self.dlg.layerSel1.currentIndex()
                    ].layer().getFeature(i[0]).geometry().asWkt()
            )
            f.close()

            # writing dump on f2.txt
            f2 = open(self.fileOut2, "w")
            f2.write(
                QgsProject.instance().layerTreeRoot().children()[
                    self.dlg.layerSel2.currentIndex()
                    ].layer().getFeature(i[1]).geometry().asWkt()
            )
            f2.close()
            
            # exceuting command
            p = Popen([self.enginePath, self.fileOut, self.fileOut2], stdin=PIPE, stdout=PIPE, stderr=PIPE)
            score = p.communicate()[0]
            p.stdout.close()
            try:
                consoleOut = self.textEditConsole.toPlainText()+'\n'+'\n'+" "+str(i[0])+","+str(i[1])+" : "+score.decode('utf-8').replace('\n', '').replace('\n', '')
                self.textEditConsole.setText(consoleOut)
                float(
                    score.decode('utf-8').replace('\r','').replace('\n', '').replace('\n', '')
                )
                if float(score) > self.treshold/100:
                    self.similarLayer.append([i[0],i[1]])
            except ValueError:
                consoleOut = self.textEditConsole.toPlainText()+'\n'+'\n'+" "+str(i[0])+","+str(i[1])+" : "+score.decode('utf-8')
                self.textEditConsole.setText(consoleOut)

        # score = "0"
        # self.dlg.labelScore.setText("Score : "+ score)
        # enabling function
        if len(self.similarLayer) > 0 :
            self.dlg.previewBtn.setEnabled(True)

    def getCheckPointList(self, layer, layer2):
        checkList = []
        
        for i in range(0, self.iter[0]):
            checkList.append(
                [
                    i, self.getNearestIter(
                        layer2, layer.getFeature(i)
                    )
                ]
            )

        return checkList

    def getNearestIter(self, layer, feature):

        nearestDist = QgsGeometry.distance(
            layer.getFeature(0).geometry().centroid(),
            feature.geometry().centroid()
        )

        i = 1
        nearestIter = 0

        while i < self.iter[1]:
            dist = QgsGeometry.distance(
                    feature.geometry().centroid(),
                    layer.getFeature(i).geometry().centroid()
                )
            if(
                dist
                 <
                nearestDist
            ):
                nearestDist = dist
                nearestIter = i
            i = i+1

        return nearestIter
    
    def run(self):
        self.threadLock.acquire()
        self.similarLayer()
        self.threadLock.release()