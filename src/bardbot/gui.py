from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QMdiArea, QAction, QMdiSubWindow, QTextEdit
import sys



class MDIWindow(QMainWindow):

    count = 0
    def __init__(self):
        super().__init__()
        #multi document interface area
        self.mdi_area = QMdiArea()
        self.setCentralWidget(self.mdi_area)
        bar = self.menuBar()

        file = bar.addMenu("File")
        file.addAction("New")
        file.addAction("cascade")
        file.addAction("Tiled")
        file.triggered[QAction].connect(self.WindowTrig)
        self.setWindowTitle("MDI Application")

    def WindowTrig(self, p):


        if p.text() == "New":
            MDIWindow.count = MDIWindow.count + 1
            sub = QMdiSubWindow()
            sub.setWidget(QTextEdit())
            #sub.setWindowTitle("Sub Window" + str(MDIWindow.count))
            sub.setWindowFlags(sub.window() | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.FramelessWindowHint )

            print(bin(sub.windowFlags()) + " " + bin(QtCore.Qt.MSWindowsFixedSizeDialogHint) + " " + bin(sub.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint))

            #sub.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
            sub.setStyleSheet('background-color: grey; border: 3px solid black')
            sub.setFixedSize(200,100)
            self.mdi_area.addSubWindow(sub)
            sub.show()

        if p.text() == "cascade":
            self.mdi_area.cascadeSubWindows()

        if p.text() == "Tiled":
            self.mdi_area.tileSubWindows()


app = QApplication(sys.argv)
mdi = MDIWindow()
mdi.show()
app.exec_()