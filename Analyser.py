#!/usr/bin/python3.6
from PyQt5 import QtWidgets, QtGui, QtCore
import pyqtgraph as pg
import csv
import sys  # We need sys so that we can pass argv to QApplication
import os
from pathlib import Path
import ast
import numpy as np
from sklearn import preprocessing
from scipy.interpolate import make_interp_spline
from scipy.signal import find_peaks
from InspectorLine import InspectorLine


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        colour = self.palette().color(QtGui.QPalette.Window)
        self.directory = os.path.dirname(os.path.abspath(__file__))
        self.file = ''
        self.open_file()
        self.setMinimumWidth(1800)
        self.setMinimumHeight(600)
        layout = QtWidgets.QHBoxLayout()
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        # Valve and Piston plots
        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setBackground(colour)
        fname = Path(self.file).stem
        self.graphWidget.setTitle("Firth Valve Gear - " + fname,
                                  color='w', size='15pt')
        styles = {'color': (255, 255, 255), 'font-size': '20px'}
        self.graphWidget.setLabel('left', 'Displacement From Mid Position',
                                  **styles)
        self.graphWidget.setLabel('bottom', 'Crank Degrees',
                                  **styles)
        self.graphWidget.addLegend(offset=(1, 0))
        self.graphWidget.showGrid(x=True, y=True)
        self.inspector1 = InspectorLine()
        self.inspector1.attachToPlotItem(self.graphWidget.getPlotItem())
        self.inspector2 = InspectorLine()
        self.inspector2.attachToPlotItem(self.graphWidget.getPlotItem())
        self.inspector2.setPos(180)

        # Plot eccentric rod end path
        self.graphWidget_1 = pg.PlotWidget()
        self.graphWidget_1.setBackground(colour)
        self.graphWidget_1.setTitle("Eccentric Rod End - Path", color='w',
                                    size='15pt')
        styles = {'color': (255, 255, 255), 'font-size': '20px'}
        self.graphWidget_1.addLegend(offset=(1, 0))
        self.graphWidget_1.showGrid(x=True, y=True)
        self.graphWidget_1.setAspectLocked()
        self.inspector3 = InspectorLine()
        self.inspector3.attachToPlotItem(self.graphWidget_1.getPlotItem())

        layout.addWidget(self.graphWidget)
        layout.addWidget(self.graphWidget_1)

        self.get_curves()
        self.get_path()

    def open_file(self):
        dialog = QtWidgets.QFileDialog()
        dialog.setDirectory(self.directory + "/Results")
        dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        dialog.setNameFilter("Text files (*.csv)")
        if dialog.exec_():
            self.file = dialog.selectedFiles()[0]

    def get_path(self):
        """
        Gets the path coordinates for the eccentric rod rocking lever end and
        plots them for each cutoff setting.'z' and 'x' refer to FreeCAD's
        coordinate system, and are plotted as x and y respectively.
        n.b.Currently the FreeCAD macro fails to output the first line (0
        degrees) of coordinates to the .csv file, so these need to be
        copy-pasted from the last line (360 degrees), which is, of course, the
        same.
        :return:
        """
        path_fwd_z = []
        path_fwd_x = []
        path_mid_z = []
        path_mid_x = []
        path_rev_z = []
        path_rev_x = []
        with open(self.file) as csv_file:
            csv_reader = csv.reader(csv_file, quoting=csv.QUOTE_NONNUMERIC)
            for row in csv_reader:
                fwd = row[5]
                fwd = ast.literal_eval(fwd)
                fwd[0] = float(fwd[0][:-3])
                fwd[1] = float(fwd[1][:-3])
                path_fwd_z.append(fwd[0])
                path_fwd_x.append(fwd[1])
                mid = row[6]
                mid = ast.literal_eval(mid)
                mid[0] = float(mid[0][:-3])
                mid[1] = float(mid[1][:-3])
                path_mid_z.append(mid[0])
                path_mid_x.append(mid[1])
                rev = row[7]
                rev = ast.literal_eval(rev)
                rev[0] = float(rev[0][:-3])
                rev[1] = float(rev[1][:-3])
                path_rev_z.append(rev[0])
                path_rev_x.append(rev[1])
        self.plot(self.graphWidget_1, path_fwd_x, path_fwd_z, "Fwd", 'r', 2)
        self.plot(self.graphWidget_1, path_mid_x, path_mid_z, "Mid", 'b',
                  2)
        self.plot(self.graphWidget_1, path_rev_x, path_rev_z, "Rev", 'g', 2)

    def get_curves(self):
        """Reads .csv file and fills lists for pyqtgraph.
        Row 0 = crankshaft degrees, 1 = piston position, 2 = valve position at
        mid-gear, 3 = valve position forward, 4 = valve position reverse"""
        crank_angle = []
        cutoff_mid = []
        cutoff_fwd = []
        cutoff_rev = []
        piston = []

        with open(self.file) as csv_file:
            csv_reader = csv.reader(csv_file, quoting=csv.QUOTE_NONNUMERIC)
            for row in csv_reader:
                crank_ang = row[0]
                crank_angle.append(crank_ang)
                piston_pos = row[1]
                piston_pos = piston_pos[:-3]
                piston.append(piston_pos)
                fwd_pos = row[2]
                fwd_pos = fwd_pos[:-3]
                fwd_pos = self.centre_positions(float(fwd_pos))
                cutoff_fwd.append(fwd_pos)
                mid_pos = row[3]
                mid_pos = mid_pos[:-3]
                mid_pos = self.centre_positions(float(mid_pos))
                cutoff_mid.append(mid_pos)
                rev_pos = row[4]
                rev_pos = rev_pos[:-3]
                rev_pos = self.centre_positions(float(rev_pos))
                cutoff_rev.append(rev_pos)
        piston = self.normalize_position_data(piston)
        piston = self.smooth_curves(crank_angle, piston)
        fwd = self.smooth_curves(crank_angle, cutoff_fwd)
        mid = self.smooth_curves(crank_angle, cutoff_mid)
        rev = self.smooth_curves(crank_angle, cutoff_rev)

        self.plot(self.graphWidget, piston[0], piston[1], "Piston Pos", 'w', 2)
        self.plot(self.graphWidget, fwd[0], fwd[1], "Valve Pos Fwd", 'r', 2)
        self.plot(self.graphWidget, mid[0], mid[1], "Valve Pos Mid", 'b', 2)
        self.plot(self.graphWidget, rev[0], rev[1], "Valve Pos Rev", 'g', 2)

    @staticmethod
    def smooth_curves(x_val, y_val):
        xnew = np.linspace(min(x_val), max(x_val), 100)
        spline = make_interp_spline(x_val, y_val, 3)
        ynew = spline(xnew)
        return xnew, ynew

    @staticmethod
    def centre_positions(val):
        """
        Valve displacement from mid position (currently 150mm from
        crankshaft centreline)
        :param val is the absolute position in FreeCAD
        :return: val - the position relative to the cylinder centreline
        """
        val = val - 150
        return val

    @staticmethod
    def normalize_position_data(pos_list):
        """
        re-scales the piston position data so that all curves are legibly
        displayed. The range should be about the same as for the valve curves
        :param pos_list:
        :return: pos_list
        """
        rescale_range = (-3, 3)
        scaler = preprocessing.MinMaxScaler(feature_range=(rescale_range[0],
                                                           rescale_range[1]))
        pos_list_scaled = scaler.fit_transform(np.array(pos_list).reshape(-1,
                                                                          1))
        # convert list-of-lists to list:
        pos_list_scaled = [round(i[0], 2) for i in pos_list_scaled]
        return pos_list_scaled

    @staticmethod
    def plot(graphwidget, x, y, plotname, color, width=1,
             style=QtCore.Qt.SolidLine):
        pen = pg.mkPen(color=color, width=width, style=style)
        graphwidget.plot(x, y, name=plotname, pen=pen)


def main():
    app = QtWidgets.QApplication(sys.argv)
    mainwin = MainWindow()
    mainwin.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

