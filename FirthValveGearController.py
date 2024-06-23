#! python
# -*- coding: utf-8 -*-
import time
import csv
import os
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QDialog, QLabel, QSlider, QLineEdit, QPushButton


class ControlPanel(QDialog):
    """
    docstring for ControlPanel.
    """
    def __init__(self, document, actuator):
        super(ControlPanel, self).__init__()
        self.doc = document
        self.actuator = document.getObject(actuator)
        self.actuator.Angle = 0
        Gui.runCommand("asm3CmdQuickSolve", 0)
        self.current_value = 0
        self.start_value = 0.001
        self.end_value = 359.999
        self.unit_suffix = (" °")
        self.result = ""
        self.setMaximumWidth(400)
        #self.setMaximumHeight(200)
        self.setMinimumWidth(400)
        self.setMinimumHeight(200)
        self.setWindowTitle("Firth Valve Gear")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        # Horizontal slider
        self.actuator_slider = QSlider(self)
        self.actuator_slider.setOrientation(QtCore.Qt.Horizontal)
        self.actuator_slider.setGeometry(QtCore.QRect(35, 15, 330, 25))
        self.actuator_slider.setObjectName("horizontalSlider")
        self.actuator_slider.setInvertedAppearance(False)
        self.actuator_slider.setRange(0, 100)
        self.actuator_slider.setValue(
            int(self.current_value / self.step_ratio()))
        self.actuator_slider.valueChanged.connect(self.on_actuator_slider)

        # Slider label
        self.label_current = QLabel("", self)
        self.label_current.setText(str(round(self.current_value, 1)) +
                                   self.unit_suffix)
        self.label_current.setGeometry(QtCore.QRect(175, 30, 50, 25))
        
        # Jog buttons
        self.button_jog_back = QPushButton('<', self)
        self.button_jog_back.setGeometry(QtCore.QRect(35, 65, 60, 25))
        self.button_jog_back.pressed.connect(self.jog_back)

        self.button_jog_fwd = QPushButton('>', self)
        self.button_jog_fwd.setGeometry(QtCore.QRect(305, 65, 60, 25))
        self.button_jog_fwd.pressed.connect(self.jog_fwd)

        # Angle input
        self.angle_input = QLineEdit(self)
        self.angle_input.setText(str(round(self.current_value, 1)))
        self.angle_input.setGeometry(170, 70, 50, 25)
        self.angle_input.returnPressed.connect(self.set_angle)

        # Cutoff setting
        self.cutoff_ctrl = QLineEdit(self)
        self.cutoff_ctrl.setGeometry(170, 105, 50, 25)
        self.cutoff_ctrl.returnPressed.connect\
            (lambda: self.set_cutoff(int(self.cutoff_ctrl.text())))

        # File name input
        self.output_file_input = QLineEdit(self)
        self.output_file_input.setText("Enter file Name Here")
        self.output_file_input.setGeometry(QtCore.QRect(100, 145, 205, 25))

        # radius link angle inputs
        self.fwd_angle = ''
        self.fwd_angle_input = QLineEdit(self)
        self.fwd_angle_input.setText('60')
        self.fwd_angle_input.setGeometry(100, 175, 50, 25)
        self.fwd_angle = self.fwd_angle_input.text()
        self.fwd_angle_input.textChanged[str].connect(self.set_fwd)

        self.mid_angle = ''
        self.mid_angle_input = QLineEdit(self)
        self.mid_angle_input.setText('80')
        self.mid_angle_input.setGeometry(180, 175, 50, 25)
        self.mid_angle = self.mid_angle_input.text()
        self.mid_angle_input.textChanged[str].connect(self.set_mid)

        self.rev_angle = ''
        self.rev_angle_input = QLineEdit(self)
        self.rev_angle_input.setText('100')
        self.rev_angle_input.setGeometry(250, 175, 50, 25)
        self.rev_angle = self.rev_angle_input.text()
        self.rev_angle_input.textChanged[str].connect(self.set_rev)

        # Buttons
        self.button_run = QPushButton("Run", self)
        self.button_run.setGeometry(QtCore.QRect(150, 210, 100, 25))
        self.button_run.pressed.connect(self.run)

        self.button_test = QPushButton("Test", self)
        self.button_test.setGeometry(QtCore.QRect(150, 245, 100, 25))
        self.button_test.pressed.connect(self.test)

        self.show()

    def test(self):
        sk = App.ActiveDocument.getObject('Sketch004')
        try:
            sk.setDatum('Cutoff CTRL',
                        App.Units.Quantity(str(int(45)) + ' deg'))
        except:
            print('test failed')

    def jog_back(self):
        self.current_value = self.current_value - 10
        self.actuator.Angle = self.current_value
        Gui.runCommand("asm3CmdQuickSolve", 0)

    def jog_fwd(self):
        self.current_value = self.current_value + 10
        self.actuator.Angle = self.current_value
        Gui.runCommand("asm3CmdQuickSolve", 0)
        self.label_current.setText(str(round(self.current_value, 1)) +
                                   self.unit_suffix)
        self.angle_input.setText(str(round(self.current_value, 1)))

    def set_angle(self):
        """
        TODO fix crash
        :param angle:
        :return:
        """
        try:
            self.current_value = int(self.angle_input.text())
            self.actuator.Angle = self.current_value
            Gui.runCommand("asm3CmdQuickSolve", 0)
            self.label_current.setText(str(round(self.current_value, 1)) +
                                       self.unit_suffix)
            self.angle_input.setText(str(round(self.current_value, 1)))
        except:
            print('Exception @ set_angle()')

    def set_output_file(self):
        output_file = self.output_file_input.text()
        return output_file

    def set_fwd(self, angle):
        self.fwd_angle = angle
        print('fwd cutoff set', angle)

    def set_mid(self, angle):
        self.mid_angle = angle
        print('mid cutoff set', angle)

    def set_rev(self, angle):
        self.rev_angle = angle
        print('rev cutoff set', angle)

    def step_ratio(self):
        ratio = (self.end_value - self.start_value) / 100
        return ratio

    def on_actuator_slider(self, slider_value):
        self.current_value = slider_value * self.step_ratio() + \
                             self.start_value
        self.actuator.Angle = self.current_value
        self.label_current.setText(str(round(self.current_value, 1)) +
                                   self.unit_suffix)
        self.angle_input.setText(str(round(self.current_value, 1)))
        Gui.runCommand("asm3CmdQuickSolve", 0)

    def run(self):
        print("Run")
        crank_angles = []
        piston_posns = []
        fwd_posns = []
        mid_posns = []
        rev_posns = []
        cutoffs = [[self.fwd_angle, fwd_posns], [self.mid_angle, mid_posns],
                   [self.rev_angle, rev_posns]]
        for angle in range(0, 370, 10):
            crank_angles.append(angle)
        piston_posns = self.get_piston_positions(piston_posns)
        try:
            for cutoff in cutoffs:
                print('setting cutoff')
                self.set_cutoff(cutoff[0])
                print('using cutoff')
                self.use_selected_cutoff(cutoff[1])
            #print(piston_posns, fwd_posns, mid_posns, rev_posns)
            posns = zip(crank_angles, piston_posns, fwd_posns, mid_posns,
                        rev_posns)
            self.write_file(posns)
        except:
            print('run failed')

    def get_piston_positions(self, posns):
        """
        Gets piston position for each crank angle setting
        :param posns: Position list
        :return: List of position lists
        """
        try:
            for angle in range(0, 370, 10):
                self.actuator.Angle = angle
                Gui.runCommand("asm3CmdQuickSolve", 0)
                ppos = App.ActiveDocument.Constraint019.Label2
                posns.append(ppos)
        except:
            print("get_piston_positions failed")
        return posns

    def use_selected_cutoff(self, posns):
        """
        Gets valve positions for the selected cutoff
        :param posns: Position list
        :return: valve positions
        """
        try:
            for angle in range(0, 370, 10):
                # n.b. add 10 to desired upper range value
                row = []
                self.actuator.Angle = angle
                Gui.runCommand("asm3CmdQuickSolve", 0)
                vpos = App.ActiveDocument.Constraint020.Label2
                posns.append(vpos)
        except:
            print("Run() exception")
        return posns

    def set_cutoff(self, angle):
        print('set_cutoff entered', angle)
        try:
            print('trying')
            App.ActiveDocument.getObject('Sketch004').\
                setDatum(5, App.Units.Quantity(angle + ' deg'))
            App.ActiveDocument.recompute()
            print('set_cutoff', App.ActiveDocument.getObject('Sketch004').
                  getDatum(5, App.Units.Quantity))
        except:
            print('Setting cutoff failed')

    def get_current_positions(self):
        """Get distance (vpos) of valve mid point from cylinder mid point at
        current crank angle (cpos). The MeasurePoints Label2 gives the
        distance rounded to 2 decimal places.
        """
        try:
            cpos = self.actuator.Angle
            ppos = App.ActiveDocument.Constraint019.Label2
            vpos = App.ActiveDocument.Constraint020.Label2
            return cpos, ppos, vpos
        except:
            print("bollox - get_valve_pos()")
            # return 0, 0, 0

    def write_file(self, posns):
        fname = self.output_file_input.text()
        f = '/home/andy_X/Projects/Mechanical/Z7S/ValveGear/Results/' + \
            fname + '.csv'
        with open(f, 'w') as csv_file:
            writer = csv.writer(csv_file, quoting=csv.QUOTE_NONNUMERIC)
            print(writer)
            for row in posns:
                writer.writerow(row)

    def on_close(self):
        self.result = "Closed"
        self.close()


###############################################################################

def main():
    app_doc = App.ActiveDocument
    drivers = findTheDrivingConstraints(app_doc)
    if len(drivers) < 1:
        print("No driver found!")
    else:
        panel_list = []
        for each_driver in drivers:
            panel = ControlPanel(app_doc, each_driver)
            panel_list.append(panel)
        panel.exec_()

def findTheDrivingConstraints(document_object):
    # search through the Objects and find the driving constraint
    driver_list = []
    for each in document_object.Objects:
        if each.Label.endswith("Driver"):
            driving_constraint = each.Name
            driver_list.append(driving_constraint)
    return driver_list

###############################################################################

if __name__ == "__main__":
    main()
