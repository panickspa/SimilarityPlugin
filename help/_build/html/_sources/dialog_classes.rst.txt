Plugin Dialog Classes
=====================

CalcDialog
----------

    msgLabel  : QLabel

    msgLabel2 : QLabel

    buttonBox : QDialogButton


SimilarityPlugin
-----------------

    dlg : SimilarityPluginDialog
    
    dialogCalc : CalcDialog

    similarLayer : list=[]

    previewLayer : int=0

SimilarityPluginDialog
----------------------
    attrOutlineEdit : QLineEdit

    calcBtn : QPushButton

    layerSel1 : QgsMapComboBox
    
    layerSel2 : QgsMapComboBox

    lineEditTreshold : QDoubleSpinBox 

    mainTab   : QWidget

    mergeCenterCheck : QCheckBox

    methodComboBox : QCheckBox

    nextBtn : QPushButton

    nnRadiusEdit : QDoubleSpinBox

    prefLineEdit  : QLineEdit

    previewAttr : QLineEdit

    previewAttr_2 : QLineEdit

    SimilarityPluginDialogBase : QDialog

    tabWidget : QTabWidget

    widgetCanvas : QgsMapCanvas

WarnDialog
----------------------
    msgLabel : QLabel

    noBtn : QPushButton

    yesBtn : QPushButton
