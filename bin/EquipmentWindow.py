from PyQt4 import uic

( Ui_EquipmentWindow, QDialog ) = uic.loadUiType( 'equipwindow.ui' )

# Log everything, and send it to file.
import logging 
logging.basicConfig(level=logging.DEBUG, filename='guredo_debug.log')

class EquipmentWindow ( QDialog ):
    """EquipmentWindow inherits QDialog"""

    def __init__ ( self, parent = None ):
        QDialog.__init__( self, parent )
        self.ui = Ui_EquipmentWindow()
        self.ui.setupUi( self )

    def __del__ ( self ):
        self.ui = None
