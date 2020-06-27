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

# importing PyQt environment
from qgis.PyQt.QtCore import QCoreApplication, QSettings, QThread, QTranslator, QUrl
from qgis.PyQt.QtGui import QIcon, QColor
from qgis.PyQt.QtWidgets import QAction, QTextEdit


# importing qgis environment
from qgis.core import (
    QgsProject, 
    QgsVectorLayer, 
    QgsMeshLayer, 
    QgsPluginLayer, 
    QgsRasterLayer, 
    QgsGeometry, 
    QgsFeature, 
    QgsField, 
    QgsRectangle, 
    QgsProcessingContext,
    QgsTaskManager,
    QgsTask,
    QgsProcessingAlgRunnerTask,
    Qgis,
    QgsProcessingFeedback,
    QgsApplication,
    QgsMessageLog
)

from qgis.gui import QgsMapCanvas, QgsQueryBuilder, QgsMapToolPan

# Initialize Qt resources from file resources.py
from .resources import *

# Import the code for the dialog
from .similarity_plugin_dialog import SimilarityPluginDialog
# Import additional dialog
from .warn_plugin_dialog import WarnDialog
from .CaculationModule import *
from .simple_warning_dialog import SimpleWarnDialog
from .CaculationModule import *

import sys, os
from timeit import default_timer as timer

class SimilarityPlugin:
    """
    Similarity Plugin parent class
    
    ..

    Attributes
    -----------

    layer : QgsVectorLayer
        First layer
    layer2 : QgsVectorLayer
        Second layer
    dlg : SimilarityPluginDialog
        MainPluginDialog
    simpleDialog : SimpleWarningDialog
        Show simple warning
    similarLayer : list=[]
        The result of calculation process
    previewLayer: int=0
        Current index similarLayer that previewed in canvas widget  
    calcThread : QThread(self.iface)
        Thread for data processing
    calcTask : CalculationModule
        Calculation module for checking similarity
    iface : QgsInterface
        An interface instance that will be passed to this class
        which provides the hook by which you can manipulate the QGIS
        application at run time.

    
    Methods
    --------

    resultPreview()
        Activate preview section
    
    attrPrinter(fieldList: object, feature: QgsFeature, place: QTextEdit)
        Print feature atrribute info on text edit in preview section


    """
    
    layer : QgsVectorLayer #: First layer
    layer2 : QgsVectorLayer #: Second layer
    simpleDialog : SimpleWarnDialog #: Simple warning dialog

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
        self.similarLayer = []
        """  """
        self.previewLayer = 0
        self.calcTask = CalculationModule()
        # Save reference to the QGIS interface
        self.iface = iface
        
        # Registering worker calculation
        self.calcThread = QThread(self.iface)
        self.calcTask.moveToThread(self.calcThread)
        self.calcThread.started.connect(self.calcTask.run)
        self.calcThread.setTerminationEnabled(True)
        
        # multithreading signal calculation      
        self.calcTask.progress.connect(self.updateCalcProgress)
        self.calcTask.progressSim.connect(self.updateSimList)
        self.calcTask.finished.connect(self.finishedCalcThread)
        self.calcTask.error.connect(self.errorCalcThread)
        self.calcTask.eventTask.connect(self.eventCalcThread)

        # pan event
        self.actionPan = QAction("Pan", self.iface)

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
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/similarity_plugin/icon-24.png'
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
            self.iface.removePluginVectorMenu(
                self.tr(u'&Calculate Similarity Map'),
                action)
            self.iface.removeToolBarIcon(action)

    def methodChange(self):
        """Signal when method changed"""
        if self.dlg.methodComboBox.currentIndex() == 2:
            self.dlg.mergeCenterCheck.setChecked(False)
            self.dlg.mergeCenterCheck.setEnabled(True)
            self.dlg.lineEditTreshold.setEnabled(False)
            self.dlg.nnRadiusEdit.setEnabled(False)
        elif self.dlg.methodComboBox.currentIndex() == 0:
            self.dlg.mergeCenterCheck.setChecked(False)
            self.dlg.mergeCenterCheck.setEnabled(False)
            self.dlg.lineEditTreshold.setEnabled(True)
            self.dlg.nnRadiusEdit.setEnabled(False)
        elif self.dlg.methodComboBox.currentIndex() == 1:
            self.dlg.mergeCenterCheck.setChecked(True)
            self.dlg.mergeCenterCheck.setEnabled(False)
            self.dlg.lineEditTreshold.setEnabled(True)
            self.dlg.nnRadiusEdit.setEnabled(True)

    def resultPreview(self):
        """Activate preview section

        This method will called if calculation process is finished

        See Also
        ----------
            refreshPreview()
            SimilarityPluginDialog.widgetCanvas
            SimilarityPluginDialog.nextBtn
            SimilarityPluginDialog.previousBtn
            SimilarityPluginDialog.removeBtn

        """
        self.previewLayer = 0
        self.refreshPreview()

        self.dlg.widgetCanvas.enableAntiAliasing(True)

        self.dlg.nextBtn.setEnabled(True)
        self.dlg.previousBtn.setEnabled(True)
        self.dlg.removeBtn.setEnabled(True)

    def attrPrinter(self, fieldsList:object, feature:QgsFeature, place:QTextEdit):
        """print the attribute table on preview panel

        :param fieldsList object: List the attribute value of feature
        :param feature QgsFeature: The feature will be printed
        :param place QTextEdit: The place for editing text
        
        """
        temp = ''

        for f in fieldsList:
            temp += f.name()
            temp += ' : '
            temp += str(feature.attribute(f.name()))
            temp += '\n' 
        # print(place)
        place.setText(temp)

    def refreshPreview(self):
        """refreshing canvas on preview"""
        if len(self.similarLayer) > 0 :
            # set the layer
            self.layerCanvas = QgsVectorLayer("Polygon?crs=ESPG:4326",'SimilarityLayer','memory')
            self.layer2Canvas = QgsVectorLayer("Polygon?crs=ESPG:4326",'SimilarityLayer','memory')

            # set the feature
            # print(self.layer.getFeature(self.similarLayer[self.previewLayer][0]).attributes())
            # print(self.layer2.getFeature(self.similarLayer[self.previewLayer][1]).attributes())
            previewLayerFeature = self.calcTask.getLayersDup()[0].getFeature(self.similarLayer[self.previewLayer][0])
            previewLayerFeature2 = self.calcTask.getLayersDup()[1].getFeature(self.similarLayer[self.previewLayer][1])

            # set the label score
            scoreLabel = "Score : " + str(self.similarLayer[self.previewLayer][2])
            
            # show distance if the layer merge centered (NN and WK only)
            if(self.dlg.methodComboBox.currentIndex() == 1 or self.dlg.methodComboBox.currentIndex() == 2 ) :
                distance = QgsGeometry.distance(
                            previewLayerFeature.geometry().centroid(), previewLayerFeature2.geometry().centroid()
                        )
                if distance < 0.00001:
                    distance = 0
                self.dlg.labelScore.setText(scoreLabel+ " - Distance : "+str(
                        round(distance, 4)
                    )
                )
            else:
                self.dlg.labelScore.setText(scoreLabel)

            self.attrPrinter(self.calcTask.getLayersDup()[0].dataProvider().fields().toList(), previewLayerFeature, self.dlg.previewAttr)
            self.attrPrinter(self.calcTask.getLayersDup()[1].dataProvider().fields().toList(), previewLayerFeature2, self.dlg.previewAttr_2)


            self.layerCanvas.dataProvider().addFeature(previewLayerFeature)
            
            # self.dlg.consoleTextEdit.setText(self.dlg.consoleTextEdit.toPlainText()+"\n\n feature added count : \n "+str(
            #        self.layerCanvas.featureCount()
            #     ))
            
            # translating preview 
            if self.calcTask.getTranslate():
                tGeom = self.calcTask.translateCenterGeom(
                    previewLayerFeature2.geometry(),
                    previewLayerFeature.geometry()
                )
                nFeat = QgsFeature(previewLayerFeature2)
                nFeat.setGeometry(tGeom)
                self.layer2Canvas.dataProvider().addFeature(nFeat)
            else:
                self.layer2Canvas.dataProvider().addFeature(previewLayerFeature2)
            
            # self.dlg.consoleTextEdit.setText(self.dlg.consoleTextEdit.toPlainText()+"\n\n feature2 added count : \n "+str(
            #         self.layer2Canvas.featureCount()
            #     ))

            # set canvas to preview feature layer
            self.dlg.widgetCanvas.setExtent(previewLayerFeature.geometry().boundingBox(), True)
            
            self.dlg.widgetCanvas.setDestinationCrs(self.layerCanvas.sourceCrs())
            
            # self.canvas.setDestinationCrs(self.layerCanvas.sourceCrs())
            # self.canvas.setExtent(self.layerCanvas.extent())

            symbol = self.layerCanvas.renderer().symbol()
            symbol.setColor(QColor(0,147,221,127))

            symbol2 = self.layer2Canvas.renderer().symbol()
            symbol2.setColor(QColor(231,120,23,127))

            self.dlg.widgetCanvas.setLayers([self.layer2Canvas, self.layerCanvas])

            # redraw the canvas
            self.dlg.widgetCanvas.refresh()

    def nextPreview(self):
        """Next preview signal for next button in preview section"""
        # f2 = open("engine/f2.txt", "w")
        if(self.previewLayer+1 < len(self.similarLayer)
            ):
            self.previewLayer = self.previewLayer+1
        # self.dlg.consoleTextEdit.setText(self.dlg.consoleTextEdit.toPlainText()+"\n\n Current Similar Layer Index : \n  "+str([self.similarLayer[self.previewLayer], self.previewLayer]))
        self.refreshPreview()

    def previousPreview(self):
        """Previous preview signal"""
        if(self.previewLayer-1 > -1):
            self.previewLayer = self.previewLayer-1
        # self.dlg.consoleTextEdit.setText(self.dlg.consoleTextEdit.toPlainText()+"\n\n Current Similar Layer Index : \n  "+str([self.similarLayer[self.previewLayer], self.previewLayer]))
        self.refreshPreview()

    def rmFeatResult(self):
        """Removing similarity info current result"""
        self.similarLayer.pop(self.previewLayer)
        if(self.previewLayer > len(self.similarLayer)):
            self.previewLayer = len(self.similarLayer-1)
        self.refreshPreview()
        self.warnDlg.close()

    def rmWarn(self):
        """prevention remove item preview"""
        self.warnDlg = self.warnDialogInit('Are you sure to delete this feature ?')
        self.warnDlg.yesBtn.clicked.connect(self.rmFeatResult)
        self.warnDlg.noBtn.clicked.connect(self.warnDlg.close)
        self.warnDlg.show()

    def updateCalcProgress(self, value):
        """Progress signal for calcTask"""
        self.dlg.progressBar.setValue(int(round(value,1)))

    def updateSimList(self, simList:list):
        """Updating similiarity result signal"""
        self.similarLayer.append(simList)
        cText = "Number of Result: "+str(len(self.similarLayer))
        self.dlg.counterLabel.setText(cText)

    # thread signal
    def errorCalcThread(self, value:str):
        """Signal when an error occured"""
        print("error : ", value)
        self.simpleWarnDialogInit(value)
        self.dlg.calcBtn.setEnabled(True)
        self.dlg.stopBtn.setEnabled(False)

    def setLayers(self, layers:list):
        """Set the layers
        
        :param layers list: List of layers
        
        """
        self.layer = layers[0]
        self.layer2 = layers[1]

    def finishedCalcThread(self, itemVal:list):
        """signal when calcTask calculation is finished

        :param itemVal list: the returned value emit
        
        """
        # print("finished returned : ", itemVal)
        # self.similarLayer = itemVal
        self.setLayers(self.calcTask.getLayersDup())
        self.calcThread.terminate()
        self.calcTask.kill()
        cText = "Number of Result: "+str(len(self.similarLayer))
        if len(self.similarLayer) > 0 :
            # self.addScoreItem()
            self.previewLayer = 0
            self.dlg.saveBtn.setEnabled(True)
            self.dlg.counterLabel.setText(cText)
            self.resultPreview()
        else:
            self.previewLayer = 0
            self.dlg.counterLabel.setText(cText)
        self.dlg.calcBtn.setEnabled(True)
        self.dlg.stopBtn.setEnabled(False)

    def stopCalcThread(self):
        """Signal when calcTask is stopped """
        self.calcThread.terminate()
        self.calcTask.kill()
        if(self.calcTask.getLayersDup()[0].featureCount() > 0 and self.calcTask.getLayersDup()[1].featureCount() > 0):
            self.layer = self.calcTask.getLayersDup()[0]
            self.layer2 = self.calcTask.getLayersDup()[1]
            cText = "Number of Result: "+str(len(self.similarLayer))
            if len(self.similarLayer) > 0 :
                # self.addScoreItem()
                self.previewLayer = 0
                self.dlg.saveBtn.setEnabled(True)
                self.dlg.counterLabel.setText(cText)
                self.resultPreview()
            else:
                self.previewLayer = 0
                self.dlg.counterLabel.setText(cText)
            self.dlg.calcBtn.setEnabled(True)
            self.dlg.stopBtn.setEnabled(False)

    def eventCalcThread(self, value:str):
        """Receiving signal event
        
        :param value str: the returned value emit
        
        """
        self.dlg.eventLabel.setText("Event: "+value)

    # executing calculation
    def calculateScore(self):
        """Signal for executing calculation for cheking maps"""
        if(isinstance(self.dlg.layerSel1.currentLayer(), QgsVectorLayer) and isinstance(self.dlg.layerSel1.currentLayer(), QgsVectorLayer)):
            # set plugin to initial condition
            self.dlg.progressBar.setValue(0)
            self.dlg.saveBtn.setEnabled(False)
            self.dlg.nextBtn.setEnabled(False)
            self.dlg.previousBtn.setEnabled(False)
            self.dlg.removeBtn.setEnabled(False)
            self.dlg.widgetCanvas.setLayers([
                    QgsVectorLayer("Polygon?crs=ESPG:4326",'SimilarityLayer','memory')
                ])
            self.dlg.previewAttr.setText("")
            self.dlg.previewAttr_2.setText("")
            self.dlg.widgetCanvas.refresh()
            scoreLabel = "Score : 0"
            self.dlg.labelScore.setText(scoreLabel)
            self.similarLayer = []
            
            # set input-output option
            self.calcTask.setLayers(self.dlg.layerSel1.currentLayer(), self.dlg.layerSel2.currentLayer())
            self.calcTask.setTreshold(self.dlg.lineEditTreshold.value())
            self.calcTask.setMethod(int(self.dlg.methodComboBox.currentIndex()))
            self.calcTask.setTranslate(self.dlg.mergeCenterCheck.isChecked())
            self.calcTask.setRadius(self.dlg.nnRadiusEdit.value())
            self.calcTask.setSuffix(str(self.dlg.sufLineEdit.text()))
            self.calcTask.setScoreName(str(self.dlg.attrOutLineEdit.text()))
            # print("input option set")
            # activating task
            self.calcTask.alive()
            # print("task alive")
            self.calcThread.start()
            # print("thread started")

            # set button
            self.dlg.calcBtn.setEnabled(False)
            self.dlg.stopBtn.setEnabled(True)
        else:
            # prevention on QgsVectorLayer only
            self.simpleWarnDialogInit("This plugin support Vector Layer only")

    # signal when saveBtn clicked
    def registerToProject(self):
        """Signal to registering project"""
        QgsProject.instance().addMapLayers(self.calcTask.getLayersResult())

    # warning dialog for error or prevention
    def warnDialogInit(self, msg:str):
        """This dialog have Yes and No button.
        
        :param msg: str Display the warning message 
        
        """

        dialog = WarnDialog()
        #set the message
        dialog.msgLabel.setText(msg)
        return dialog

    # initializing simple warning dialog
    def simpleWarnDialogInit(self, msg:str):
        """ This dialog have ok button only
        
        :param: msg str: Display the warning message 
        
        """
        
        # Set the message
        self.simpleDialog.msgLabel.setText(msg)
        self.simpleDialog.show()
        
    def run(self):
        """Run method that performs all the real work"""
        
        # print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        # init run variable
        # self.canvas = QgsMapCanvas()
        
        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:    
            self.previewLayer = 0
            self.currentCheckLayer = [0,0]
            self.first_start = False
            self.dlg = SimilarityPluginDialog()
            self.simpleDialog = SimpleWarnDialog()
        # set help documentation
        self.dlg.helpTextBrowser.setSource(
            QUrl.fromLocalFile(
                os.path.join(os.path.dirname(__file__), "help", "build","index.html")
            )
        )
        self.dlg.nextHelpBtn.clicked.connect(self.dlg.helpTextBrowser.forward)
        self.dlg.previousHelpBtn.clicked.connect(self.dlg.helpTextBrowser.backward)
        # filtering selection layer (empty layer not allowed)
        self.dlg.layerSel1.setAllowEmptyLayer(False)
        self.dlg.layerSel1.setAllowEmptyLayer(False)

        # method combobox initialiazation
        self.dlg.methodComboBox.clear()
        self.dlg.methodComboBox.addItems(
            [
                'Squential',
                'Nearest Neightbour',
                'Wilkerstat BPS'
            ]
        )

        # registering signal

        self.dlg.methodComboBox.currentIndexChanged.connect(self.methodChange)
        
        self.dlg.nextBtn.clicked.connect(self.nextPreview)
        self.dlg.previousBtn.clicked.connect(self.previousPreview)

        self.dlg.calcBtn.clicked.connect(self.calculateScore)

        self.dlg.saveBtn.clicked.connect(self.registerToProject)

        self.dlg.removeBtn.clicked.connect(self.rmWarn)

        self.dlg.stopBtn.clicked.connect(self.stopCalcThread)

        # intialize pan tool
        panTool = QgsMapToolPan(self.dlg.widgetCanvas)
        # set signal
        panTool.setAction(self.actionPan)
        # set map tool
        self.dlg.widgetCanvas.setMapTool(panTool)
        # set pan tool to be activate
        panTool.activate()

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            self.similarLayer = []
            self.dlg.widgetCanvas.setLayers([
                    QgsVectorLayer("Polygon?crs=ESPG:4326",'SimilarityLayer','memory')
                ])
            self.dlg.previewAttr.setText("")
            self.dlg.previewAttr_2.setText("")
            self.dlg.widgetCanvas.refresh()
            scoreLabel = "Score : 0"
            self.dlg.labelScore.setText(scoreLabel)
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            

    # manipulating geom
    # def translateCenterGeom(self, g:QgsGeometry, target:QgsGeometry):
    #     """
    #         :param: g QgsGeometry
    #             The geometry will be translated
    #         :param: target QgsGeometry
    #             Destination
    #     """
    #     # duplicate geometry due to data integrity
    #     g_new = QgsGeometry(g)
    #     target_new = QgsGeometry(target)
    #     c = target_new.centroid().asQPointF()
    #     c2 = g_new.centroid().asQPointF()
    #     transX = c.x() - c2.x()
    #     transY = c.y() - c2.y()
    #     g.translate(transX, transY)
    #     return g

    # calculating score between two geometry
    # def calcMapCurvesGeom(self, g:QgsGeometry, g2:QgsGeometry):
    #     """
    #         :param: feature QgsGeometry
    #             First geometry will be checked
    #         :param: feature2 QgsGeometry
    #             Second geometry will be checked
    #     """
    #     inter = g.intersection(g2)
    #     if(inter.isEmpty()):
    #         return 0
    #     else:
    #         score = (inter.area()/g.area())*(inter.area()/g2.area())
    #         return round(score, 4)
 
    # calculating the score between two feature and store it to list : self.similarityList
    # def calcMapCurves(self, feature:QgsFeature, feature2:QgsFeature):
    #     """
    #         :param: feature QgsFeature
    #             First feature will be checked
    #         :param: feature2 QgsFeature
    #             Second feature will be checked
    #     """
    #     # make treshold to decimal
    #     treshold = self.dlg.lineEditTreshold.value()/100

    #     if self.dlg.methodComboBox.currentIndex() == 1:
    #         score = self.calcMapCurvesGeom(
    #                     feature.geometry(),
    #                     self.translateCenterGeom(feature2.geometry(),feature.geometry()) 
    #                 )
    #     else:
    #         score = self.calcMapCurvesGeom(feature.geometry(), feature2.geometry())

    #     # print("score : "+str(score)+" treshold : "+str(self.dlg.lineEditTreshold.value()/100))

    #     if score >= treshold and treshold > 0:
    #         self.similarLayer.append([feature.id(), feature2.id(), score])

    # wilkerstat mechanism
    # def calculateWK(self, layer:QgsVectorLayer, layer2:QgsVectorLayer):
    #     """
    #         :param: layer QgsVectorLayer
    #             First layer will be checked
    #         :param: layer2 QgsVectorLayer
    #             Second layer will be checked
    #     """
    #     print("WK method")
    #     # start = timer()

    #     attrName = layer.dataProvider().fields().names()
    #     attrName2 = layer2.dataProvider().fields().names()
        
    #     # pkCheck = self.wilkerstatPKExist(layer, layer2)

    #     for i in layer.getFeatures():
    #         # Querying for matching attribute 
            
    #         que = QgsQueryBuilder(layer2)
            
    #         queText = ""
    #         try:
    #             if("PROVNO" in attrName2):
    #                 queText += '"PROVNO"' + " LIKE '"
    #                 if("PROVNO" in attrName):
    #                     queText += i.attribute("PROVNO")
    #                 else:
    #                     queText += i.attribute("provno")
    #             else:
    #                 queText += '"provno"' + " LIKE '"
    #                 if("PROVNO" in attrName):
    #                     queText += i.attribute("PROVNO")
    #                 else:
    #                     queText += i.attribute("provno")
                
    #             if ("KABKOTNO" in attrName2):
    #                 queText += "'"+' AND "KABKOTNO" ' + " LIKE '"
    #                 if ("KABKOTNO" in attrName):
    #                     queText += i.attribute("KABKOTNO")
    #                 else:
    #                     queText += i.attribute("kabkotno")
    #             else:
    #                 queText += "'"+' AND "kabkotno" ' + " LIKE '"
    #                 if ("KABKOTNO" in attrName):
    #                     queText += i.attribute("KABKOTNO")
    #                 else:
    #                     queText += i.attribute("kabkotno")
                
    #             if ("KECNO" in attrName2):
    #                 queText += "'"+' AND "KECNO" ' + "LIKE '"
    #                 if ("KECNO" in attrName):
    #                     queText += i.attribute("KECNO")
    #                 else:
    #                     queText += i.attribute("kecno")
    #             else:
    #                 queText += "'"+' AND "kecno" ' + "LIKE '"
    #                 if ("KECNO" in attrName):
    #                     queText += i.attribute("KECNO")
    #                 else:
    #                     queText += i.attribute("kecno")
                
    #             if ('DESANO' in attrName2):
    #                 queText += "'"+' AND "DESANO" ' + "LIKE '"
    #                 if('DESANO' in attrName):
    #                     queText += i.attribute("DESANO")+"' "
    #                 else:
    #                     queText += i.attribute("desano")+"' "
    #             else:
    #                 queText += "'"+' AND "desano" ' + "LIKE '"
    #                 if('DESANO' in attrName):
    #                     queText += i.attribute("DESANO")+"' "
    #                 else:
    #                     queText += i.attribute("desano")
                
    #             queText += "' "
                
    #             que.clear()
    #             que.setSql(queText)
    #             que.accept()

    #             if layer2.featureCount() > 0:
    #                 if self.dlg.mergeCenterCheck.isChecked():
    #                     for j in layer2.getFeatures():
    #                         score = self.calcMapCurvesGeom(
    #                             i.geometry(),
    #                             self.translateCenterGeom(i.geometry(), j.geometry())
    #                         )
    #                         self.similarLayer.append([i.id(),j.id(), score])
    #                 else:
    #                     for j in layer2.getFeatures(): 
    #                         score = self.calcMapCurvesGeom(
    #                             i.geometry(), j.geometry()
    #                         )
    #                         if(score > -1):
    #                             self.similarLayer.append([i.id(),j.id(), score])

    #             que.clear()
    #             que.accept()
    #         except KeyError as identifier:
    #             # show error message
    #             warnDlg = self.simpleWarnDialogInit("It might be not Wilkerstat, PROVNO, KABKOTNO, KECNO, DESANO is required") 

    # squential mechanism
    # def calculateSq(self, layer:QgsVectorLayer, layer2:QgsVectorLayer):
    #     """
    #         :param: layer QgsVectorLayer
    #             First layer will be checked
    #         :param: layer2 QgsVectorLayer
    #             Second layer will be checked
    #     """
    #     # print("layer 1 count : "+str(layer.featureCount()))
    #     # print("layer 2 count : "+str(layer2.featureCount()))
    #     print("Squential Method")
    #     for i in layer.getFeatures():
    #         for j in layer2.getFeatures(i.geometry().boundingBox()):
    #             self.calcMapCurves(i, j)

    # # knn mechanism            
    # def calculateKNN(self, layer:QgsVectorLayer, layer2:QgsVectorLayer):
    #     """
    #         :param: layer QgsVectorLayer
    #             First layer will be checked
    #         :param: layer2 QgsVectorLayer
    #             Second layer will be checked
    #     """

    #     for i in layer.getFeatures() :
    #         if(i.hasGeometry()):
    #             # making bounding box
    #             centroid = i.geometry().centroid().asQPointF()
    #             bbFilter = QgsRectangle(
    #                 centroid.x()-self.dlg.nnRadiusEdit.value(),
    #                 centroid.y()-self.dlg.nnRadiusEdit.value(),
    #                 centroid.x()+self.dlg.nnRadiusEdit.value(),
    #                 centroid.y()+self.dlg.nnRadiusEdit.value()
    #             )
    #             # iterating in boundingbox only
    #             for j in layer2.getFeatures(bbFilter):
    #                 self.calcMapCurves(i, j)

    # cloning layer (better performance on WK)
    # def duplicateLayer(self, currentLayer:QgsVectorLayer, suffix:str, scoreName:str):
    #     """
    #         :param: currentLayer
    #             The layer will be duplicated
    #         :param: suffix str
    #             Suffix name
    #         :param: scoreName
    #             Attribute name of score in attribute table
    #     """
    #     layername = str(currentLayer.name())+"_"+str(suffix)
    #     layer = QgsVectorLayer("Polygon?crs=ESPG:4326",
    #                     layername,
    #                     'memory')
    #     layer.setCrs(
    #         currentLayer.sourceCrs()
    #     )
    #     layer.dataProvider().addAttributes(
    #         currentLayer.dataProvider().fields().toList()
    #     )
    #     # adding score attributes info
    #     layer.dataProvider().addAttributes(
    #         [
    #             QgsField(scoreName, QVariant.Double),
    #             QgsField('id', QVariant.Int),
    #             QgsField('match', QVariant.Int)
    #         ]
    #     )
    #     # update the fields
    #     layer.updateFields()
    #     layer.dataProvider().addFeatures(
    #         [f for f in currentLayer.getFeatures()]
    #     )

    #     return layer

     # def addScoreItem(self):
    #     """save score item into the clone layer"""
    #     self.layer.commitChanges()
    #     self.layer2.commitChanges()

    #     scoreFieldIndex = self.layer.dataProvider().fieldNameIndex(self.dlg.attrOutLineEdit.text())
    #     scoreFieldIndex2 = self.layer2.dataProvider().fieldNameIndex(self.dlg.attrOutLineEdit.text())

    #     idIndex = self.layer.dataProvider().fieldNameIndex('id')
    #     idIndex2 = self.layer2.dataProvider().fieldNameIndex('id')

    #     matchIndex = self.layer.dataProvider().fieldNameIndex('match')
    #     matchIndex2 = self.layer2.dataProvider().fieldNameIndex('match')

    #     self.layer.startEditing()
    #     self.layer2.startEditing()

    #     for sim in self.similarLayer:
    #         self.layer.changeAttributeValue(sim[0], scoreFieldIndex, sim[2])
    #         self.layer.changeAttributeValue(sim[0], idIndex, sim[0])
    #         self.layer.changeAttributeValue(sim[0], matchIndex, sim[1])
    #         self.layer2.changeAttributeValue(sim[1], scoreFieldIndex2, sim[2])
    #         self.layer2.changeAttributeValue(sim[1], idIndex2, sim[1])
    #         self.layer2.changeAttributeValue(sim[1], matchIndex2, sim[0])

    #     self.layer.commitChanges()
    #     self.layer2.commitChanges()  