==========================
Plugin Dialog Interaction
==========================
Interaction method is stored in SimilarityPlugin Class as its method

.. toctree::
   :maxdepth: 2

Input section
------------------------------
   .. py:attribute:: methodChange(self)

      Change on interaction method combobox


Preview section
-------------------------------
   .. py:attribute:: resultPreview(self)

      Activate preview section

   .. py:attribute:: attrPrinter(self, fieldList:object, feature:QgsFeature, place:QTextEdit)

      Print feature atrribute info on text edit in preview section

      :param object fieldList: Iterable field value object
      :param QgsFeature feature: The feature will be printed
      :param QTextEdit place: The place atrribute will be printed

   .. py:attribute:: refreshPreview(self)

      redraw Canvas preview

   .. py:attribute:: nextPreview(self)

      next result features

   .. py:attribute:: nextPrevious(self)

      previous result features

   .. py:attribute:: rmFeatResult(self)

      Remove the current result

   .. py:attribute:: rmWarn(self)

      Warning dialog to prevent accidentally remove result

Action section
-------------------------------
   .. py:attribute:: addScoreItem(self)

      Adding result score

   .. py:attribute:: calculateDialogAccepted(self)

      Interaction when self.dialogCalc accepted

   .. py:attribute:: calculateClicked(self)

      Interaction when self.dlg.calcBtn clicked


   .. py:attribute:: calculateDialogRejected(self)

       Interaction when self.dialogCalc rejected

   .. py:attribute:: registerToProject(self)

      Interaction when self.dlg.saveBtn clicked