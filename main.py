from PyQt5 import QtWidgets, QtGui, QtCore
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import csv
import sys  # We need sys so that we can pass argv to QApplication
#sys.path.append('../')
import os
import numpy as np
from sklearn import preprocessing
from scipy.interpolate import make_interp_spline
from InspectorLine import InspectorLine


FILENAME_0 = '/001_mid.csv'
FILENAME_1 = '/001_fwd_20.csv'
FILENAME_2 = '/.csv'


class Color(QtWidgets.QWidget):
    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor(color))
        self.setPalette(palette)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        colour = self.palette().color(QtGui.QPalette.Window)
        self.directory = os.path.dirname(os.path.abspath(__file__))
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(Color('red'))
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        # Original
        self.graphWidget_0 = pg.PlotWidget()
        self.graphWidget_0.setBackground(colour)
        self.graphWidget_0.setTitle("Firth Valve Gear",
                                    color='w', size='15pt')
        styles = {'color': (255, 255, 255), 'font-size': '20px'}
        self.graphWidget_0.setLabel('left', 'Displacement From '
                                                     'Mid Position', **styles)
        self.graphWidget_0.setLabel('bottom', 'Crank Degrees',
                                    **styles)
        self.graphWidget_0.addLegend(offset=(1, 0))
        self.graphWidget_0.showGrid(x=True, y=True)

        # Modified
        self.graphWidget_1 = pg.PlotWidget()
        self.graphWidget_1.setBackground(colour)
        self.graphWidget_1.setTitle("Firth Valve Gear - Modified ",
                                    color='w', size='15pt')
        styles = {'color': (255, 255, 255), 'font-size': '20px'}
        self.graphWidget_1.setLabel('left', 'Displacement '
                                                       'From Mid Position',
                                    **styles)
        self.graphWidget_1.setLabel('bottom', 'Crank Degrees',
                                    **styles)
        self.graphWidget_1.addLegend(offset=(1, 0))
        self.graphWidget_1.showGrid(x=True, y=True)
        layout.addWidget(self.graphWidget_0)
        layout.addWidget(self.graphWidget_1)

        self.inspector_0 = InspectorLine()
        self.inspector_1 = InspectorLine()
        self.inspector_0.attachToPlotItem(self.graphWidget_0.getPlotItem())
        self.inspector_1.attachToPlotItem(self.graphWidget_1.getPlotItem())

        self.get_curves(FILENAME_0, self.graphWidget_0)
        self.get_curves(FILENAME_1, self.graphWidget_1)

    def get_crank_degrees(self):
        crank_angle = []
        with open(self.directory + FILENAME_0) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',',
                                    quoting=csv.QUOTE_NONNUMERIC)
            line_count = 0
            for row in csv_reader:
                crank_angle.append(row[0])
                line_count += 1
        #crank_angle = self.normalize_position_data(crank_angle)
        return crank_angle

    def get_curves(self, fname, graphwidget):
        """Reads .csv file and fills lists for pyqtgraph.
        Row 0 = crankshaft degrees, 1 = piston position, 2 = valve position at
        mid-gear, 3 = valve position forward, 4 = valve position reverse"""
        crank_angle = self.get_crank_degrees()
        cutoff_mid = []
        cutoff_fwd = []
        cutoff_rev = []
        piston_x = []

        with open(self.directory + fname) as csv_file:
            csv_reader = csv.reader(csv_file, quoting=csv.QUOTE_NONNUMERIC)
            line_count = 0
            for row in csv_reader:
                piston_pos = row[1]
                piston_pos = piston_pos[:-3]
                piston_x.append(piston_pos)
                valve_pos = row[2]
                valve_pos = valve_pos[:-3]
                cutoff_mid.append(valve_pos)
                #cutoff_rev.append(row[4])
                line_count += 1
        piston_x = self.normalize_position_data(piston_x)
        piston_x = self.smooth_curves(crank_angle, piston_x)
        #cutoff_mid = self.normalize_position_data(cutoff_mid)
        mid = self.smooth_curves(crank_angle, cutoff_mid)


        if graphwidget == self.graphWidget_0:
            #self.plot(piston_x[0], piston_x[1], "Piston Pos", 'w', 2)
            #self.plot(fwd[0], fwd[1], "Valve Pos Fwd 20 deg", 'r', 2)
            self.plot(mid[0], mid[1], "Valve Pos Mid gear", 'b', 2)
            #self.plot(rev[0], rev[1], "Valve Pos Rev 20 deg", 'g', 2)

        else:
            #self.plot_mod(piston_x[0], piston_x[1], "Piston Pos", 'w', 2)
            #self.plot_mod(fwd[0], fwd[1], "Valve Pos Fwd 20 deg", 'r', 2)
            self.plot_mod(mid[0], mid[1], "Valve Pos Mid gear", 'b', 2)
            #self.plot_mod(rev[0], rev[1], "Valve Pos Rev 20 deg", 'g', 2)

    def smooth_curves(self, x_val, y_val):
        xnew = np.linspace(min(x_val), max(x_val), 100)
        spline = make_interp_spline(x_val, y_val, 3)
        ynew = spline(xnew)
        return xnew, ynew

    def centre_valve_positions(self, val):
        """Valve displacement from centre position (304.8)"""
        val = val - 305
        return val

    def normalize_position_data(self, pos_list):
        rescale_range = (-50, 50)
        scaler = preprocessing.MinMaxScaler(feature_range=(rescale_range[0],
                                                           rescale_range[1]))
        pos_list_scaled = scaler.fit_transform(np.array(pos_list).reshape(-1,
                                                                          1))
        # convert list-of-lists to list:
        pos_list_scaled = [round(i[0], 2) for i in pos_list_scaled]
        return pos_list_scaled

    def plot(self, x, y, plotname, color, width=1, style=QtCore.Qt.SolidLine):
        pen = pg.mkPen(color=color, width=width, style=style)
        self.graphWidget_0.plot(x, y, name=plotname, pen=pen)
        #self.inspector_0.setPos(x)

    def plot_mod(self, x, y, plotname, color, width=1, style=QtCore.Qt.SolidLine):
        pen = pg.mkPen(color=color, width=width, style=style)
        self.graphWidget_1.plot(x, y, name=plotname, pen=pen)
        #self.inspector_1.setPos(x)

def main():
    app = QtWidgets.QApplication(sys.argv)
    mainwin = MainWindow()
    mainwin.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

