import _thread
import matplotlib.pyplot as plt
import numpy as np
import os
import pickle
import pyqtgraph as pg
import socket
import sys
import threading
import time


from PIL import Image
from pyqtgraph import PlotWidget
from pyqtgraph.opengl import GLViewWidget
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from socket import SHUT_RDWR


ROOTPATH_g = (os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")).split("/Data")[0]

sys.path.append(ROOTPATH_g + "/Data/Work/UtilSrcCode/python-DeviceInterface")
from AV_DeviceInterface import EEGClientThread

sys.path.append(ROOTPATH_g + "/Data/Work/UtilSrcCode/python-SignalProc")
from AV_filters import AV_ShortFFT, AV_taper_signal


_fromUtf8 = lambda s: s

class UI(QtWidgets.QMainWindow):

    # def __init__(self, eegclientThread_p, refreshRate_p, main_p=None):
    def __init__(self, refreshRate_p, main_p=None):

        super(UI, self).__init__()

        # self.resize(660, 562)

        self.__main = main_p

        # self.showMaximized()
        # QMainWindow requires these two lines, otherwise we cannot set its layout.
        wid = QtGui.QWidget(self)
        self.setCentralWidget(wid)


        # pg.setConfigOption('background', (230, 233, 237))
        # pg.setConfigOption('background', (255, 255, 255))
        # pg.setConfigOption('background', None)
        # pg.setConfigOption('foreground', 'k')        

        ##### Set layouts
        main_layout = QtWidgets.QHBoxLayout()

        left_main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(left_main_layout)

        right_main_layout = QtWidgets.QVBoxLayout()        
        main_layout.addLayout(right_main_layout)

        top_left_main_layout = QtWidgets.QHBoxLayout()
        left_main_layout.addLayout(top_left_main_layout)

        bottom_left_main_layout = QtWidgets.QVBoxLayout()
        left_main_layout.addLayout(bottom_left_main_layout)

        left_top_left_main_layout = QtWidgets.QVBoxLayout()
        top_left_main_layout.addLayout(left_top_left_main_layout)

        ##### Create items
        self.__linePlot0 = PlotWidget(self)
        self.__linePlot0.setLabel("bottom", "Time", "Seconds")        
        self.__linePlot0.setLabel("left", "Raw data", "-")        
        self.__linePlot0.setObjectName("linePlot0")

        self.__linePlot0_TP9_PlotCurveItem = pg.PlotCurveItem()        
        self.__linePlot0_AF7_PlotCurveItem = pg.PlotCurveItem()
        self.__linePlot0_AF8_PlotCurveItem = pg.PlotCurveItem()
        self.__linePlot0_TP10_PlotCurveItem = pg.PlotCurveItem()
        self.__linePlot0_VLine_PlotCurveItem = pg.PlotCurveItem()

        self.__linePlot0.addItem(self.__linePlot0_TP9_PlotCurveItem)
        self.__linePlot0.addItem(self.__linePlot0_AF7_PlotCurveItem)
        self.__linePlot0.addItem(self.__linePlot0_AF8_PlotCurveItem)
        self.__linePlot0.addItem(self.__linePlot0_TP10_PlotCurveItem)
        self.__linePlot0.addItem(self.__linePlot0_VLine_PlotCurveItem)  

        self.__imgPlot0 = QtWidgets.QLabel(self)        
        myPixmap_l = QtGui.QPixmap(_fromUtf8("./pic/meditation.jpg"))
        pix_ratio_l = 1.0
        self.__imgPlot0.resize(myPixmap_l.size().width()*pix_ratio_l, myPixmap_l.size().height()*pix_ratio_l)
        # myScaledPixmap_l = myPixmap_l.scaled(self.__imgPlot0.size(), Qt.KeepAspectRatio)
        myScaledPixmap_l = myPixmap_l.scaled(self.__imgPlot0.size())
        self.__imgPlot0.setPixmap(myScaledPixmap_l)
        self.__imgPlot0.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        # FFT.
        self.__fftPlot0 = PlotWidget(self)
        self.__fftPlot0.setLabel("bottom", "Frequency", "Hz")        
        self.__fftPlot0.setLabel("left", "10log10(Power)", "-")                
        self.__fftPlot0.setObjectName("fftPlot0")

        self.__fftPlot0_PlotCurveItem = pg.PlotCurveItem()        

        self.__fftPlot0.addItem(self.__fftPlot0_PlotCurveItem)

        bottom_left_main_layout.addWidget(self.__linePlot0)
        bottom_left_main_layout.addWidget(self.__fftPlot0)
        top_left_main_layout.addWidget(self.__imgPlot0)



        wid.setLayout(main_layout)        

        ##### Set timer to update the plots.
        self.__refreshRatetimer = QtCore.QTimer(self)
        self.__refreshRatetimer.timeout.connect(self._plot)
        # self.__refreshRatetimer.start(1000/refreshRate_p) # in milliseconds
        self.__refreshRatetimer.setInterval(1000/refreshRate_p) # in milliseconds
        # self.__refreshRatetimer.stop()

        # self.__eegclientThread = eegclientThread_p
        self.__eegclientThread = None

        self.__taper_EEG_data_fft = None

        self.__time_begin_recording = None

        self.init()

    def init(self):
        # self.__samples_duration = 2 # [sec.]
        self.__samples_duration = 10 # [sec.]
        self.__Fs = 15000 # [Hz]
        # self.__Fs = 20000 # [Hz]
        # self.__linePlot0.setXRange(0, self.__samples_duration, padding=0)        
        
        pass

    def handleSignOut(self):
        pass

    def handleStop(self):
        pass

    def handlePause(self):
        pass

    def handleStart(self):
        pass

    def handleCalibrate(self):
        pass

    # def closeEvent(self, event):

    #     self.__eegclientThread.terminate()
    #     event.accept() # let the window close

    def closeEvent(self, event):
        
        self.stop()

        if self.__main is not None:
            event.ignore() # let the window close

            self.__main.hideMainUI()
            self.__main.showLogin()
        else:
            event.accept()

    def run(self):

        iaware_l = EEGClientThread(N_channels_p=1, samples_duration_p=self.__samples_duration)
        iaware_l.createTCPClient(buff_socket_size_p=4096, server_ip_p="192.168.4.1", server_port_p=5000, Fs_senddata_p=20, Fs_p=self.__Fs, Name_p="iAwareClient")
        iaware_l.start()

        self.__eegclientThread = iaware_l
        self.__refreshRatetimer.start()

        idx_samples_l, samples_l = self.__eegclientThread.getRawData()

        _, self.__taper_EEG_data_fft = AV_taper_signal(signal_p=np.zeros(np.shape(samples_l)[1]), typeTaper_p="hann")

        self.__idx_samples = np.arange(np.shape(samples_l)[1])
        self.__time_lin = self.__idx_samples*(1/self.__Fs)

        print(self.__time_lin)

        self.showMaximized()

    def stop(self):

        if self.__eegclientThread is not None:
            self.__eegclientThread.terminate()

        self.__refreshRatetimer.stop()

    def exit(self):

        if self.__eegclientThread is not None:
            self.__eegclientThread.terminate()

        self.__refreshRatetimer.stop()            

        self.close()

    ##### Refresh
    def _plot(self):
        try:
            if self.__time_begin_recording is None:
                self.__time_begin_recording = np.floor(time.time()*1000)
            else:
                if (np.floor(time.time()*1000) - self.__time_begin_recording) > 20*1000:
                    self.__time_begin_recording = self.__time_begin_recording + 100000000

                    idx_samples_l, samples_l = self.__eegclientThread.getRawData()
                    samples_l = np.take(a=samples_l, indices=(self.__idx_samples + idx_samples_l), mode='wrap')

                    # with open("./vag_samples_v1_finger", "wb+") as fp:
                    # with open("./vag_samples_nothing", "wb+") as fp:                    
                    with open("./vag_samples_rubtable", "wb+") as fp:                    
                        pickle.dump([samples_l], fp)
                        fp.close()

                        print("Successful recording data.")  


            # freq_positive_l, fft_pw_ch1_l = self.__eegclientThread.getFFTPower()
            # print(fft_pw_ch1_l)

            idx_samples_l, samples_l = self.__eegclientThread.getRawData()

        # print(idx_samples_l)
        # print(np.shape(samples_l))        

            # print(idx_samples_l)
            # print(np.shape(samples_l))

            # self.__linePlot0_PlotCurveItems[i_channels_g].setData(x=time_downsampled_EEG_data_linePlot0_g, y=filtered_l)            

            # print(np.shape(samples_l[0,:]))

            # y_min_linePlot0_g = np.min(samples_l[0, idx_downsampled_EEG_data_linePlot0_g, i_channels_g])
            # y_min_linePlot0_g = y_min_linePlot0_g - 0.1*y_min_linePlot0_g
            # y_max_linePlot0_g = np.max(samples_l[0, idx_downsampled_EEG_data_linePlot0_g, i_channels_g])
            # y_max_linePlot0_g = y_max_linePlot0_g + 0.1*y_max_linePlot0_g
            # self.__linePlot0_PlotCurveItems[-1].setData(x=[(i_EEG_data_linePlot0_g*T_x_ranges_linePlot0_g)/N_EEG_data_linePlot0_g, (i_EEG_data_linePlot0_g*T_x_ranges_linePlot0_g)/N_EEG_data_linePlot0_g], y=[y_min_linePlot0_g, y_max_linePlot0_g])

            # self.__linePlot0_TP9_PlotCurveItem.setData(x=np.arange(int(self.__Fs*self.__samples_duration)), y=samples_l[0, :])            
            self.__linePlot0_TP9_PlotCurveItem.setData(x=self.__time_lin, y=samples_l[0, :])            
            

            modulo_samples_l = np.take(a=samples_l, indices=(self.__idx_samples + idx_samples_l), mode='wrap')


            # self.__linePlot0_TP9_PlotCurveItem.setData(x=time_downsampled_EEG_data_linePlot0_g, y=filtered_l)            
            # self.__linePlot0_TP9_PlotCurveItem.setData(x=freq_positive_l, y=fft_pw_ch1_l)            


        # self.__img.setImage(img_EEG_data_fft_g, autoLevels=False)

            freq_positive_l, _, _, fft_pw_ch1_l, _, _, _    = AV_ShortFFT(fs_p=self.__Fs, signal_p=modulo_samples_l - np.mean(modulo_samples_l), typeTaper_p="hann", taper_p=self.__taper_EEG_data_fft)

            with np.errstate(divide='ignore',invalid='ignore'):
                # avg_pw_l = fft_pw_ch1_l/np.nanmax(fft_pw_ch1_l) 
                avg_pw_l = 10*np.log10(fft_pw_ch1_l)

            self.__fftPlot0_PlotCurveItem.setData(x=freq_positive_l, y=avg_pw_l)            
            # self.__spectrogramPlot0_ImageItem.setImage(img_EEG_data_fft_g, autoLevels=False)

        except Exception as e:
            print(e)
            pass      
           

if __name__ == '__main__':
    app_l = QtWidgets.QApplication(sys.argv)

    window_l = UI(refreshRate_p=20)
    window_l.run()
    window_l.show()

    sys.exit(app_l.exec_())

