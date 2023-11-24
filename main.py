import numpy as np
import pyqtgraph as pg
from PyQt5 import QtCore, QtWidgets,QtGui
# from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSlider, QLabel, QLineEdit
import pyqtgraph as pg
import sys
from ctypes import *
from mocap_processor import MocapStreamer
from fes import Fes_streamer, TSHapticMasterMultiplier
from suit_handler import Teslasuit
import torch

class App(QtWidgets.QMainWindow):
    def __init__(self,parent=None):
        super(App, self).__init__(parent)
        self.suit=Teslasuit()
        self.suit.connect_suit()
        self.streamer = MocapStreamer(self.suit)
  
        # self.biomechanics=MocapHandler()
 
        self.suit.load_asset('assets/left_tib.ts_asset', 'Left_tibialis')
        self.suit.load_asset('assets/right_tib.ts_asset', 'Right_tibialis')
        self.suit.load_asset('assets/left_gastr.ts_asset', 'Left_gastrocnemius')
        self.suit.load_asset('assets/right_gastr.ts_asset', 'Right_gastrocnemius')
        self.suit.load_asset('assets/left_quad.ts_asset', 'Left_quadriceps')
        self.suit.load_asset('assets/right_quad.ts_asset', 'Right_quadriceps')
        self.suit.load_asset('assets/left_hamstr.ts_asset', 'Left_hamstring')
        self.suit.load_asset('assets/right_hamstr.ts_asset', 'Right_hamstring')

        self.stimulator=Fes_streamer(self.suit.asset_id_list, self.suit.haptic)
        def callback(multiplier, opaque):
            self.slider.setValue(int(multiplier.contents.pulse_width * 100))

        self.subscribe_callback_proto = CFUNCTYPE(None, POINTER(TSHapticMasterMultiplier), c_void_p)
        self.callback_fn = self.subscribe_callback_proto(callback)
        # self.stimulator.teslasuit_api_dll.ts_haptic_subscribe_on_master_multiplier_update(self.callback_fn, py_object(self))

        self.mainbox = QtWidgets.QWidget()
        self.setCentralWidget(self.mainbox)  
        self.mainbox.setLayout(QtWidgets.QVBoxLayout())

        self.PlotBox = QtWidgets.QHBoxLayout()
        self.mainbox.layout().addLayout(self.PlotBox)

        self.Leftbox = QtWidgets.QVBoxLayout()
        self.PlotBox.layout().addLayout(self.Leftbox)

        self.Rightbox = QtWidgets.QVBoxLayout()
        self.PlotBox.layout().addLayout(self.Rightbox)


        self.left_leg_box = QtWidgets.QCheckBox('Left leg stimulation')
        self.left_leg_box.stateChanged.connect(self.LeftLegStateChanged)
        self.Leftbox.addWidget(self.left_leg_box)

        self.Left_data_canvas = pg.GraphicsLayoutWidget()
        self.Leftbox.layout().addWidget(self.Left_data_canvas)

        self.Left_data_status = QtWidgets.QVBoxLayout()
        self.Leftbox.addLayout(self.Left_data_status)

        self.left_front_box = QtWidgets.QCheckBox('Left leg front contact')
        self.left_front_box.stateChanged.connect(self.Left_leg_front_contact) 
        self.Left_data_status.addWidget(self.left_front_box)

        self.left_back_box = QtWidgets.QCheckBox('Left leg heel contact')
        self.left_back_box.stateChanged.connect(self.Left_leg_back_contact)
        self.Left_data_status.addWidget(self.left_back_box)

        self.Left_haptic_canvas = pg.GraphicsLayoutWidget()
        self.Leftbox.layout().addWidget(self.Left_haptic_canvas)

        self.Left_haptic_status = QtWidgets.QHBoxLayout()
        self.Leftbox.addLayout(self.Left_haptic_status)


        self.Left_haptic_status_c1=QtWidgets.QVBoxLayout()
        self.Left_haptic_status.addLayout(self.Left_haptic_status_c1)

        self.Left_haptic_status_c2=QtWidgets.QVBoxLayout()
        self.Left_haptic_status.addLayout(self.Left_haptic_status_c2)

        self.Left_haptic_status_c3=QtWidgets.QVBoxLayout()
        self.Left_haptic_status.addLayout(self.Left_haptic_status_c3)

        self.Left_haptic_status_c4=QtWidgets.QVBoxLayout()
        self.Left_haptic_status.addLayout(self.Left_haptic_status_c4)

        self.Left_haptic_status_c5=QtWidgets.QVBoxLayout()
        self.Left_haptic_status.addLayout(self.Left_haptic_status_c5)


        self.Left_quadriceps_box = QtWidgets.QCheckBox('Left leg quadriceps')
        self.Left_quadriceps_box.stateChanged.connect(self.LeftQuadricepsChecked)
        self.Left_haptic_status_c1.addWidget(self.Left_quadriceps_box)

        self.Left_hamstring_box = QtWidgets.QCheckBox('Left leg hamstring')
        self.Left_hamstring_box.stateChanged.connect(self.LeftHamstringhecked)
        self.Left_haptic_status_c1.addWidget(self.Left_hamstring_box)

        self.Left_gastrocnemius_box = QtWidgets.QCheckBox('Left leg gastrocnemius')
        self.Left_gastrocnemius_box.stateChanged.connect(self.LeftGastrocnemiusChecked)
        self.Left_haptic_status_c1.addWidget(self.Left_gastrocnemius_box)

        self.Left_tibialis_box = QtWidgets.QCheckBox('Left leg tibialis anterior')
        self.Left_tibialis_box.stateChanged.connect(self.LeftTibialisChecked)
        self.Left_haptic_status_c1.addWidget(self.Left_tibialis_box)


        self.left_delay_label_1 = QLabel(self)
        self.left_delay_label_1.setText('Delay')
        self.left_delay_label_2 = QLabel(self)
        self.left_delay_label_2.setText('Delay')
        self.left_delay_label_3 = QLabel(self)
        self.left_delay_label_3.setText('Delay')
        self.left_delay_label_4 = QLabel(self)
        self.left_delay_label_4.setText('Delay')
        self.Left_haptic_status_c2.addWidget(self.left_delay_label_1)
        self.Left_haptic_status_c2.addWidget(self.left_delay_label_2)
        self.Left_haptic_status_c2.addWidget(self.left_delay_label_3)
        self.Left_haptic_status_c2.addWidget(self.left_delay_label_4)

        
        self.left_quadriceps_delay=QLineEdit(str(self.stimulator.haptic_delay['Left_quadriceps']))
        self.left_quadriceps_delay.textChanged.connect(self.left_quadriceps_delay_change)
        self.Left_haptic_status_c3.addWidget(self.left_quadriceps_delay)

        self.left_hamstring_delay=QLineEdit(str(self.stimulator.haptic_delay['Left_hamstring']))
        self.left_hamstring_delay.textChanged.connect(self.left_hamstring_delay_change)
        self.Left_haptic_status_c3.addWidget(self.left_hamstring_delay)

        self.left_gastrocnemius_delay=QLineEdit(str(self.stimulator.haptic_delay['Left_gastrocnemius']))
        self.left_gastrocnemius_delay.textChanged.connect(self.left_gastrocnemius_delay_change)
        self.Left_haptic_status_c3.addWidget(self.left_gastrocnemius_delay)

        self.left_tibialis_delay=QLineEdit(str(self.stimulator.haptic_delay['Left_tibialis']))
        self.left_tibialis_delay.textChanged.connect(self.left_tibialis_delay_change)
        self.Left_haptic_status_c3.addWidget(self.left_tibialis_delay)

        self.left_stimulation_label_1 = QLabel(self)
        self.left_stimulation_label_1.setText('Duration')
        self.left_stimulation_label_2 = QLabel(self)
        self.left_stimulation_label_2.setText('Duration')
        self.left_stimulation_label_3 = QLabel(self)
        self.left_stimulation_label_3.setText('Duration')
        self.left_stimulation_label_4 = QLabel(self)
        self.left_stimulation_label_4.setText('Duration')

        self.Left_haptic_status_c4.addWidget(self.left_stimulation_label_1)
        self.Left_haptic_status_c4.addWidget(self.left_stimulation_label_2)
        self.Left_haptic_status_c4.addWidget(self.left_stimulation_label_3)
        self.Left_haptic_status_c4.addWidget(self.left_stimulation_label_4)
                                        

        self.left_quadriceps_stimulation=QLineEdit(str(self.stimulator.haptic_len['Left_quadriceps']))
        self.left_quadriceps_stimulation.textChanged.connect(self.left_quadriceps_duration_change)
        self.Left_haptic_status_c5.addWidget(self.left_quadriceps_stimulation)

        self.left_hamstring_stimulation=QLineEdit(str(self.stimulator.haptic_len['Left_hamstring']))
        self.left_hamstring_stimulation.textChanged.connect(self.left_hamstring_duration_change)
        self.Left_haptic_status_c5.addWidget(self.left_hamstring_stimulation)

        self.left_gastrocnemius_stimulation=QLineEdit(str(self.stimulator.haptic_len['Left_gastrocnemius']))
        self.left_gastrocnemius_stimulation.textChanged.connect(self.left_gastrocnemius_duration_change)
        self.Left_haptic_status_c5.addWidget(self.left_gastrocnemius_stimulation)

        self.left_tibialis_stimulation=QLineEdit(str(self.stimulator.haptic_len['Left_tibialis']))
        self.left_tibialis_stimulation.textChanged.connect(self.left_tibialis_duration_change)
        self.Left_haptic_status_c5.addWidget(self.left_tibialis_stimulation)



        self.right_leg_box = QtWidgets.QCheckBox('Right leg stimulation')
        self.right_leg_box.stateChanged.connect(self.RightLegStateChanged)
        self.Rightbox.addWidget(self.right_leg_box)

        self.Right_data_canvas = pg.GraphicsLayoutWidget()
        self.Rightbox.layout().addWidget(self.Right_data_canvas)

        self.Right_data_status = QtWidgets.QVBoxLayout()
        self.Rightbox.addLayout(self.Right_data_status)

        self.right_front_box = QtWidgets.QCheckBox('Right leg front contact')
        self.right_front_box.stateChanged.connect(self.Right_leg_front_contact)
        self.Right_data_status.addWidget(self.right_front_box)

        self.right_back_box = QtWidgets.QCheckBox('Right leg heel contact')
        self.right_back_box.stateChanged.connect(self.Right_leg_back_contact) 
        self.Right_data_status.addWidget(self.right_back_box)

        self.Right_haptic_canvas = pg.GraphicsLayoutWidget()
        self.Rightbox.layout().addWidget(self.Right_haptic_canvas)

        self.Right_haptic_status = QtWidgets.QHBoxLayout()
        self.Rightbox.addLayout(self.Right_haptic_status)

        self.Right_haptic_status_c1=QtWidgets.QVBoxLayout()
        self.Right_haptic_status.addLayout(self.Right_haptic_status_c1)

        self.Right_haptic_status_c2=QtWidgets.QVBoxLayout()
        self.Right_haptic_status.addLayout(self.Right_haptic_status_c2)

        self.Right_haptic_status_c3=QtWidgets.QVBoxLayout()
        self.Right_haptic_status.addLayout(self.Right_haptic_status_c3)

        self.Right_haptic_status_c4=QtWidgets.QVBoxLayout()
        self.Right_haptic_status.addLayout(self.Right_haptic_status_c4)

        self.Right_haptic_status_c5=QtWidgets.QVBoxLayout()
        self.Right_haptic_status.addLayout(self.Right_haptic_status_c5)


        self.Right_quadriceps_box = QtWidgets.QCheckBox('Right leg quadriceps')
        self.Right_quadriceps_box.stateChanged.connect(self.RightQuadricepsChecked)
        self.Right_haptic_status_c1.addWidget(self.Right_quadriceps_box)

        self.Right_hamstring_box = QtWidgets.QCheckBox('Right leg hamstring')
        self.Right_hamstring_box.stateChanged.connect(self.RightHamstringhecked)
        self.Right_haptic_status_c1.addWidget(self.Right_hamstring_box)

        self.Right_gastrocnemius_box = QtWidgets.QCheckBox('Right leg gastrocnemius')
        self.Right_gastrocnemius_box.stateChanged.connect(self.RightGastrocnemiusChecked)
        self.Right_haptic_status_c1.addWidget(self.Right_gastrocnemius_box)

        self.Right_tibialis_box = QtWidgets.QCheckBox('Right leg tibialis anterior')
        self.Right_tibialis_box.stateChanged.connect(self.RightTibialisChecked)
        self.Right_haptic_status_c1.addWidget(self.Right_tibialis_box)

        self.right_delay_label_1 = QLabel(self)
        self.right_delay_label_1.setText('Delay')
        self.right_delay_label_2 = QLabel(self)
        self.right_delay_label_2.setText('Delay')
        self.right_delay_label_3 = QLabel(self)
        self.right_delay_label_3.setText('Delay')
        self.right_delay_label_4 = QLabel(self)
        self.right_delay_label_4.setText('Delay')
        self.Right_haptic_status_c2.addWidget(self.right_delay_label_1)
        self.Right_haptic_status_c2.addWidget(self.right_delay_label_2)
        self.Right_haptic_status_c2.addWidget(self.right_delay_label_3)
        self.Right_haptic_status_c2.addWidget(self.right_delay_label_4)

        self.right_quadriceps_delay=QLineEdit(str(self.stimulator.haptic_delay['Right_quadriceps']))
        self.right_quadriceps_delay.textChanged.connect(self.right_quadriceps_delay_change)
        self.Right_haptic_status_c3.addWidget(self.right_quadriceps_delay)

        self.right_hamstring_delay=QLineEdit(str(self.stimulator.haptic_delay['Right_hamstring']))
        self.right_hamstring_delay.textChanged.connect(self.right_hamstring_delay_change)
        self.Right_haptic_status_c3.addWidget(self.right_hamstring_delay)

        self.right_gastrocnemius_delay=QLineEdit(str(self.stimulator.haptic_delay['Right_gastrocnemius']))
        self.right_gastrocnemius_delay.textChanged.connect(self.right_gastrocnemius_delay_change)
        self.Right_haptic_status_c3.addWidget(self.right_gastrocnemius_delay)

        self.right_tibialis_delay=QLineEdit(str(self.stimulator.haptic_delay['Right_tibialis']))
        self.right_tibialis_delay.textChanged.connect(self.right_tibialis_delay_change)
        self.Right_haptic_status_c3.addWidget(self.right_tibialis_delay)


        
        self.right_stimulation_label_1 = QLabel(self)
        self.right_stimulation_label_1.setText('Duration')
        self.right_stimulation_label_2 = QLabel(self)
        self.right_stimulation_label_2.setText('Duration')
        self.right_stimulation_label_3 = QLabel(self)
        self.right_stimulation_label_3.setText('Duration')
        self.right_stimulation_label_4 = QLabel(self)
        self.right_stimulation_label_4.setText('Duration')
        self.Right_haptic_status_c4.addWidget(self.right_stimulation_label_1)
        self.Right_haptic_status_c4.addWidget(self.right_stimulation_label_2)
        self.Right_haptic_status_c4.addWidget(self.right_stimulation_label_3)
        self.Right_haptic_status_c4.addWidget(self.right_stimulation_label_4)


        self.right_quadriceps_stimulation=QLineEdit(str(self.stimulator.haptic_len['Right_quadriceps']))
        self.right_quadriceps_stimulation.textChanged.connect(self.right_quadriceps_duration_change)
        self.Right_haptic_status_c5.addWidget(self.right_quadriceps_stimulation)

        self.right_hamstring_stimulation=QLineEdit(str(self.stimulator.haptic_len['Right_hamstring']))
        self.right_hamstring_stimulation.textChanged.connect(self.right_hamstring_duration_change)
        self.Right_haptic_status_c5.addWidget(self.right_hamstring_stimulation)

        self.right_gastrocnemius_stimulation=QLineEdit(str(self.stimulator.haptic_len['Right_gastrocnemius']))
        self.right_gastrocnemius_stimulation.textChanged.connect(self.right_gastrocnemius_duration_change)
        self.Right_haptic_status_c5.addWidget(self.right_gastrocnemius_stimulation)

        self.right_tibialis_stimulation=QLineEdit(str(self.stimulator.haptic_len['Right_tibialis']))
        self.right_tibialis_stimulation.textChanged.connect(self.right_tibialis_duration_change)
        self.Right_haptic_status_c5.addWidget(self.right_tibialis_stimulation)


        self.status_panel = QtWidgets.QHBoxLayout()
        self.mainbox.layout().addLayout(self.status_panel)

        self.pause_button = QtWidgets.QPushButton('Pause')
        self.pause_button.setMinimumWidth(250)
        self.pause_button.setMaximumWidth(350)


        self.slider = QSlider(QtCore.Qt.Horizontal, self)
        self.slider.setRange(0, 100)
        self.slider.setMinimumWidth(600)


        # initial_get = TSHapticMasterMultiplier()

        # self.stimulator.teslasuit_api_dll.ts_haptic_get_master_multiplier(pointer(initial_get))
        self.slider.setValue(100)
        self.slider.valueChanged[int].connect(self.changeSliderValue)

        self.slider_label = QLabel('Haptic power: ' + str(self.slider.value()), self)
        self.slider_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        self.status_panel.addWidget(self.slider_label)
        self.status_panel.addSpacing(10)
        self.status_panel.layout().addWidget(self.slider, alignment=QtCore.Qt.AlignLeft)
        self.status_panel.addSpacing(15)
        self.Left_mean_angle_plot = self.Left_data_canvas.addPlot()
        self.Left_mean_angle_plot.addLegend(offset=(30, 30))

        # self.Left_current_angle_plot = self.Left_data_canvas.addPlot()
        # self.Left_current_angle_plot.addLegend(offset=(30, 30))

        self.Right_data_plot = self.Right_data_canvas.addPlot()
        self.Right_data_plot.addLegend(offset=(30, 30))

        self.Left_Haptic_plot1 = self.Left_haptic_canvas.addPlot(row=0,col=0)
        self.Left_Haptic_plot2 = self.Left_haptic_canvas.addPlot(row=1,col=0)
        self.Left_Haptic_plot3 = self.Left_haptic_canvas.addPlot(row=3,col=0)
        self.Left_Haptic_plot4 = self.Left_haptic_canvas.addPlot(row=4,col=0)

        self.Left_Haptic_plot1.addLegend(offset=(3,3))
        self.Left_Haptic_plot2.addLegend(offset=(3,3))
        self.Left_Haptic_plot3.addLegend(offset=(3,3))
        self.Left_Haptic_plot4.addLegend(offset=(3,3))


        self.Right_Haptic_plot1 = self.Right_haptic_canvas.addPlot(row=0,col=0)
        self.Right_Haptic_plot2 = self.Right_haptic_canvas.addPlot(row=1,col=0)
        self.Right_Haptic_plot3 = self.Right_haptic_canvas.addPlot(row=2,col=0)
        self.Right_Haptic_plot4 = self.Right_haptic_canvas.addPlot(row=3,col=0)
        self.Right_Haptic_plot1.addLegend(offset=(3, 3))
        self.Right_Haptic_plot2.addLegend(offset=(3, 3))
        self.Right_Haptic_plot3.addLegend(offset=(3, 3))
        self.Right_Haptic_plot4.addLegend(offset=(3, 3))

        self.x = np.arange(0,400)
        # self.drawer1 = list(np.zeros(400))
        self.drawer2 = list(np.zeros(400))
        # self.drawer3 = list(np.zeros(400))
        self.drawer4 = list(np.zeros(400))

        self.drawer5 = list(np.zeros(400))
        self.drawer6 = list(np.zeros(400))
        self.drawer7 = list(np.zeros(400))
        self.drawer8 = list(np.zeros(400))

        self.drawer9 = list(np.zeros(400))
        self.drawer10 = list(np.zeros(400))
        self.drawer11 = list(np.zeros(400))
        self.drawer12 = list(np.zeros(400))

        # self.left_mean_angle_drawer= list(np.zeros(400))
        # self.left_current_angle_drawer=list(np.zeros(400))


        self.widget5 = self.Left_Haptic_plot1.plot(x=self.x,y=self.drawer5 ,fillLevel=0,fillBrush=QtGui.QColor('papayawhip'), name='Left quadriceps stimualtion')
        self.widget6 = self.Left_Haptic_plot2.plot(x=self.x,y=self.drawer6 ,fillLevel=0,fillBrush=QtGui.QColor('wheat'), name='Left hamstrings stimualtion')
        self.widget7 = self.Left_Haptic_plot3.plot(x=self.x,y=self.drawer7 ,fillLevel=0,fillBrush=QtGui.QColor('lightgrey'), name='Left  gastrocnemius stimualtion')
        self.widget8 = self.Left_Haptic_plot4.plot(x=self.x,y=self.drawer8 ,fillLevel=0,fillBrush=QtGui.QColor('silver'), name='Left tibialis  stimualtion')

        self.widget9 = self.Right_Haptic_plot1.plot(x=self.x,y=self.drawer9 ,fillLevel=0,fillBrush=QtGui.QColor('papayawhip'), name='Right quadriceps stimualtion')
        self.widget10 = self.Right_Haptic_plot2.plot(x=self.x,y=self.drawer10 ,fillLevel=0,fillBrush=QtGui.QColor('wheat'), name='Right hamstring  stimualtion')
        self.widget11 = self.Right_Haptic_plot3.plot(x=self.x,y=self.drawer11 ,fillLevel=0,fillBrush=QtGui.QColor('lightgrey'), name='Right  gastrocnemius stimualtion')
        self.widget12 = self.Right_Haptic_plot4.plot(x=self.x,y=self.drawer12 ,fillLevel=0,fillBrush=QtGui.QColor('silver'), name='Right tibialis stimualtion')

        # self.widget1 = self.Left_current_angle_plot.plot(x=self.x,y=self.left_current_angle_drawer ,pen=QtGui.QColor('red'), name='Left foot front')
        # self.widget2 = self.Left_current_angle_plot.plot(x=self.x,y=self.left_current_angle_drawer ,pen=QtGui.QColor('orange'), name='Left foot back')
        # self.widget1 = self.Left_mean_angle_plot.plot(x=self.x,y=self.drawer1 ,pen=QtGui.QColor('red'), name='Left foot front')
        self.widget2 = self.Left_mean_angle_plot.plot(x=self.x,y=self.drawer2 ,pen=QtGui.QColor('orange'), name='Left foot heel strike')
        
        # self.widget3 = self.Right_data_plot.plot(x=self.x,y=self.drawer3 ,pen=QtGui.QColor('blue'), name='Left foot front')
        self.widget4 = self.Right_data_plot.plot(x=self.x,y=self.drawer4 ,pen=QtGui.QColor('green'), name='Right foot heel strike')

        # self.widget1 = self.Left_data_plot.plot(x=self.x,y=self.drawer1 ,pen=QtGui.QColor('red'), name='Left foot front')
        # self.widget2 = self.Left_data_plot.plot(x=self.x,y=self.drawer2 ,pen=QtGui.QColor('orange'), name='Left foot back')
        # self.widget3 = self.Right_data_plot.plot(x=self.x,y=self.drawer3 ,pen=QtGui.QColor('blue'), name='Left foot front')
        # self.widget4 = self.Right_data_plot.plot(x=self.x,y=self.drawer4 ,pen=QtGui.QColor('green'), name='Left foot back')

        self.left_front_box.setCheckState(QtCore.Qt.Checked)
        self.left_back_box.setCheckState(QtCore.Qt.Checked)
        self.right_front_box.setCheckState(QtCore.Qt.Checked)
        self.right_back_box.setCheckState(QtCore.Qt.Checked)

        
        self.view_update_timer = QtCore.QTimer()
        self.view_update_timer.timeout.connect(lambda: self._update())
        self.view_update_timer.start(50)


    def left_quadriceps_duration_change(self):
        self.stimulator.haptic_len['Left_quadriceps']=float(self.left_quadriceps_stimulation.text())
    def left_hamstring_duration_change(self):
        self.stimulator.haptic_len['Left_hamstring']=float(self.left_hamstring_stimulation.text())
    def left_gastrocnemius_duration_change(self):
        self.stimulator.haptic_len['Left_gastrocnemius']=float(self.left_gastrocnemius_stimulation.text())
    def left_tibialis_duration_change(self):
        self.stimulator.haptic_len['Left_tibialis']=float(self.left_tibialis_stimulation.text())

    def right_quadriceps_duration_change(self):
        self.stimulator.haptic_len['Right_quadriceps']=float(self.right_quadriceps_stimulation.text())
    def right_hamstring_duration_change(self):
        self.stimulator.haptic_len['Right_hamstring']=float(self.right_hamstring_stimulation.text())
    def right_gastrocnemius_duration_change(self):
        self.stimulator.haptic_len['Right_gastrocnemius']=float(self.right_quadriceps_stimulation.text())
    def right_tibialis_duration_change(self):
        self.stimulator.haptic_len['Right_tibialis']=float(self.right_tibialis_stimulation.text())

    def left_quadriceps_delay_change(self):
        self.stimulator.haptic_delay['Left_quadriceps']=float(self.left_quadriceps_delay.text())
        print(self.stimulator.haptic_delay['Left_quadriceps'])
    def left_hamstring_delay_change(self):
        self.stimulator.haptic_delay['Left_hamstring']=float(self.left_hamstring_delay.text())
    def left_gastrocnemius_delay_change(self):
        self.stimulator.haptic_delay['Left_gastrocnemius']=float(self.left_gastrocnemius_delay.text())
        print(self.stimulator.haptic_delay['Left_gastrocnemius'])
    def left_tibialis_delay_change(self):
        self.stimulator.haptic_delay['Left_tibialis']=float(self.left_tibialis_delay.text())
        print(self.stimulator.haptic_delay['Left_tibialis'])

    def right_quadriceps_delay_change(self):
        self.stimulator.haptic_delay['Right_quadriceps']=float(self.right_quadriceps_delay.text())
    def right_hamstring_delay_change(self):
        self.stimulator.haptic_delay['Right_hamstring']=float(self.right_hamstring_delay.text())
    def right_gastrocnemius_delay_change(self):
        self.stimulator.haptic_delay['Right_gastrocnemius']=float(self.right_gastrocnemius_delay.text())
    def right_tibialis_delay_change(self):
        self.stimulator.haptic_delay['Right_tibialis']=float(self.right_tibialis_delay.text())


    def changeSliderValue(self):
        value = self.slider.value()

        mult = TSHapticMasterMultiplier()
        mult.pulse_width = value/100
        mult.temperature = 1.0
        mult.frequency = 1.0
        mult.amplitude = 1.0


        self.suit.haptic.get_master_multiplier(c_uint32(0))
        
        self.slider_label.setText('Haptic power: ' + str(value))


    def _updateInput(self):
        self.streamer.update()

        self.streamer.get_features()
        self.input=self.streamer.run_model()
        # self.biomechanics.get_left_knee_angle()  

    def _updateOutput(self):
        self.stimulator.run_walking_fes(result=self.input)
        self.stimulator._update_playing_assets()


    def _update(self):

        self._updateInput()
        self._updateOutput()
        self.stimulator._update_playing(self.suit.haptic)

        # self.left_current_angle_drawer[0:-1]=self.left_current_angle_drawer[1:]
        # self.left_current_angle_drawer[-1]=self.biomechanics.lk_angle
        
        # self.drawer1[0:-1]=self.drawer1[1:]
        # self.drawer1[-1]=self.input[0]*1
        self.drawer2[0:-1]=self.drawer2[1:]
        self.drawer2[-1]=self.input[1]*1
        # self.drawer3[0:-1]=self.drawer3[1:]
        # self.drawer3[-1]=self.input[2]*(1)
        self.drawer4[0:-1]=self.drawer4[1:]
        self.drawer4[-1]=self.input[3]*(1)
        self.drawer5[0:-1]=self.drawer5[1:]
        self.drawer5[-1]=self.stimulator.haptic_playing['Left_quadriceps']
        self.drawer6[0:-1]=self.drawer6[1:]
        self.drawer6[-1]=self.stimulator.haptic_playing['Left_hamstring']
        self.drawer7[0:-1]=self.drawer7[1:]
        self.drawer7[-1]=self.stimulator.haptic_playing['Left_gastrocnemius']
        self.drawer8[0:-1]=self.drawer8[1:]
        self.drawer8[-1]=self.stimulator.haptic_playing['Left_tibialis']

        self.drawer9[0:-1]=self.drawer9[1:]
        self.drawer9[-1]=self.stimulator.haptic_playing['Right_quadriceps']
        self.drawer10[0:-1]=self.drawer10[1:]
        self.drawer10[-1]=self.stimulator.haptic_playing['Right_hamstring']
        self.drawer11[0:-1]=self.drawer11[1:]
        self.drawer11[-1]=self.stimulator.haptic_playing['Right_gastrocnemius']
        self.drawer12[0:-1]=self.drawer12[1:]
        self.drawer12[-1]=self.stimulator.haptic_playing['Right_tibialis']
        self.x = np.arange(0,400)


        # self.widget1.setData(x=self.x,y=self.left_current_angle_drawer)
        self.widget2.setData(x=self.x,y=self.drawer2)
        # self.widget3.setData(x=self.x,y=self.drawer3)
        self.widget4.setData(x=self.x,y=self.drawer4)
        self.widget5.setData(x=self.x,y=self.drawer5)
        self.widget6.setData(x=self.x,y=self.drawer6)
        self.widget7.setData(x=self.x,y=self.drawer7)
        self.widget8.setData(x=self.x,y=self.drawer8)
        self.widget9.setData(x=self.x,y=self.drawer9)
        self.widget10.setData(x=self.x,y=self.drawer10)
        self.widget11.setData(x=self.x,y=self.drawer11)
        self.widget12.setData(x=self.x,y=self.drawer12)


    def pauseButtonClicked(self, event):
        self.paused = not self.paused

        self.pause_button.setText('Unpause' if self.paused else 'Pause')
        if self.paused:
            self.suit.stop_mocap_streaming()
            self.view_update_timer.stop()
        else:
            self.suit.start_mocap_streaming()
            self.view_update_timer.start(0.1)

    def Left_leg_front_contact(self, state):
        pass
        # self.widget1.setVisible(state)

    def Left_leg_back_contact(self, state):
        self.widget2.setVisible(state)

    def Right_leg_front_contact(self, state):
        pass
        # self.widget3.setVisible(state)

    def Right_leg_back_contact(self, state):
        self.widget4.setVisible(state)

    def LeftLegStateChanged(self,state):
        self.stimulator.ChangeLegState('left',state)
        self.Left_quadriceps_box.setCheckState(state)
        self.Left_tibialis_box.setCheckState(state)
        self.Left_hamstring_box.setCheckState(state)
        self.Left_gastrocnemius_box.setCheckState(state)
        print(state)

    def LeftTibialisChecked(self,state):
        self.stimulator.ChangeHapticChecked('left','Left_tibialis',state)

    def LeftQuadricepsChecked(self,state):
        self.stimulator.ChangeHapticChecked('left','Left_quadriceps',state)

    def LeftHamstringhecked(self,state):
        self.stimulator.ChangeHapticChecked('left','Left_hamstring',state)

    def LeftGastrocnemiusChecked(self,state):
        self.stimulator.ChangeHapticChecked('left','Left_gastrocnemius',state)
    
    def RightLegStateChanged(self,state):
        self.stimulator.ChangeLegState('right',state)
        self.Right_quadriceps_box.setCheckState(state)
        self.Right_tibialis_box.setCheckState(state)
        self.Right_hamstring_box.setCheckState(state)
        self.Right_gastrocnemius_box.setCheckState(state)
        print(state)  

    def RightTibialisChecked(self,state):
        self.stimulator.ChangeHapticChecked('right','Right_tibialis',state)

    def RightQuadricepsChecked(self,state):
        self.stimulator.ChangeHapticChecked('right','Right_quadriceps',state)

    def RightHamstringhecked(self,state):
        self.stimulator.ChangeHapticChecked('right','Right_hamstring',state)

    def RightGastrocnemiusChecked(self,state):
        self.stimulator.ChangeHapticChecked('right','Right_gastrocnemius',state)
        
if 1 == 1:
    app = QtWidgets.QApplication(sys.argv)
    thisapp = App()
    thisapp.showMaximized()
    sys.exit(app.exec_())
