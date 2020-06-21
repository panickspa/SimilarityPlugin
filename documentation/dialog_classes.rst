==============================
Plugin Classes
==============================
All attribute in this plugin dialog and object classes

Class: CalcDialog
-----------------

    .. py:attribute:: msgLabel  : QLabel

        First line message in dialog

    .. py:attribute:: msgLabel2 : QLabel

        Second line message in dialog

    .. py:attribute:: buttonBox : QDialogButton

        Button dialog to accept and reject the condition on the message

Class: SimilarityPlugin
------------------------

    .. py:attribute:: dlg : SimilarityPluginDialog

        Main plugin dialog
    
    .. py:attribute:: dialogCalc : CalcDialog

        Caution dialog to convincing the user of large data checking

    .. py:attribute:: similarLayer : list=[]

        The result of calculation process

    .. py:attribute:: previewLayer : int=0

        Current index similarLayer that previewed in canvas

Class: SimilarityPluginDialog
------------------------------
    .. py:attribute:: attrOutlineEdit : QLineEdit

        Inputation interface for attribute name score in attribute table in string (text)

    .. py:attribute:: calcBtn : QPushButton

        Button for exceuting calculation

    .. py:attribute:: layerSel1 : QgsMapComboBox

        Combo Box for selecting first layer

    .. py:attribute:: layerSel2 : QgsMapComboBox

        Combo Box for selecting second layer

    .. py:attribute:: lineEditTreshold : QDoubleSpinBox 

        Inputation for similarity score treshold in float (number)

    .. py:attribute:: mainTab   : QWidget

        Tab for the main menu

    .. py:attribute:: mergeCenterCheck : QCheckBox

        Check box for calculation with centering the geometry to another geometry

    .. py:attribute:: methodComboBox : QCheckBox

        Combo box for selecting the checking similarity method

    .. py:attribute:: nextBtn : QPushButton

        Button for preview the next feature in similarity list result

    .. py:attribute:: nnRadiusEdit : QDoubleSpinBox

        Inputation the radius tolerance (The number is according to the projection unit scale)

    .. py:attribute:: prefLineEdit  : QLineEdit

        Inputation for prefix result layer name

    .. py:attribute:: previewAttr : QLineEdit

        Previewing attribute current feature in first layer

    .. py:attribute:: previewAttr_2 : QLineEdit

        Previewing attribute current feature in second layer

    .. py:attribute:: previousBtn : QPushButton

        Button for preview the previous feature in similarity list result

    .. py:attribute:: SimilarityPluginDialogBase : QDialog

        Base plugin window dialog

    .. py:attribute:: tabWidget : QTabWidget

        Tab widget in the plugin

    .. py:attribute:: widgetCanvas : QgsMapCanvas

        Canvas widget in preview section for previewing the result

Class: WarnDialog
----------------------
    .. py:attribute:: msgLabel : QLabel

        The warning message

    .. py:attribute:: noBtn : QPushButton

        Button for reject the condition

    .. py:attribute:: yesBtn : QPushButton

        Button for accept the condition

Class: SimpleWarningDialog

    .. py:attribute:: msgLabel : QLabel

        The warning message

    .. py:attribute:: okBtn : QPushButton

        Ok condition