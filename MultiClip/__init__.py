# -*- coding: utf-8 -*-
"""
/***************************************************************************
 multiClip
                                 A QGIS plugin
 Clips a layer into new shapefiles defined by each polygon in another layer.
                             -------------------
        begin                : 2016-04-27
        copyright            : (C) 2016 by Jack Houk
        email                : john.houk@mymail.champlain.edu
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load multiClip class from file multiClip.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .multi_clip import multiClip
    return multiClip(iface)
