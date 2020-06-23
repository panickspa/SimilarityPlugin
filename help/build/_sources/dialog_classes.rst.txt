==============================
Plugin Classes
==============================
All attribute in this plugin dialog and object classes

Class: CalcDialog
-----------------

    .. py:data:: msgLabel  
      :type: QLabel

        First line message in dialog

    .. py:data:: msgLabel2 
      :type: QLabel

        Second line message in dialog

    .. py:data:: buttonBox 
      :type: QDialogButton

        Button dialog to accept and reject the condition on the message

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

    .. py:attribute:: calcMapCurvesGeom (self, g:QgsGeometry, g2:QgsGeometry)
         
      Calculate the score between the geometry in float number using GOF Mapcurves (Hargrove et al. 2006)
      
      :param SimilarityPlugin self: class parent
      :param QgsGeometry g: first geometry will be checked
      :param QgsGeometry g2: second geometry will be checked
      :return: float

    .. py:attribute:: calcMapCurves (self, feature:QgsFeature, feature2:QgsFeature)
         
      Calculate the score and save to self.similarLayer. Score saved in float number using GOF Mapcurves (Hargrove et al. 2006)
      
      :param SimilarityPlugin self: class parent
      :param QgsFeature feature: first feature will be checked
      :param QgsFeature feature2: second feature will be checked
      :return: null

    .. py:attribute:: calcSq (self, layer:QgsVectorLayer, layer2:QgsVectorLayer)
         
      Checking similarity between two layer with squential method
      
      :param SimilarityPlugin self: class parent
      :param QgsVectorLayer layer: first layer will checked
      :param QgsVectorLayer layer2: second layer will checked
      :return: null

    .. py:attribute:: calcKNN (self, layer:QgsVectorLayer, layer2:QgsVectorLayer)
         
      Check each feature between 2 layer within radius bounding box. Radius distance using euclidean.

      :param SimilarityPlugin self: class parent
      :param QgsVectorLayer layer: first layer will checked
      :param QgsVectorLayer layer2: second layer will checked
      :return: null

    .. py:attribute:: calcWK (self, layer:QgsVectorLayer, layer2:QgsVectorLayer)
         
      Match each feature the primary key in map, see https://sig.bps.go.id/

      :param SimilarityPlugin self: class parent
      :param QgsVectorLayer layer: first layer will checked
      :param QgsVectorLayer layer2: second layer will checked
      :return: null

    .. py:attribute:: translateCenterGeom (self, g:QgsGeometry, target:QgsGeometry)

      Translate first geometry to the center of target geometry

      :param SimilarityPlugin self: class parent
      :param QgsVectorLayer layer: first layer will checked
      :param QgsVectorLayer layer2: second layer will checked
      :return: QgsGeometry

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