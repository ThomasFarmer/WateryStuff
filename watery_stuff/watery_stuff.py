# -*- coding: utf-8 -*-
"""
/***************************************************************************
 WateryStuff
                                 A QGIS plugin
 Utility tool for a project i know nothing about
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2019-11-04
        git sha              : $Format:%H$
        copyright            : (C) 2019 by Béres Tamás
        email                : berestamasbela@protonmail.com
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
from qgis.PyQt import QtGui
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

# Initialize Qt resources from file resources.py
from qgis._core import QgsProject, QgsMapLayer, QgsPoint, QgsDistanceArea, QgsPointXY, QgsUnitTypes, QgsSpatialIndex

from .resources import *
# Import the code for the dialog
from .watery_stuff_dialog import WateryStuffDialog
import os.path
import geojson


class WateryStuff:
    """QGIS Plugin Implementation."""
    vector_layers = []
    polygon_picked = None
    point_picked = None
    layerPolyOK = False
    layerPtsOK = False

    # raster_layers = []


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
            'WateryStuff_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&WateryStuff')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

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
        return QCoreApplication.translate('WateryStuff', message)


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
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def loadVectors(self):
        try:
            self.dlg.textEditLogProcess.clear()
            self.dlg.comboBoxPoint.clear()
            self.dlg.comboBoxPolygon.clear()
            self.vector_layers = []
            self.polygon_picked = None
            self.point_picked = None
            self.RG_picked = None
            self.hitlist = []

            layers = [layer for layer in QgsProject.instance().mapLayers().values()]
            for layer in layers:
                # if layer.type() == QgsMapLayer.RasterLayer:
                #     raster_layers.append(layer)
                if layer.type() == QgsMapLayer.VectorLayer:
                    self.vector_layers.append(layer)

            for vl in self.vector_layers:
                #self.dlg.comboBoxPoint.addItem('fvdd')
                # point layer type
                if str(vl.geometryType()) == '0':
                    self.dlg.comboBoxPoint.addItem(str(vl.name()))
                    self.dlg.comboBoxRainGauge.addItem(str(vl.name()))
                    self.dlg.textEditLogProcess.setPlainText(self.dlg.textEditLogProcess.toPlainText() + 'Adding point layer '+ str(vl.name())+"...\n")
                # polygon layer type
                elif str(vl.geometryType()) == '2':
                    self.dlg.comboBoxPolygon.addItem(str(vl.name()))
                    self.dlg.textEditLogProcess.setPlainText(self.dlg.textEditLogProcess.toPlainText() + 'Adding polygon layer '+ str(vl.name())+"...\n")
            self.dlg.textEditLogProcess.moveCursor(QtGui.QTextCursor.End)
        except Exception as genex:
            self.dlg.textEditLogProcess.setPlainText(self.dlg.textEditLogProcess.toPlainText() + "PYTHON EXCEPTION CAUGHT: \n" + str(genex) + '\n')

    def checkLayers(self):
        try:
            llayerPolyOK = False
            llayerPtsOK = False
            llayerRGOK = False
            for vl in self.vector_layers:
                if (self.dlg.comboBoxPolygon.currentText() == str(vl.name())):
                    prov = vl.dataProvider()
                    fieldNames = []
                    fields = prov.fields()
                    for field in fields:
                        fieldNames.append(field.name())
                    if (('HND' in fieldNames) and str(vl.name()) == self.dlg.comboBoxPolygon.currentText()):
                        self.polygon_picked = vl
                        self.dlg.textEditLogProcess.setPlainText(
                            self.dlg.textEditLogProcess.toPlainText() + "Watershed layer field requirements checked.\n")
                        self.dlg.labelStatus.setText('Selected layers have passed the layer check.')
                        llayerPolyOK = True
                    else:
                        self.polygon_picked = None
                        self.dlg.textEditLogProcess.setPlainText(
                            self.dlg.textEditLogProcess.toPlainText() + "Watershed layer field requirements check failed.\n")
                        self.dlg.labelStatus.setText('**LAYER CHECKS FAILED**')
                        llayerPolyOK = False
            for vl2 in self.vector_layers:
                if (self.dlg.comboBoxPoint.currentText() == str(vl2.name())):
                    prov = vl2.dataProvider()
                    fieldNames = []
                    fields = prov.fields()
                    for field in fields:
                        fieldNames.append(field.name())
                    if (('SUB_CATCH_' in fieldNames) and str(vl2.name()) == self.dlg.comboBoxPoint.currentText()):
                        self.point_picked = vl2
                        self.dlg.textEditLogProcess.setPlainText(self.dlg.textEditLogProcess.toPlainText() + "Intersection point layer field requirements checked.\n")
                        llayerPtsOK = True
                    else:
                        self.point_picked = None
                        self.dlg.textEditLogProcess.setPlainText(
                            self.dlg.textEditLogProcess.toPlainText() + "Intersection point layer field requirements check failed.\n")
                        self.dlg.labelStatus.setText('**LAYER CHECKS FAILED**')
                        llayerPtsOK = False
            for vl3 in self.vector_layers:
                if (self.dlg.comboBoxRainGauge.currentText() == str(vl3.name())):
                    prov = vl3.dataProvider()
                    fieldNames = []
                    fields = prov.fields()
                    for field in fields:
                        fieldNames.append(field.name())
                    if (('HND' in fieldNames) and ('NAME' in fieldNames) and str(vl3.name()) == self.dlg.comboBoxRainGauge.currentText()):
                        self.RG_picked = vl3
                        self.dlg.textEditLogProcess.setPlainText(self.dlg.textEditLogProcess.toPlainText() + "Rain gauge layer field requirements checked.\n")
                        llayerRGOK = True
                    else:
                        self.RG_picked = None
                        self.dlg.textEditLogProcess.setPlainText(
                            self.dlg.textEditLogProcess.toPlainText() + "Rain gauge layer field requirements check failed.\n")
                        self.dlg.labelStatus.setText('**LAYER CHECKS FAILED**')
                        llayerRGOK = False
            if ((llayerPtsOK == True) and (llayerPolyOK == True) and (llayerRGOK == True)):
                self.dlg.pushButtonCalculate.setEnabled(True)
                self.dlg.pushButtonCalculate_NN.setEnabled(True)
            else:
                self.dlg.pushButtonCalculate.setEnabled(False)
                self.dlg.pushButtonCalculate_NN.setEnabled(False)
            self.dlg.textEditLogProcess.moveCursor(QtGui.QTextCursor.End)
        except Exception as genex:
            self.dlg.textEditLogProcess.setPlainText(self.dlg.textEditLogProcess.toPlainText() + "PYTHON EXCEPTION CAUGHT: \n" + str(genex) + '\n')


    def doStuffv2(self):
        try:
            self.hitlist = []
            poly_features = self.polygon_picked.getFeatures()
            pts_features = self.point_picked.getFeatures()
            self.dlg.textEditLogProcess.setPlainText(self.dlg.textEditLogProcess.toPlainText() + "Running process on " + self.polygon_picked.name() + " / " + self.point_picked.name() + "...\n")

            # preproc, feature id, coords and hnd/subcatch to table
            point_table = []
            polygon_table = []
            for thisPoint in pts_features:
                pointGeom = thisPoint.geometry()
                pointID = thisPoint.id()
                xpoint = pointGeom.asMultiPoint()

                SUBCATCH0_of_thisPoint = thisPoint["SUB_CATCH_"]
                SUBCATCH1_of_thisPoint = thisPoint["SUB_CATCH1"]
                SUBCATCH2_of_thisPoint = thisPoint["SUB_CATCH2"]
                SUBCATCH3_of_thisPoint = thisPoint["SUB_CATCH3"]
                SUBCATCH4_of_thisPoint = thisPoint["SUB_CATCH4"]

                for pointElem in xpoint:
                    rxpoint = round(pointElem.x(), 2)
                    rypoint = round(pointElem.y(), 2)
                    # self.dlg.textEditLogProcess.setPlainText(
                    #     self.dlg.textEditLogProcess.toPlainText() + "RXPOINT: "+  str(rxpoint) +" RYPOINT: "+str(rypoint)+ "\n")
                    point_table.append([pointID, rxpoint, rypoint, SUBCATCH0_of_thisPoint, SUBCATCH1_of_thisPoint, SUBCATCH2_of_thisPoint, SUBCATCH3_of_thisPoint, SUBCATCH4_of_thisPoint])

            # for p in point_table:
            #     self.dlg.textEditLogProcess.setPlainText(self.dlg.textEditLogProcess.toPlainText() + "FEAT.ID: "+str(p[0])+" RXPOINT: " + str(p[1]) + " RYPOINT: " + str(p[2])+ " SUBCATCH0: " + str(p[3]) + "\n")

            for thisPoly in poly_features:
                polyGeom = thisPoly.geometry()
                xpoly = polyGeom.asMultiPolygon()
                polyID = thisPoly.id()
                HND_of_thisPoly = thisPoly["HND"]
                for polyElem in xpoly:
                    vxgroup = []
                    vygroup = []
                    for multiwhatever in polyElem:
                        for vertex in multiwhatever:
                            rxpoly = round(vertex.x(), 2)
                            rypoly = round(vertex.y(), 2)
                            vxgroup.append(rxpoly)
                            vygroup.append(rypoly)
                    polygon_table.append([polyID, vxgroup, vygroup, HND_of_thisPoly])
            # for p in polygon_table:
            #     self.dlg.textEditLogProcess.setPlainText(self.dlg.textEditLogProcess.toPlainText() + "FEAT.ID: "+str(p[0])+" RXPOLY: " + str(p[1]) + " RYPOLY: " + str(p[2])+ " HND: " + str(p[3]) + "\n")

            # cross-check for HND and SUBCATCH
            hitcounter = 0
            hitlist = []
            for ply in polygon_table:
                for pt in point_table:
                    if ply[3] == pt[3]:
                        # self.dlg.textEditLogProcess.setPlainText(
                        #     self.dlg.textEditLogProcess.toPlainText() + 'HND/SUBCATCH match found at: ' + str(
                        #         pt[1]) + ";" + str(pt[2]) +"\nIN: "+str(ply[1])+" "+str(ply[2])+ "\nHND: " + str(pt[3]) + "\n")
                        hitcounter+=1
                        hitlist.append([pt[0],ply[0]])
                    elif ply[3] == pt[4]:
                        # self.dlg.textEditLogProcess.setPlainText(
                        #     self.dlg.textEditLogProcess.toPlainText() + 'HND/SUBCATCH match found at: ' + str(
                        #         pt[1]) + ";" + str(pt[2]) +"\nIN: "+str(ply[1])+" "+str(ply[2])+ "\nHND: " + str(pt[3]) + "\n")
                        hitcounter+=1
                        hitlist.append([pt[0], ply[0]])
                    elif ply[3] == pt[5]:
                        # self.dlg.textEditLogProcess.setPlainText(
                        #     self.dlg.textEditLogProcess.toPlainText() + 'HND/SUBCATCH match found at: ' + str(
                        #         pt[1]) + ";" + str(pt[2]) +"\nIN: "+str(ply[1])+" "+str(ply[2])+ "\nHND: " + str(pt[3]) + "\n")
                        hitcounter+=1
                        hitlist.append([pt[0], ply[0]])
                    elif ply[3] == pt[6]:
                        # self.dlg.textEditLogProcess.setPlainText(
                        #     self.dlg.textEditLogProcess.toPlainText() + 'HND/SUBCATCH match found at: ' + str(
                        #         pt[1]) + ";" + str(pt[2]) +"\nIN: "+str(ply[1])+" "+str(ply[2])+ "\nHND: " + str(pt[3]) + "\n")
                        hitcounter+=1
                        hitlist.append([pt[0], ply[0]])
                    elif ply[3] == pt[7]:
                        # self.dlg.textEditLogProcess.setPlainText(
                        #     self.dlg.textEditLogProcess.toPlainText() + 'HND/SUBCATCH match found at: ' + str(
                        #         pt[1]) + ";" + str(pt[2]) +"\nIN: "+str(ply[1])+" "+str(ply[2])+ "\nHND: " + str(pt[3]) + "\n")
                        hitcounter+=1
                        hitlist.append([pt[0], ply[0]])
            self.dlg.textEditLogProcess.setPlainText(
                self.dlg.textEditLogProcess.toPlainText() + 'Total number of HND/SUBCATCH matches: ' + str(hitcounter) + "\n")

            # hitlist: [matching point feature id, of matching polygon feature id]
            self.hitlist = hitlist
            self.dlg.textEditLogProcess.setPlainText(
                self.dlg.textEditLogProcess.toPlainText() + 'Calculating distance, updating fields... '  + "\n")
            self.polygon_picked.startEditing()
            #distance = QgsDistanceArea()
            # checking for longest diagonal
            for geometryPair in hitlist:
                for p in point_table:
                    if geometryPair[1] == p[0]:
                        basePoint = QgsPointXY(p[1],p[2])
                        for polywat in polygon_table:
                            maxrange = 0.0
                            # self.dlg.textEditLogProcess.setPlainText(
                            #     self.dlg.textEditLogProcess.toPlainText() + " polywat " + str(polywat) + '\n')
                            for vx in range(len(polywat[1])):
                                vertexPoint = QgsPointXY(polywat[1][vx], polywat[2][vx])

                                # Measure the distance
                                m = basePoint.distance(vertexPoint)
                                #d.convertAreaMeasurement(d.measureArea(geom), QgsUnitTypes.DistanceKilometers ))
                                if m > maxrange:
                                    maxrange = m

                            id_mod_col = self.polygon_picked.dataProvider().fieldNameIndex("S_LEFOLY")
                            self.polygon_picked.changeAttributeValue(geometryPair[1], id_mod_col, maxrange)

            self.polygon_picked.commitChanges()
            self.dlg.textEditLogProcess.setPlainText(
                self.dlg.textEditLogProcess.toPlainText() + 'Process finished.\n')
            self.dlg.textEditLogProcess.moveCursor(QtGui.QTextCursor.End)
        except Exception as genex:
            self.dlg.textEditLogProcess.setPlainText(self.dlg.textEditLogProcess.toPlainText() + "PYTHON EXCEPTION CAUGHT: \n" + str(genex) + '\n')

    def doStuff_NN(self):
        try:
            self.dlg.textEditLogProcess.setPlainText(self.dlg.textEditLogProcess.toPlainText() + "Calculating nearest neighbors for watershed polygons... \n")
            target_layer = self.polygon_picked

            source_layer_index = QgsSpatialIndex(self.RG_picked.getFeatures())
            source_layer_features = {feature.id(): feature for (feature) in self.RG_picked.getFeatures()}
            target_layer_features = self.polygon_picked.getFeatures()

            target_layer.startEditing()

            for f in target_layer_features:
                nearest = source_layer_index.nearestNeighbor(f.geometry().centroid().asPoint(), 1)[0]
                value = source_layer_features[nearest].attribute("NAME")

                #target_layer.changeAttributeValue(f.id(), 1, value)
                id_mod_col = self.polygon_picked.dataProvider().fieldNameIndex("RAIN_GAGE")
                target_layer.changeAttributeValue(f.id(), id_mod_col, value)
                #print(str(f.id()) + " " + str(id_mod_col) + " " + str(value))

            target_layer.commitChanges()
            self.dlg.textEditLogProcess.setPlainText(
                self.dlg.textEditLogProcess.toPlainText() + 'Process finished.\n')
        except Exception as genex:
            self.dlg.textEditLogProcess.setPlainText(self.dlg.textEditLogProcess.toPlainText() + "PYTHON EXCEPTION CAUGHT: \n" + str(genex) + '\n')


    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/watery_stuff/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'WateryStuff'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&WateryStuff'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = WateryStuffDialog()

        # show the dialog
        self.dlg.show()
        self.dlg.labelStatus.setText('Select layers for field req. checks.')
        self.dlg.textEditLogProcess.ensureCursorVisible()
        self.dlg.pushButtonCalculate.setEnabled(False)
        self.dlg.pushButtonCalculate_NN.setEnabled(False)
        self.dlg.tabWidget.setTabEnabled(1, False)
        self.dlg.pushButtonCheckLayers.clicked.connect(self.checkLayers)
        self.dlg.pushButtonCalculate.clicked.connect(self.doStuffv2)
        self.dlg.pushButtonCalculate_NN.clicked.connect(self.doStuff_NN)
        # loading up vectors on window popup
        self.loadVectors()

        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
