# -*- coding: utf-8 -*-
"""
/***************************************************************************
 multiClip
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QAction, QIcon
from qgis.core import *
from qgis.utils import *
# Initialize Qt resources from file resources.py
#import resources
# Import the code for the dialog
from multi_clip_dialog import multiClipDialog
import os.path
import time
import processing

class multiClip:
	"""QGIS Plugin Implementation."""

	def __init__(self, iface):
		"""Constructor.

		:param iface: An interface instance that will be passed to this class
			which provides the hook by which you can manipulate the QGIS
			application at run time.
		:type iface: QgsInterface
		"""
        # Save reference to the QGIS interface
		self.iface = iface
        # initialize plugin directory
		self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
		locale = QSettings().value('locale/userLocale')[0:2]
		locale_path = os.path.join(
			self.plugin_dir,
			'i18n',
			'multiClip_{}.qm'.format(locale))

		if os.path.exists(locale_path):
			self.translator = QTranslator()
			self.translator.load(locale_path)

			if qVersion() > '4.3.3':
				QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
		self.dlg = multiClipDialog(iface)

        # Declare instance attributes
		self.actions = []
		self.menu = self.tr(u'&Multi Clip')
        # TODO: We are going to let the user set this up in a future iteration
		self.toolbar = self.iface.addToolBar(u'multiClip')
		self.toolbar.setObjectName(u'multiClip')

    # noinspection PyMethodMayBeStatic
	def tr(self, message):
		"""Get the translation for a string using Qt translation API.

		We implement this ourselves since we do not inherit QObject.

		:param message: String for translation.
		:type message: str, QString

		:returns: Translated version of message.
		:rtype: QString
		"""
		# noinspection PyTypeChecker,PyArgumentList,PyCallByClass
		return QCoreApplication.translate('multiClip', message)


	def add_action(
		self,
		icon_path,
		text,
		callback,
		enabled_flag=True,
		add_to_menu=True,
		add_to_toolbar=True,
		status_tip=None,
		whats_this=None,
		parent=None):
		"""Add a toolbar icon to the toolbar.

		:param icon_path: Path to the icon for this action. Can be a resource
			path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
		:type icon_path: str

		:param text: Text that should be shown in menu items for this action.
		:type text: str

		:param callback: Function to be called when the action is triggered.
		:type callback: function

		:param enabled_flag: A flag indicating if the action should be enabled
			by default. Defaults to True.
		:type enabled_flag: bool

		:param add_to_menu: Flag indicating whether the action should also
			be added to the menu. Defaults to True.
		:type add_to_menu: bool

		:param add_to_toolbar: Flag indicating whether the action should also
			be added to the toolbar. Defaults to True.
		:type add_to_toolbar: bool

		:param status_tip: Optional text to show in a popup when mouse pointer
			hovers over the action.
		:type status_tip: str

		:param parent: Parent widget for the new action. Defaults None.
		:type parent: QWidget

		:param whats_this: Optional text to show in the status bar when the
			mouse pointer hovers over the action.

		:returns: The action that was created. Note that the action is also
			added to self.actions list.
		:rtype: QAction
		"""

		icon = QIcon(icon_path)
		action = QAction(icon, text, parent)
		action.triggered.connect(callback)
		action.setEnabled(enabled_flag)

		if status_tip is not None:
			action.setStatusTip(status_tip)

		if whats_this is not None:
			action.setWhatsThis(whats_this)

		if add_to_toolbar:
			self.toolbar.addAction(action)

		if add_to_menu:
			self.iface.addPluginToVectorMenu(
				self.menu,
				action)

		self.actions.append(action)

		return action

	def initGui(self):
		"""Create the menu entries and toolbar icons inside the QGIS GUI."""

		icon_path = ':/plugins/multiClip/icon.png'
		self.add_action(
			icon_path,
			text=self.tr(u'Multi-Clip'),
			callback=self.run,
			parent=self.iface.mainWindow())


	def unload(self):
		"""Removes the plugin menu item and icon from QGIS GUI."""
		for action in self.actions:
			self.iface.removePluginVectorMenu(
				self.tr(u'&Multi Clip'),
				action)
			self.iface.removeToolBarIcon(action)
        # remove the toolbar
		del self.toolbar


	def run(self):
		"""Run method that performs all the real work"""
		# update and show the dialog
		self.dlg.__init__(iface)
		self.dlg.show()
		# Run the dialog event loop
		result = self.dlg.exec_()
		# See if OK was pressed
		if result:
			inputLayer = str(self.dlg.cbo1.currentText())
			overLayer = str(self.dlg.cbo2.currentText())
			#clipLower and clipUpper are used to iterate throught shapes
			clipLower = 0
			clipUpper = 1
			#baseFilename is also project dependant and should be input by the user if this script is fully implemented
			baseFilename = str(self.dlg.outShp.text())[:-4]
			outputFilename = None
			#finds two layers by name
			for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
					if lyr.name() == overLayer:
							overLayer = lyr
							break

			for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
					if lyr.name() == inputLayer:
							inputLayer = lyr
							break

			#creates lists of feature IDs for given layers
			iface.setActiveLayer(overLayer)
			it = overLayer.getFeatures( QgsFeatureRequest( ) )
			overLayerIds = [i.id() for i in it]
			it = inputLayer.getFeatures( QgsFeatureRequest() )
			inputLayerIds = [i.id() for i in it]

			#selects all of the input feature and one feature from the clip layer
			inputLayer.setSelectedFeatures( inputLayerIds )

			for i in overLayerIds:
				overLayer.setSelectedFeatures( overLayerIds[clipLower:clipUpper] )
				outputFilename = (baseFilename + `clipUpper` + ".shp")
				processing.runalg("qgis:clip", inputLayer, overLayer, outputFilename)
				print i
				clipUpper += 1
				clipLower += 1
				time.sleep(2)

			#Clears map canvas selection
			mc = iface.mapCanvas()
			for layer in mc.layers():
				if layer.type() == layer.VectorLayer:
					layer.removeSelection()
			mc.refresh()
			# Do something useful here - delete the line containing pass and
			# substitute with your code.