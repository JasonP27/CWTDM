#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
CWTDM 0.1 by JasonP27
Custom Wii Test Disc Maker

For quickly creating a custom Wii disc image for testing purposes.
Uses Wiimms ISO Tools for back-end
"""

import sys
import os.path
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QProcess

app = None
mainWindow = None
fstPath = None

def module_path():
    """This will get us the program's directory, even if we are frozen using py2exe"""
    if hasattr(sys, 'frozen'):
        return os.path.dirname(sys.executable)
    if __name__ == '__main__':
        return os.path.dirname(os.path.abspath(sys.argv[0]))
    return None

def FilesAreMissing():
    """Checks to see if any of the required files for CWTDM are missing"""

    if not os.path.isdir('wit'):
        QtGui.QMessageBox.warning(None, 'Error',  'Sorry, you seem to be missing the required data files for CWTDM to work. Please redownload a copy of the program.')
        return True

    required = ['wit.exe', 'cygwin1.dll', 'titles.txt', 'titles-de.txt', 'titles-es.txt', 'titles-fr.txt', 'titles-it.txt', 'titles-ja.txt', 'titles-ko.txt', 'titles-nl.txt', 'titles-pt.txt', 'titles-ru.txt', 'titles-zhcn.txt', 'titles-zhtw.txt']

    missing = []

    for check in required:
        if not os.path.isfile('wit/' + check):
            missing.append(check)

    if len(missing) > 0:
        QtGui.QMessageBox.warning(None, 'Error',  'Sorry, you seem to be missing some of the required data files for CWTDM to work. Please redownload your copy of the program. These are the files you are missing: ' + ', '.join(missing))
        return True

    return False


def GetIcon(name):
    """Helper function to grab a specific icon"""
    return QtGui.QIcon('icons/icon_%s.png' % name)


def SetFSTPath(newpath):
    """Sets the FST path"""

    global fstPath

    # isValidFSTPath will crash in os.path.join if QString is used
    # so we must change it to a Python string manually
    fstPath = unicode(newpath)


def isValidFSTPath(check='ug'):
    """Checks to see if the selected path contains an extracted FST of a Wii game"""
    if check == 'ug': check = fstPath

    if check == None or check == '': return False
    if not os.path.isdir(check): return False
    if not os.path.isdir(os.path.join(check, 'disc')): return False
    if not os.path.isdir(os.path.join(check, 'files')): return False
    if not os.path.isdir(os.path.join(check, 'sys')): return False
    if not os.path.isfile(os.path.join(check, 'align-files.txt')): return False
    if not os.path.isfile(os.path.join(check, 'cert.bin')): return False
    if not os.path.isfile(os.path.join(check, 'h3.bin')): return False
    if not os.path.isfile(os.path.join(check, 'setup.txt')): return False
    if not os.path.isfile(os.path.join(check, 'ticket.bin')): return False
    if not os.path.isfile(os.path.join(check, 'tmd.bin')): return False

    return True

class TDMWindow(QtGui.QMainWindow):
    
    def __init__(self):
        super(TDMWindow, self).__init__()
        
        self.initUI()
        
    def initUI(self):
        # set up window
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('CWTDM v0.1')
        self.setWindowIcon(QtGui.QIcon('icons/iconsm.png'))

        # create the actions
        self.SetupActionsAndMenus()

        # create the form
        self.SetupForm()

    def CreateAction(self, shortname, function, icon, text, statustext, shortcut, toggle=False):
        """Helper function to create an action"""

        if icon != None:
            act = QtGui.QAction(icon, text, self)
        else:
            act = QtGui.QAction(text, self)

        if shortcut != None: act.setShortcut(shortcut)
        if statustext != None: act.setStatusTip(statustext)
        if toggle:
            act.setCheckable(True)
        act.triggered.connect(function)

        self.actions[shortname] = act

    def SetupActionsAndMenus(self):
        """Sets up the actions and menus for CWTDM"""
        self.actions = {}
        self.CreateAction('opendir', self.HandleOpenDir, GetIcon('opendir'), 'Convert FST to WBFS', 'Choose a directory', QtGui.QKeySequence('Ctrl+Shift+O'))
        self.CreateAction('exit', self.HandleExit, None, 'Exit', 'Exit CWTDM', QtGui.QKeySequence('Ctrl+Q'))
        self.CreateAction('aboutqt', QtGui.qApp.aboutQt, None, 'About PyQt...', 'About the Qt library CWTDM is based on', QtGui.QKeySequence('Ctrl+Shift+Y'))
        self.CreateAction('infobox', self.InfoBox, GetIcon('about'), 'About CWTDM', 'Info about the program', QtGui.QKeySequence('Ctrl+Shift+I'))

        self.CreateAction('createtd', self.witProcess, GetIcon('createtd'), 'Create', 'Create a disc image from the FST chosen', QtGui.QKeySequence('Ctrl+Alt+C'))

        # create a menubar
        menubar = self.menuBar()
        #menubar.setStyleSheet("QMenuBar:item {background-color: #505050; color: #FFFFFF}")

        fmenu = menubar.addMenu('&File')
        fmenu.addAction(self.actions['opendir'])
        fmenu.addAction(self.actions['createtd'])
        fmenu.addAction(self.actions['exit'])

        hmenu = menubar.addMenu('&Help')
        hmenu.addAction(self.actions['infobox'])
        hmenu.addAction(self.actions['aboutqt'])

    def SetupForm(self):
        """Set up the widget"""
        widget = QtGui.QWidget(self)

        self.inputBox = QtGui.QLineEdit()
        self.createButton = QtGui.QPushButton("Create")
        self.inputBox.setText('Select an extracted FST and click Create')
        self.inputBox.setReadOnly(True)
        self.createButton.addAction(self.actions['createtd'])

        mainLayout = QtGui.QHBoxLayout()
        mainLayout.addWidget(widget)
        mainLayout.addWidget(self.inputBox)
        mainLayout.addWidget(self.createButton)
        self.setLayout(mainLayout)
    
    def witProcess(self):
        self.createButton.setEnabled(0)
        self.createButton.setText("Please Wait")
        os.chdir(module_path(), 'wit')
        command = "wit.exe"
        args =  ["copy", fstPath, "testdisc.wbfs", "--overwrite"] # "--verbose", "--progress"
        process = QProcess(self)
        process.finished.connect(self.onFinished)
        process.startDetached(command, args)

    def onFinished(self, exitCode, exitStatus):
        self.pushButton.setEnabled(True)

    @QtCore.pyqtSlot()
    def HandleOpenDir(self):
        """Change the fst path"""

        path = None
        while not isValidFSTPath(path):
            path = QtGui.QFileDialog.getExistingDirectory(None, 'Choose a directory containing an extracted game FST.')
            if path == '':
                return

            path = unicode(path)

            if not isValidFSTPath(path):
                QtGui.QMessageBox.information(None, 'Error',  'This folder doesn\'t seem to be a proper extracted FST from a Wii game.')
            else:
                settings.setValue('FSTPath', path)
                break

        SetFSTPath(path)

    @QtCore.pyqtSlot()
    def InfoBox(self):
        """Shows the about box"""
        AboutDialog().exec_()
        return

    @QtCore.pyqtSlot()
    def HandleExit(self):
        """Exit the editor. Why would you want to do this anyway?"""
        self.close()

def main():
    """start the app"""
    global app, mainWindow, settings
    app = QtGui.QApplication(sys.argv)
    
    # load stuff here if I want

    # settings go here if I need them
    settings = QtCore.QSettings('CWTDM', 'Custom Wii Test Disc Maker')
    # create and show main window
    mainWindow = TDMWindow()
    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()    

