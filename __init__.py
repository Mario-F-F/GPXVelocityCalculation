# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GPXVelocityCalculation
                                 A QGIS plugin
 This plugin calculates velocity along a GPX track
                             -------------------
        begin                : 2015-12-22
        copyright            : (C) 2015 by Mario FF
        email                : my mail is not public
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
    """Load GPXVelocityCalculation class from file GPXVelocityCalculation.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .GPX_Velocity_Calculation import GPXVelocityCalculation
    return GPXVelocityCalculation(iface)
