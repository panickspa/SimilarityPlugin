Plugin Dialog Interaction
=========================

.. toctree::
   :maxdepth: 2

Input section
------------------------------
   methodChange(self)

      change on interaction method combobox


Preview section
-------------------------------
   resultPreview(self)

      Activate preview section

   attrPrinter(self, fieldList:object, feature:QgsFeature, place:QTextEdit)

      Print atrribute info on text edit in preview section

   refreshPreview(self)

      redraw Canvas preview

   nextPreview(self)

      next result features

   nextPrevious(self)

      previous result features

   rmFeatResult(self)

      Remove the current result

   rmWarn(self)

      Warning dialog to prevent accidentally remove result

Action section
-------------------------------
   addScoreItem(self)

      adding result score

   calculateDialogAccepted(self)

      Interaction when self.dialogCalc accepted

   calculateClicked(self)

      interaction when self.dlg.calcBtn clicked


   calculateDialogRejected(self)

       Interaction when self.dialogCalc rejected

   registerToProject(self)

      Interaction when saveBtn clicked