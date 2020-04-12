# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SimilarityPlugin
                                 A QGIS plugin
 Calculate score of similarity
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-03-20
        git sha              : $Format:%H$
        copyright            : (C) 2020 by STIS
        email                : 16.9350@stis.ac.id
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import QIcon, QColor
from qgis.PyQt.QtWidgets import QAction

from qgis.core import QgsProject, QgsVectorLayer, QgsGeometry, QgsFeature, QgsField

from qgis.gui import QgsMapCanvas, QgsQueryBuilder

from subprocess import Popen, PIPE
# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .similarity_plugin_dialog import SimilarityPluginDialog

import sys, os
from copy import copy

from timeit import default_timer as timer 

from numpy import *

# import numba, cudatoolkit

class SimilarityPlugin:
    """QGIS Plugin Implementation."""

    def __init__(
        self, 
        iface
    ):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Layer preview
        
        self.previewLayer = 0
        self.previewLayer2 = 0

        self.signals = pyqtSignal()
        self.similarLayer = []

        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'SimilarityPlugin_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Calculate Similarity Map')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('SimilarityPlugin', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/similarity_plugin/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Check Similarity ...'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Calculate Similarity Map'),
                action)
            self.iface.removeToolBarIcon(action)

    # gui interaction (general item)
    def pkCheckBox(self, int):
        if self.dlg.checkBoxPk.isChecked():
            self.dlg.lineEditPK.setEnabled(True)
        else:
            self.dlg.lineEditPK.setEnabled(False)

    def methodChange(self):
        if self.dlg.methodComboBox.currentIndex() == 2:
            self.dlg.mergeCenterCheck.setChecked(False)
            self.dlg.mergeCenterCheck.setEnabled(True)
            self.dlg.lineEditTreshold.setEnabled(False)
        elif self.dlg.methodComboBox.currentIndex() == 0:
            self.dlg.mergeCenterCheck.setChecked(False)
            self.dlg.mergeCenterCheck.setEnabled(False)
            self.dlg.lineEditTreshold.setEnabled(True)
        elif self.dlg.methodComboBox.currentIndex() == 1:
            self.dlg.mergeCenterCheck.setChecked(True)
            self.dlg.mergeCenterCheck.setEnabled(False)
            self.dlg.lineEditTreshold.setEnabled(True)

    # def filterCheckBox(self):
    #     if self.dlg.filterCheck.isChecked():
    #         self.dlg.textEditSQL.setEnabled(True)
    #         self.dlg.textEditSQL_2.setEnabled(True)
    #     else:
    #         self.dlg.textEditSQL.setEnabled(False)
    #         self.dlg.textEditSQL_2.setEnabled(False)

    # canvas interaction
    def resultPreview(self):
        self.previewLayer = 0
        self.previewLayer2 = 0
        self.refreshPreview()

        self.dlg.widgetCanvas.enableAntiAliasing(True)

        self.dlg.nextBtn.setEnabled(True)
        self.dlg.previousBtn.setEnabled(True)
        self.dlg.removeBtn.setEnabled(True)
        
    def attrPrinter(self, fieldsList, feature, place):
        temp = ''

        for f in fieldsList:
            temp += f.name()
            temp += ' : '
            temp += str(feature.attribute(f.name()))
            temp += '\n' 
        
        place.setText(temp)

    def refreshPreview(self):
        if len(self.similarLayer) > 0 :
            self.layerCanvas = QgsVectorLayer("Polygon?crs=ESPG:4326",'SimilarityLayer','memory')
            self.layer2Canvas = QgsVectorLayer("Polygon?crs=ESPG:4326",'SimilarityLayer','memory')

            self.previewLayerFeature = self.layer.getFeature(self.similarLayer[self.previewLayer][0])
            self.previewLayerFeature2 = self.layer2.getFeature(self.similarLayer[self.previewLayer][1])

            scoreLabel = "Score : " + str(self.similarLayer[self.previewLayer][2])
            if(self.dlg.methodComboBox.currentIndex() == 1) :
                distance = QgsGeometry.distance(
                            self.previewLayerFeature.geometry().centroid(), self.previewLayerFeature2.geometry().centroid()
                        )
                if distance < 0.00001:
                    distance = 0
                self.dlg.labelScore.setText(scoreLabel+ " - Distance : "+str(
                        round(distance, 4)
                    )+ " meter"
                )
            else:
                self.dlg.labelScore.setText(scoreLabel)

            self.attrPrinter(self.layer.dataProvider().fields().toList(), self.previewLayerFeature, self.dlg.previewAttr)
            self.attrPrinter(self.layer2.dataProvider().fields().toList(), self.previewLayerFeature2, self.dlg.previewAttr_2)


            self.layerCanvas.dataProvider().addFeature(self.previewLayerFeature)
            # self.dlg.consoleTextEdit.setText(self.dlg.consoleTextEdit.toPlainText()+"\n\n feature added count : \n "+str(
            #        self.layerCanvas.featureCount()
            #     ))
                
            if self.dlg.mergeCenterCheck.isChecked():
                self.tGeom = self.translateCenterGeom(
                    self.previewLayerFeature2.geometry(),
                    self.previewLayerFeature.geometry()
                )
                self.nFeat = QgsFeature(self.previewLayerFeature2)
                self.nFeat.setGeometry(self.tGeom)
                self.layer2Canvas.dataProvider().addFeature(self.nFeat)
            else:
                self.layer2Canvas.dataProvider().addFeature(self.previewLayerFeature2)
            # self.dlg.consoleTextEdit.setText(self.dlg.consoleTextEdit.toPlainText()+"\n\n feature2 added count : \n "+str(
            #         self.layer2Canvas.featureCount()
            #     ))

            self.dlg.widgetCanvas.setExtent(self.previewLayerFeature.geometry().boundingBox(), True)
            
            self.dlg.widgetCanvas.setDestinationCrs(self.layerCanvas.sourceCrs())
            
            # self.canvas.setDestinationCrs(self.layerCanvas.sourceCrs())
            # self.canvas.setExtent(self.layerCanvas.extent())

            symbol = self.layerCanvas.renderer().symbol()
            symbol.setColor(QColor(0,147,221,127))

            symbol2 = self.layer2Canvas.renderer().symbol()
            symbol2.setColor(QColor(231,120,23,127))

            self.dlg.widgetCanvas.setLayers([self.layer2Canvas, self.layerCanvas])

            self.dlg.widgetCanvas.refresh()

    def nextPreview(self):
        # f2 = open("engine/f2.txt", "w")
        if(self.previewLayer+1 < len(self.similarLayer)
            ):
            self.previewLayer = self.previewLayer+1
        self.dlg.consoleTextEdit.setText(self.dlg.consoleTextEdit.toPlainText()+"\n\n Current Similar Layer Index : \n  "+str([self.similarLayer[self.previewLayer], self.previewLayer]))
        self.refreshPreview()

    def previousPreview(self):
        if(self.previewLayer-1 > -1):
            self.previewLayer = self.previewLayer-1
        self.dlg.consoleTextEdit.setText(self.dlg.consoleTextEdit.toPlainText()+"\n\n Current Similar Layer Index : \n  "+str([self.similarLayer[self.previewLayer], self.previewLayer]))
        self.refreshPreview()

    def rmFeatResult(self):
        self.similarLayer.pop(self.previewLayer)

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
 
    def calcMapCurves(self, feature, feature2):
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
        
        treshold = self.dlg.lineEditTreshold.value()/100

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
            # self.dlg.consoleTextEdit.setText(self.dlg.consoleTextEdit.toPlainText()+"\n"+str(feat2Id))
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
        self.dlg.consoleTextEdit.setText(self.dlg.consoleTextEdit.toPlainText()+"\nElapsedTime"+str(
            elapsed
        ))

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
                # self.dlg.consoleTextEdit.setText(self.dlg.consoleTextEdit.toPlainText()+"\nIter"+str(
                #     [i,j]
                # ))
                if switchState:
                    self.calcMapCurves(layer.getFeature(ids[j]), layer2.getFeature(ids2[i]))
                else:
                    self.calcMapCurves(layer.getFeature(ids[i]), layer2.getFeature(ids2[j]))
        
        elapsed = timer() - start
        self.dlg.consoleTextEdit.setText(self.dlg.consoleTextEdit.toPlainText()+"\nElapsedTime"+str(
            elapsed
        )+" "+str([i,j]))

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
        # self.dlg.consoleTextEdit.setText(
        #     self.dlg.consoleTextEdit.toPlainText()+"\n\n checkpoint : "+str(checkList)
        # )
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
            # self.dlg.consoleTextEdit.setText(
            #     self.dlg.consoleTextEdit.toPlainText()+"\n\n check process : "+str([
            #         layer.getFeature(ids_[j]).attributes(),
            #         feature.attributes(),
            #         dist
            #     ])
            # )
            if(
                abs(dist) < abs(nearestDist)
            ):
                nearestDist = dist
                nearestIter = j

        # self.dlg.consoleTextEdit.setText(
        #     self.dlg.consoleTextEdit.toPlainText()+"\n\n iter nearest : "+str([last, nearestIter, nearestDist])
        # )
        return nearestIter
 
    def calculateKNN(self, layer, layer2):
        start = timer()
        neightbourList = self.getCheckPointList(layer, layer2)
        
        for i in neightbourList :
            # writing dump on f.txt 
            self.calcMapCurves(layer.getFeature(i[0]), layer2.getFeature(i[1]))
        
        elapsed = timer() - start
        self.dlg.consoleTextEdit.setText(self.dlg.consoleTextEdit.toPlainText()+"\nElapsedTime"+str(
            elapsed
        ))

    def addScoreItem(self):
        self.layer.commitChanges()
        self.layer2.commitChanges()

        scoreFieldIndex = self.layer.dataProvider().fieldNameIndex(self.dlg.attrOutLineEdit.text())
        scoreFieldIndex2 = self.layer2.dataProvider().fieldNameIndex(self.dlg.attrOutLineEdit.text())

        idIndex = self.layer.dataProvider().fieldNameIndex('id')
        idIndex2 = self.layer2.dataProvider().fieldNameIndex('id')

        matchIndex = self.layer.dataProvider().fieldNameIndex('match')
        matchIndex2 = self.layer2.dataProvider().fieldNameIndex('match')

        self.layer.startEditing()
        self.layer2.startEditing()

        for sim in self.similarLayer:
            self.dlg.consoleTextEdit.setText(
                self.dlg.consoleTextEdit.toPlainText()+"\n\n editing value "+
                    str([
                        [sim[0], scoreFieldIndex, sim[2]],
                        self.layer.changeAttributeValue(sim[0], scoreFieldIndex, sim[2]),
                        [sim[0], idIndex, sim[0]],
                        self.layer.changeAttributeValue(sim[0], idIndex, sim[0]),
                        [sim[0], matchIndex, sim[1]],
                        self.layer.changeAttributeValue(sim[0], matchIndex, sim[1]),
                        self.layer2.changeAttributeValue(sim[1], scoreFieldIndex2, sim[2]),
                        self.layer2.changeAttributeValue(sim[1], idIndex2, sim[1]),
                        self.layer2.changeAttributeValue(sim[1], matchIndex2, sim[0])
                    ])
                 +" \n\n"
            )
            self.layer.changeAttributeValue(sim[0], scoreFieldIndex, sim[2])
            self.layer.changeAttributeValue(sim[0], idIndex, sim[0])
            self.layer.changeAttributeValue(sim[0], matchIndex, sim[1])
            self.layer2.changeAttributeValue(sim[1], scoreFieldIndex2, sim[2])
            self.layer2.changeAttributeValue(sim[1], idIndex2, sim[1])
            self.layer2.changeAttributeValue(sim[1], matchIndex2, sim[0])
        
        self.dlg.consoleTextEdit.setText(
                self.dlg.consoleTextEdit.toPlainText()+"\n\n commiting "+str(
                    [
                        self.layer.commitChanges(),
                        self.layer.commitErrors(),
                        self.layer2.commitChanges(),
                        self.layer2.commitErrors()
                    ]
                )
        )

        self.layer.commitChanges()
        self.layer2.commitChanges()

    def calculateScore(self):
        
        # self.dlg.previewBtn.setEnabled(False)
        self.dlg.saveBtn.setEnabled(False)
        self.dlg.nextBtn.setEnabled(False)
        self.dlg.removeBtn.setEnabled(False)

        self.similarLayer = []
        self.currentCheckLayer = [self.dlg.layerSel1.currentIndex(), self.dlg.layerSel2.currentIndex()]

        # qkab = QgsQueryBuilder(
        #     QgsProject.instance().layerTreeRoot().children()[self.currentCheckLayer[0]].layer()
        # )
        # qkab_temp = qkab.sql()
        # qkab_2 = QgsQueryBuilder(
        #     QgsProject.instance().layerTreeRoot().children()[self.currentCheckLayer[1]].layer()
        # )
        # qkab_2_temp = qkab_2.sql()

        # if(self.dlg.filterCheck.isChecked()):
        #     qkab.clear()
        #     sqlkab = self.dlg.textEditSQL.toPlainText().decode("utf-8")
        #     qkab.setSql(sqlkab)
        #     qkab.accept()
        #     qkab_2.clear()
        #     sqlkab2 = self.dlg.textEditSQL.toPlainText().decode("utf-8")
        #     qkab_2.setSql(sqlkab2)
        #     qkab_2.accept()

        # layer = QgsProject.instance().layerTreeRoot().children()[
        #     self.currentCheckLayer[0]
        # ].layer()
        # layer2 = QgsProject.instance().layerTreeRoot().children()[
        #     self.currentCheckLayer[1]
        # ].layer()

        # duplicating layer for better performance
        layername = str(self.dlg.prefLineEdit.text())+str(QgsProject.instance().layerTreeRoot().children()[self.currentCheckLayer[0]].layer().name())
        self.layer = QgsVectorLayer("Polygon?crs=ESPG:4326",
                        layername,
                        'memory')
        self.layer.setCrs(
            QgsProject.instance().layerTreeRoot().children()[
                self.currentCheckLayer[0]
            ].layer().sourceCrs()
        )
        self.layer.dataProvider().addAttributes(
            QgsProject.instance().layerTreeRoot().children()[
                self.currentCheckLayer[0]
            ].layer().dataProvider().fields().toList()
        )
        self.layer.dataProvider().addAttributes(
            [
                QgsField(self.dlg.attrOutLineEdit.text(), QVariant.Double),
                QgsField('id', QVariant.Int),
                QgsField('match', QVariant.Int)
            ]
        )
        self.layer.updateFields()
        self.layer.dataProvider().addFeatures(
            [f for f in QgsProject.instance().layerTreeRoot().children()[
                self.currentCheckLayer[0]
            ].layer().getFeatures()]
        )

        # layer.dataProvider().addFeatures(QgsProject.instance().layerTreeRoot().children()[
        #     self.currentCheckLayer[0]
        # ].layer().getFeatures())
        layername = str(self.dlg.prefLineEdit.text())+str(QgsProject.instance().layerTreeRoot().children()[self.currentCheckLayer[1]].layer().name())
        self.layer2 = QgsVectorLayer("Polygon?crs=ESPG:4326",
                        layername,
                        'memory')
        self.layer2.setCrs(
            QgsProject.instance().layerTreeRoot().children()[
                self.currentCheckLayer[1]
            ].layer().sourceCrs()
        )
        self.layer2.dataProvider().addAttributes(
            QgsProject.instance().layerTreeRoot().children()[
                self.currentCheckLayer[1]
            ].layer().dataProvider().fields().toList()
        )
        self.layer2.dataProvider().addAttributes(
            [
                QgsField(self.dlg.attrOutLineEdit.text(), QVariant.Double),
                QgsField('id', QVariant.Int),
                QgsField('match', QVariant.Int)
            ]
        )
        self.layer2.updateFields()
        self.layer2.dataProvider().addFeatures(
            [f for f in QgsProject.instance().layerTreeRoot().children()[
                self.currentCheckLayer[1]
            ].layer().getFeatures()]
        )

        if self.dlg.methodComboBox.currentIndex() == 0:
            self.calculateSq(self.layer, self.layer2)
        elif self.dlg.methodComboBox.currentIndex() == 1:
            self.calculateKNN(self.layer, self.layer2)
        elif self.dlg.methodComboBox.currentIndex() == 2:
            #self.threadCalc = CalculateThread(layer, layer2, 2) 
            self.calculateWK(self.layer, self.layer2)

        cText = "Feature Count of Result: "+str(len(self.similarLayer))
        
        if len(self.similarLayer) > 0 :
            self.addScoreItem()
            self.previewLayer = 0
            self.dlg.saveBtn.setEnabled(True)
            self.dlg.counterLabel.setText(cText)
            self.dlg.consoleTextEdit.setText(self.dlg.consoleTextEdit.toPlainText()+"\n\n Similar Layer Result index :  "+str(self.similarLayer))
            self.resultPreview()
        else:
            self.previewLayer = 0
            self.dlg.counterLabel.setText(cText)
    
    def registerToProject(self):
        layer = QgsVectorLayer("Polygon?crs=ESPG:4326",
                        self.layer.name(),
                        'memory')
        layer.setCrs(
            self.layer.sourceCrs()
        )
        layer.dataProvider().addAttributes(
            self.layer.dataProvider().fields().toList()
        )
        layer.updateFields()
        layer.dataProvider().addFeatures(
            [self.layer.getFeature(f[0]) for f in self.similarLayer]
        )

        layer2 = QgsVectorLayer("Polygon?crs=ESPG:4326",
                        self.layer2.name(),
                        'memory')
        layer2.setCrs(
            self.layer2.sourceCrs()
        )
        layer2.dataProvider().addAttributes(
            self.layer2.dataProvider().fields().toList()
        )
        layer2.updateFields()
        layer2.dataProvider().addFeatures(
            [self.layer2.getFeature(f[1]) for f in self.similarLayer]
        )
        QgsProject.instance().addMapLayers([layer, layer2])

    def run(self):
        """Run method that performs all the real work"""
        
        # init run variable
        self.previewLayer = 0
        self.previewLayer2 = 0
        self.currentCheckLayer = [0,0]
        self.canvas = QgsMapCanvas()


        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = SimilarityPluginDialog()

        layers = QgsProject.instance().layerTreeRoot().children()

        layer_list = [layer.name() for layer in layers]

        self.dlg.layerSel1.clear()
        self.dlg.layerSel1.addItems(layer_list)
        
        self.dlg.layerSel2.clear()
        self.dlg.layerSel2.addItems(layer_list)

        # self.dlg.filterCheck.stateChanged.connect(self.filterCheckBox)
        
        self.dlg.methodComboBox.addItems(
            [
                'Squential',
                'Nearest Neightbour',
                'Wilkerstat BPS'
            ]
        )

        self.dlg.methodComboBox.currentIndexChanged.connect(self.methodChange)

        self.dlg.nextBtn.clicked.connect(self.nextPreview)
        self.dlg.previousBtn.clicked.connect(self.previousPreview)

        self.dlg.calcBtn.clicked.connect(self.calculateScore)

        self.dlg.saveBtn.clicked.connect(self.registerToProject)

        self.dlg.removeBtn.clicked.connect(self.rmFeatResult)

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
