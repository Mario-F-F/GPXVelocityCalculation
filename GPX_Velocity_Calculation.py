# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GPXVelocityCalculation
                                 A QGIS plugin
 This plugin calculates velocity along a GPX track
                              -------------------
        begin                : 2015-12-22
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Mario FF
        email                : my mail is not public
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
import datetime
from datetime import *
import xml.dom.minidom
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QVariant
from PyQt4.QtGui import QAction, QIcon, QFileDialog
from qgis.core import *
import qgis.utils




# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from GPX_Velocity_Calculation_dialog import GPXVelocityCalculationDialog
import os.path


# Track point information from the GPX file
class TrackPoint( object ):
    
    def __init__(self, lat, lon, elev, time):
        
        self.lat = float( lat )
        self.lon = float( lon )
        self.time = time      
        self.elev = float( elev ) 
        
        
class GPXVelocityCalculation:
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
            'GPXVelocityCalculation_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = GPXVelocityCalculationDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&GPX Velocity Calculation')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'GPXVelocityCalculation')
        self.toolbar.setObjectName(u'GPXVelocityCalculation')
        
        
        # -- clearing input and output file name
        self.dlg.txtInputFileName.clear()
        self.dlg.txtOutputFileName.clear()
        
        self.dlg.pbOpenFileDialogInputFile.clicked.connect(self.select_input_file)
        self.dlg.pbOpenFileDialogOutputFile.clicked.connect(self.select_output_file)

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
        return QCoreApplication.translate('GPXVelocityCalculation', message)


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
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/GPXVelocityCalculation/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'GPX Velocity'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&GPX Velocity Calculation'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar
    
    
    # 
    # select_input_file
    #
    # Opens open file dialog for the input file name and propagates it to the output file name
    #
    def select_input_file(self):
        inputFilename = QFileDialog.getOpenFileName(self.dlg, "Select input file",QgsProject.instance().homePath(), '*.gpx')
        self.dlg.txtInputFileName.setText(inputFilename)
        
        # when a name is input, propagate name to output file name
        if inputFilename:
            extIndex = inputFilename.rfind(".",1)
            self.dlg.txtOutputFileName.setText(inputFilename[0:extIndex] + ".shp")
    
    
    #
    # select_output_file
    #
    # Opens open file dialog to select the output file name
    #
    def select_output_file(self):
        outputFilename = QFileDialog.getSaveFileName(self.dlg, "Select output file",QgsProject.instance().homePath(), '*.shp')
        self.dlg.txtOutputFileName.setText(outputFilename)

    
    # 
    # computeVelocity(self, sourceGPXPath, sourceSHPPath, loadLayer, meanNumSegments = 3)
    #
    #   sourceGPXPath: GPX input file name
    #   sourceSHPPath: SHP output file name
    #   loadLayer: load layer after computing or not
    #   meanNumSegments: number of preceding and suceding segment for computing mean speed
    def computeVelocity(self, sourceGPXPath, sourceSHPPath, loadLayer, meanNumSegments = 3):
        # Fields of each segmen
        #
        #   track_n:   track number
        #   elev:      elevation
        #   dateTime:  date and time
        #   speed_i:   instantaneous speed
        #   dist_i:    distance along cumputed instantaneous speed
        #   speed_m:   mean speed
        #   dist_m:    distance along cumputed mean speed
        #
        fields = QgsFields()
        fields.append(QgsField("track_n", QVariant.Int))
        fields.append(QgsField("elev", QVariant.Double))
        fields.append(QgsField("dateTime", QVariant.String))
        fields.append(QgsField("speed_i", QVariant.Double))
        fields.append(QgsField("dist_i", QVariant.Double))
        fields.append(QgsField("speed_m", QVariant.Double))
        fields.append(QgsField("dist_m", QVariant.Double))

        # open input file
        doc = xml.dom.minidom.parse( sourceGPXPath )
        
        #open output file
        writer = QgsVectorFileWriter(sourceSHPPath, "CP1250", fields, QGis.WKBLineString , QgsCoordinateReferenceSystem("EPSG:4326"), "ESRI Shapefile")

        # check output file
        if writer.hasError() != QgsVectorFileWriter.NoError:
            print "Error when creating shapefile: ",  w.errorMessage()
            return

        
        # init distance calculation
        d = QgsDistanceArea()
        d.setSourceCrs( GEOCRS_ID )
        d.setEllipsoidalMode(True)

        trk_measures = []
        track_n=0

        # reading GPX file
        for trk_node in doc.getElementsByTagName( 'trk'):
            track_n = track_n+1
            trkname = trk_node.getElementsByTagName( 'name' )[0].firstChild.data
            trksegments = trk_node.getElementsByTagName( 'trkseg' )
            
            points = []
            
            # for each segment in GPX ...
            for trksegment in trksegments:
                trk_pts = trksegment.getElementsByTagName( 'trkpt' )
                
                # ... read each track point
                for tkr_pt in trk_pts:
                
                    # get latitude and longitude
                    ptLat =tkr_pt.getAttribute("lat")
                    ptLon = tkr_pt.getAttribute("lon")
                    ptEle = None
                    ptTime = None
                    
                    # get elevation
                    if len(tkr_pt.getElementsByTagName("ele")) != 0:
                        if len(tkr_pt.getElementsByTagName("ele")[0].childNodes) != 0:
                            ptEle = tkr_pt.getElementsByTagName("ele")[0].childNodes[0].data
                            
                    # get date and time
                    if len(tkr_pt.getElementsByTagName("time")) != 0:
                        if len(tkr_pt.getElementsByTagName("time")[0].childNodes) != 0:
                            ptTime = tkr_pt.getElementsByTagName("time")[0].childNodes[0].data
                    
                    # add point to array
                    points.append(TrackPoint(ptLat, ptLon, ptEle, ptTime))

                # init (i) values
                dateTime0 = None
                dateTime1 = None

                
                x0 = points[0].lon
                y0 = points[0].lat
                elev0 = points[0].elev
                time0 = points[0].time
                if time0:
                    dateTime0 = datetime.strptime(time0, "%Y-%m-%dT%H:%M:%SZ")

                # for each point
                for i in range(1, len(points)):
                    
                    # get (i+i) values
                    x1 = points[i].lon
                    y1 = points[i].lat
                    elev1 = points[i].elev
                    time1 = points[i].time
                    
                    # compute distance
                    dist = (d.measureLine(QgsPoint(x0,y0),QgsPoint(x1,y1)))*100000
                    vel = None
                    if time1:
                        dateTime1 = datetime.strptime(time1, "%Y-%m-%dT%H:%M:%SZ")
                        if time0:
                            # compute distance and intantaneus speed
                            delta_t = (dateTime1 - dateTime0).total_seconds()
                            vel = (dist / delta_t) *3.6
                    
                    
                    # compute distance and mean speed
                    prevIndex = max(0, i - meanNumSegments)
                    postIndex = min(len(points) - 1, i + meanNumSegments)
                    
                    # compute distance
                    dist_m = 0
                    
                    for j in range(prevIndex, postIndex):
                        dist_m = dist_m + (d.measureLine(QgsPoint(points[j].lon, points[j].lat), QgsPoint(points[j+1].lon, points[j+1].lat)))*100000

                    
                    # compute mean speed
                    time_prev = points[prevIndex].time
                    time_post = points[postIndex].time
                    
                    vel_m = None
                    if time_prev and time_post:
                        delta_t_m = (datetime.strptime(time_post, "%Y-%m-%dT%H:%M:%SZ") - datetime.strptime(time_prev, "%Y-%m-%dT%H:%M:%SZ")).total_seconds()
                        vel_m = (dist_m / delta_t_m) *3.6
                    
                    # add values to the SHP file
                    fet = QgsFeature()
                    fet.setGeometry(QgsGeometry.fromPolyline([QgsPoint(x0,y0),QgsPoint(x1,y1)]))
                    fet.setAttributes([track_n, elev0, time0, vel, dist, vel_m, dist_m])
                    
                    b= writer.addFeature(fet)
                    
                     # set (i) to (i+1) for the next segment
                    x0 = x1
                    y0 = y1
                    elev0 = elev1
                    time0 = time1
                    dateTime0 = dateTime1

        # flush SHP file handler
        del writer
        
        # load layer if selected
        if loadLayer:
            head, tail = os.path.split(sourceSHPPath)
            extIndex = tail.rfind(".",1)
            
            outputLayer = self.iface.addVectorLayer(sourceSHPPath, tail[:extIndex], "ogr")
            if not outputLayer:
                print "Layer failed to load!"
    
    
    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            #pass
            self.computeVelocity(self.dlg.txtInputFileName.text(), self.dlg.txtOutputFileName.text(), self.dlg.cbLoadLayer.isChecked(), self.dlg.sbSegmentsCompute.value())
   
   
