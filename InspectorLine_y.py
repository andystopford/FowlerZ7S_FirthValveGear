from PyQt5 import Qt
from pyqtgraph import InfiniteLine, TextItem
import numpy as np
from datetime import date


class InspectorLine_y(InfiniteLine):

    def __init__(self, ):
        super(InspectorLine_y, self).__init__(angle=0, movable=True)
        self._labels = []
        self._plot_item = None
        self.sigPositionChanged.connect(self._onMoved)

    def _onMoved(self):
        x_px_size, _ = self.getViewBox().viewPixelSize()
        inspector_x = self.value()
        self._removeLabels()
        points = []

        # iterate over the existing curves
        for c in self._plot_item.curves:

            # find the index of the closest point of this curve
            adiff = np.abs(c.yData - inspector_x)
            idx = np.argmin(adiff)

            # only add a label if the line touches the symbol
            tolerance = .5 * max(1, c.opts['symbolSize']) * x_px_size
            if adiff[idx] < tolerance:
                points.append((c.xData[idx], c.yData[idx]))

        self._createLabels(points)

    def _createLabels(self, points):
        for x, y in points:
            x = round(x, 2)
            y = round(y, 2)
            text = 'x={}, y={}'.format(x, y)
            text_item = TextItem(text=text)
            text_item.setPos(x, y)
            self._labels.append(text_item)
            self._plot_item.addItem(text_item)

    def _removeLabels(self):
        # remove existing texts
        for item in self._labels:
            self._plot_item.removeItem(item)
        self._labels = []

    def attachToPlotItem(self, plot_item):
        self._plot_item = plot_item
        plot_item.addItem(self, ignoreBounds=True)

    def dettach(self, plot_item):
        self._removeLabels()
        self._plot_item.removeItem(self)
        self._plot_item = None
