# -*- coding: utf-8 -*-
"""
/***************************************************************************
 multiClipDialog
                                 A QGIS plugin
 Clips a layer into new shapefiles defined by each polygon in another layer.
                             -------------------
        begin                : 2016-04-27
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Jack Houk
        email                : john.houk@mymail.champlain.edu
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

import os

from qgis.core import *
from qgis.utils import *

from PyQt4 import QtGui, QtCore, uic

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'multi_clip_dialog_base.ui'))


class multiClipDialog(QtGui.QDialog, FORM_CLASS):
	def __init__(self, iface, parent=None):
		"""Constructor."""
		self.iface = iface
		super(multiClipDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
		self.setupUi(self)
		self.cbo1.clear()
		self.cbo2.clear()
		legendInterface = self.iface.legendInterface()
		listLayerName = [i.name() for i in legendInterface.layers() if i.type() == QgsMapLayer.VectorLayer]
		self.cbo1.addItems(listLayerName)
		self.cbo2.addItems(listLayerName)
		#connect filepath bar to browse function
		self.Browse.clicked.connect(self.outFile)

	def outFile(self): 
		# by Carson Farmer 2008
		# display file dialog for output shapefile
		self.outShp.clear()
		fileDialog = QtGui.QFileDialog()
		fileDialog.setConfirmOverwrite(False)
		outName = fileDialog.getSaveFileName(self, "Output Shapefile",".", "Shapefiles (*.shp)")
		outPath = QtCore.QFileInfo(outName).absoluteFilePath()
		if not outPath.upper().endswith(".SHP"):
			outPath = outPath + ".shp"
		if outName:
			self.outShp.clear()
			self.outShp.insert(outPath)
