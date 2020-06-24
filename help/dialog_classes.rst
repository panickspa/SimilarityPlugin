==============================
Plugin Classes
==============================
All attribute in this plugin dialog and object classes

CalculationModule
------------------------

    .. py:data:: killed
      :type: boolean

        Statement of task is being killed or not

    .. py:data:: layer
      :type: QgsVectorLayer

        First original layer 

    .. py:data:: layerDup
      :type: QgsVectorLayer

        Clone of the first layer and the first result layer for calculation

    .. py:data:: layer2
      :type: QgsVectorLayer

        Second original layer

    .. py:data:: layer2Dup
      :type: QgsVectorLayer

        Clone of the second layer and the second result layer for calculation

    .. py:data:: method 
      :type: int
    
      Selected method index
    
    .. py:data:: radius 
      :type: float

      Radius for NN method

    .. py:data::similarLayer 
      :type: list=[]

      Result of similarity calculation, Zero index is the first feature id in first layer, First index is the second feature id in second layer, Third index is the score of similarity

    .. py:data:: suffix 
      :type: str

      Suffix for Cloned layer name

    .. py:data:: scoreName
    :type: str

      Attribute name for reserving score information in cloned layer

    .. py:data:: translate 
      :type: bool

      Statement for checking method is translated or not for Wilkerstat method

    .. py:data::treshold 
      :type: float
    

    .. py:attribute:: setTreshold(self, treshold:float)
      
      Set threshold option

      :param float treshold: determined treshold
      :return: None

    .. py:atrribute:: setLayers(self, layer:QgsVectorLayer, layer2:QgsVectorLayer)

      Set the original layers

      :param QgsVectorLayer layer: The first original layer 
      :param QgsVectorLayer layer2: The second original layer 
      :return: None

    .. py:atrribute:: setMethod(self, method:int)

      Set method attribute

      :param int method: Selected method index
      :return: None

    .. py:atrribute:: setTranslate(self, translate:bool)

      Set translate attribute

      :param bool translate: Translate Statement
      :return: None

    .. py:atrribute:: setRadius(self, radius:float)

      Set the radius attribute

      :param float radius: Determined radius from user
      :return: None

    .. py:atrribute: setSuffix(self, suffix:str)

      Set suffix attribute

      :param str suffix: suffix name for duplicated layer

    .. py:atrribute: setScoreName(self, scoreName)

      Set scoreName attribute

      :param str suffix: socre name attribute for duplicated layer

    .. py:atrribute:: getSimilarLayer(self)

      get similar layer result list

      :return: list self.similarLayer: The list

    .. py:atrribute::getLayers(self)

      get the original layer

      :return: list [self.layer, self.layer2]: The list

    .. py:atrribute:: getLayersDup(self)

      get duplicated layer

      :return: list [self.layerDup, self.layer2Dup]: The list

    .. py:atrribute:: setLayer(self, layer:QgsVectorLayer, layer2:QgsVectorLayer)

      Set the original layers

      :param QgsVectorLayer layer: The first layer
      :param QgsVectorLayer layer2: The second layer
      :return: None

    .. py:atrribute:: duplicateLayer(self, currentLayer:QgsVectorLayer, suffix:str, scoreName:str)

      Duplicating layer and stored to temporary layer

      :param QgsVectorLayer currentLayer: Layer target
      :param str suffix: suffix name layer
      :param str scoreName: score name attribute in layer
      :return: QgsVectorLayer

    .. py:attribute:: calcMapCurvesGeom (self, g:QgsGeometry, g2:QgsGeometry)
         
      Calculate the score between the geometry in float number using GOF Mapcurves (Hargrove et al. 2006)
      
      :param QgsGeometry g: first geometry will be checked
      :param QgsGeometry g2: second geometry will be checked
      :return: float

    .. py:attribute:: calcMapCurves (self, feature:QgsFeature, feature2:QgsFeature)
         
      Calculate the score and save to self.similarLayer. Score saved in float number using GOF Mapcurves (Hargrove et al. 2006)
      
      :param QgsFeature feature: first feature will be checked
      :param QgsFeature feature2: second feature will be checked
      :return: None

    .. py:attribute:: calcSq (self, layer:QgsVectorLayer, layer2:QgsVectorLayer)
         
      Checking similarity between two layer with squential method
      
      :param QgsVectorLayer layer: first layer will checked
      :param QgsVectorLayer layer2: second layer will checked
      :return: None

    .. py:attribute:: calcKNN (self, layer:QgsVectorLayer, layer2:QgsVectorLayer)
         
      Check each feature between 2 layer within radius bounding box. Radius distance using euclidean.

      :param QgsVectorLayer layer: first layer will checked
      :param QgsVectorLayer layer2: second layer will checked
      :return: None

    .. py:attribute:: calcWK (self, layer:QgsVectorLayer, layer2:QgsVectorLayer)
         
      Match each feature the primary key in map, see https://sig.bps.go.id/

      :param QgsVectorLayer layer: first layer will checked
      :param QgsVectorLayer layer2: second layer will checked
      :return: None

    .. py:attribute:: translateCenterGeom (self, g:QgsGeometry, target:QgsGeometry)

      Translate first geometry to the center of target geometry

      :param QgsVectorLayer layer: first layer will checked
      :param QgsVectorLayer layer2: second layer will checked
      :return: QgsGeometry
    

Class: SimilarityPlugin
------------------------

    .. py:data:: dlg
      :type: SimilarityPluginDialog

        Main plugin dialog
    
    .. py:data:: dialogCalc
      :type: CalcDialog

        Caution dialog to convincing the user of large data checking

    .. py:data:: similarLayer
      :type: list=[]

        The result of calculation process

    .. py:data:: previewLayer
      :type: int=0

        Current index similarLayer that previewed in canvas
    
    .. py:data:: resultPreview(self)

      Activate preview section

        *See also*

          .. py:attribute:: refreshPreview(self)
          .. py:data:: CalcDialog.widgetCanvas 
            :type: QgsMapCanvas
          .. py:data:: CalcDialog.nextBtn 
            :type: QPushButton
          .. py:data:: CalcDialog.previousBtn 
            :type: QPushButton
          .. py:data:: CalcDialog.removeBtn 
            :type: QPushButton

    .. py:attribute:: attrPrinter(self, fieldList:object, feature:QgsFeature, place:QTextEdit)

      Print feature atrribute info on text edit in preview section

      :param object fieldList: Iterable field value object
      :param QgsFeature feature: The feature will be printed
      :param QTextEdit place: The place atrribute will be printed

    .. py:attribute:: refreshPreview(self)

      Redraw canvas preview and reprint the attribute value based on current preview.

         *See also*

          .. py:attribute:: attrPrinter(self, fieldList:object, feature:QgsFeature, place:QTextEdit)

    .. py:attribute:: nextPreview(self)

      next result features

    .. py:attribute:: nextPrevious(self)

      previous result features

    .. py:attribute:: rmFeatResult(self)

      Remove the current result

    .. py:attribute:: rmWarn(self)

      Warning dialog to prevent accidentally remove result

    .. py:attribute:: addScoreItem(self)

      Adding result score

    .. py:attribute:: calculateDialogAccepted(self)

      Interaction when self.dialogCalc accepted

    .. py:attribute:: calculateClicked(self)

      Interaction when self.dlg.calcBtn clicked

    .. py:attribute:: methodChange(self)

      Change on interaction method combo box

    .. py:attribute:: calculateDialogRejected(self)

      Interaction when self.dialogCalc rejected

    .. py:attribute:: registerToProject(self)

      Interaction when self.dlg.saveBtn clicked

    .. py:attribute:: finishedCalcThread(self, itemVal)

      Signal when calc worker finished

    .. py:attribute:: stopCalcThread(self)

      Signal when thread stopped

    .. py:attribute:: errorCalcThread(self)
      
      Signal when thread error


Class: SimilarityPluginDialog
------------------------------
    .. py:data:: attrOutlineEdit 
      :type: QLineEdit

        Inputation interface for attribute name score in attribute table in string (text)

    .. py:data:: calcBtn 
      :type: QPushButton

        Button for exceuting calculation

    .. py:data:: layerSel1 
      :type: QgsMapComboBox

        Combo Box for selecting first layer

    .. py:data:: layerSel2 
      :type: QgsMapComboBox

        Combo Box for selecting second layer

    .. py:data:: lineEditTreshold 
      :type: QDoubleSpinBox 

        Inputation for similarity score treshold in float (number)

    .. py:data:: mainTab   
      :type: QWidget

        Tab for the main menu

    .. py:data:: mergeCenterCheck 
      :type: QCheckBox

        Check box for calculation with centering the geometry to another geometry

    .. py:data:: methodComboBox 
      :type: QCheckBox

        Combo box for selecting the checking similarity method

    .. py:data:: nextBtn 
      :type: QPushButton

        Button for preview the next feature in similarity list result

    .. py:data:: nnRadiusEdit 
      :type: QDoubleSpinBox

        Inputation the radius tolerance (The number is according to the projection unit scale)

    .. py:data:: prefLineEdit  
      :type: QLineEdit

        Inputation for prefix result layer name

    .. py:data:: previewAttr 
      :type: QLineEdit

        Previewing attribute current feature in first layer

    .. py:data:: previewAttr_2 
      :type: QLineEdit

        Previewing attribute current feature in second layer

    .. py:data:: previousBtn 
      :type: QPushButton

        Button for preview the previous feature in similarity list result

    .. py::data:: progressBar
      :type: QProgressBar

        Show the progress calculation

    .. py:data:: SimilarityPluginDialogBase 
      :type: QDialog

        Base plugin window dialog

    .. py:data:: tabWidget 
      :type: QTabWidget

        Tab widget in the plugin

    .. py:data:: widgetCanvas 
      :type: QgsMapCanvas

        Canvas widget in preview section for previewing the result

Class: WarnDialog
----------------------
    .. py:data:: msgLabel 
      :type: QLabel

        The warning message

    .. py:data:: noBtn 
      :type: QPushButton

        Button for reject the condition

    .. py:data:: yesBtn 
      :type: QPushButton

        Button for accept the condition

Class: SimpleWarningDialog
----------------------------

    .. py:data:: msgLabel 
      :type: QLabel

        The warning message

    .. py:data:: okBtn 
      :type: QPushButton

        Ok condition