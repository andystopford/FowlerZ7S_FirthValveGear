#!/usr/bin/python3.6
from PyQt5 import QtWidgets, QtGui, QtCore
import pyqtgraph as pg
import csv
import sys  # We need sys so that we can pass argv to QApplication
import os
import numpy as np
from sklearn import preprocessing
from scipy.interpolate import make_interp_spline
from scipy.signal import find_peaks
from InspectorLine import InspectorLine


FILENAME_0 = '/Results/Test016.csv'
FILENAME_1 = '/001_fwd_20.csv'
FILENAME_2 = '/.csv'


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        colour = self.palette().color(QtGui.QPalette.Window)
        self.directory = os.path.dirname(os.path.abspath(__file__))
        layout = QtWidgets.QHBoxLayout()
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        # Original
        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setBackground(colour)
        self.graphWidget.setTitle("Firth Valve Gear" + FILENAME_0[:-3],
                                  color='w', size='15pt')
        styles = {'color': (255, 255, 255), 'font-size': '20px'}
        self.graphWidget.setLabel('left', 'Displacement From '
                                                     'Mid Position', **styles)
        self.graphWidget.setLabel('bottom', 'Crank Degrees',
                                  **styles)
        self.graphWidget.addLegend(offset=(1, 0))
        self.graphWidget.showGrid(x=True, y=True)
        self.inspector1 = InspectorLine()
        self.inspector1.attachToPlotItem(self.graphWidget.getPlotItem())
        self.inspector2 = InspectorLine()
        self.inspector2.attachToPlotItem(self.graphWidget.getPlotItem())
        self.inspector2.setPos(180)
        layout.addWidget(self.graphWidget)
        self.get_curves()

    def get_curves(self):
        """Reads .csv file and fills lists for pyqtgraph.
        Row 0 = crankshaft degrees, 1 = piston position, 2 = valve position at
        mid-gear, 3 = valve position forward, 4 = valve position reverse"""
        crank_angle = []
        cutoff_mid = []
        cutoff_fwd = []
        cutoff_rev = []
        piston = []

        with open(self.directory + FILENAME_0) as csv_file:
            csv_reader = csv.reader(csv_file, quoting=csv.QUOTE_NONNUMERIC)
            line_count = 0
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
                line_count += 1
        piston = self.normalize_position_data(piston)
        piston = self.smooth_curves(crank_angle, piston)
        fwd = self.smooth_curves(crank_angle, cutoff_fwd)
        mid = self.smooth_curves(crank_angle, cutoff_mid)
        rev = self.smooth_curves(crank_angle, cutoff_rev)

        self.plot(piston[0], piston[1], "Piston Pos", 'w', 2)
        self.plot(fwd[0], fwd[1], "Valve Pos Fwd 20 deg", 'r', 2)
        self.plot(mid[0], mid[1], "Valve Pos Mid gear", 'b', 2)
        self.plot(rev[0], rev[1], "Valve Pos Rev 20 deg", 'g', 2)

    def smooth_curves(self, x_val, y_val):
        xnew = np.linspace(min(x_val), max(x_val), 100)
        spline = make_interp_spline(x_val, y_val, 3)
        ynew = spline(xnew)
        return xnew, ynew

    def centre_positions(self, val):
        """
        Valve displacement from mid position (currently 150mm from
        crankshaftcentreline)
        :param val:
        :return: val
        """
        val = val - 150
        return val

    def normalize_position_data(self, pos_list):
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

    def plot(self, x, y, plotname, color, width=1, style=QtCore.Qt.SolidLine):
        pen = pg.mkPen(color=color, width=width, style=style)
        self.graphWidget.plot(x, y, name=plotname, pen=pen)


def main():
    app = QtWidgets.QApplication(sys.argv)
    mainwin = MainWindow()
    mainwin.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

