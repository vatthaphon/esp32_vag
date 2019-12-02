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

        # Spectrogram.
        self.__spectrogramPlot0 = PlotWidget(self)
        self.__spectrogramPlot0.setObjectName("spectrogramPlot0")

        self.__spectrogramPlot0_ImageItem = pg.ImageItem(labels={'bottom':('time [sec.]',''),'left':('frequency [Hz]','')})        

        self.__spectrogramPlot0.addItem(self.__spectrogramPlot0_ImageItem)

        bottom_left_main_layout.addWidget(self.__linePlot0)
        bottom_left_main_layout.addWidget(self.__spectrogramPlot0)
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

        self.init()

    def init(self):
        self.__samples_duration = 1 # [sec.]
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

        print(idx_samples_l)
        print(np.shape(samples_l))        

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

            # freq_positive_l, fft_pw_ch1_l = self.__eegclientThread.getFFTPower()
            # print(fft_pw_ch1_l)

            idx_samples_l, samples_l = self.__eegclientThread.getRawData()

            # print(idx_samples_l)
            # print(np.shape(samples_l))

            # self.__linePlot0_PlotCurveItems[i_channels_g].setData(x=time_downsampled_EEG_data_linePlot0_g, y=filtered_l)            

            # print(np.shape(samples_l[0,:]))

            # y_min_linePlot0_g = np.min(samples_l[0, idx_downsampled_EEG_data_linePlot0_g, i_channels_g])
            # y_min_linePlot0_g = y_min_linePlot0_g - 0.1*y_min_linePlot0_g
            # y_max_linePlot0_g = np.max(samples_l[0, idx_downsampled_EEG_data_linePlot0_g, i_channels_g])
            # y_max_linePlot0_g = y_max_linePlot0_g + 0.1*y_max_linePlot0_g
            # self.__linePlot0_PlotCurveItems[-1].setData(x=[(i_EEG_data_linePlot0_g*T_x_ranges_linePlot0_g)/N_EEG_data_linePlot0_g, (i_EEG_data_linePlot0_g*T_x_ranges_linePlot0_g)/N_EEG_data_linePlot0_g], y=[y_min_linePlot0_g, y_max_linePlot0_g])

            self.__linePlot0_TP9_PlotCurveItem.setData(x=np.arange(int(self.__Fs*self.__samples_duration)), y=samples_l[0, :])            

            # self.__linePlot0_TP9_PlotCurveItem.setData(x=time_downsampled_EEG_data_linePlot0_g, y=filtered_l)            
            # self.__linePlot0_TP9_PlotCurveItem.setData(x=freq_positive_l, y=fft_pw_ch1_l)            


        # self.__img.setImage(img_EEG_data_fft_g, autoLevels=False)

            # freq_positive_l, _, _, fft_pw_ch1_l, _, _, _    = AV_ShortFFT(fs_p=self.__Fs, signal_p=ch1_l - np.mean(ch1_l), typeTaper_p="hann", taper_p=taper_EEG_data_fft_g)

            # self.__spectrogramPlot0_ImageItem.setImage(img_EEG_data_fft_g, autoLevels=False)

        except Exception as e:
            print(e)
            pass

    # def _mainV2(self, sender_Type_p):
    #     data_len_bytes_l    = bytearray(4)

    #     self._running = True

    #     while self._running:
    #         try:
    #             try:
    #                 ##### Open the TCP connection.
    #                 sock_l = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #                 sock_l.settimeout(1)

    #                 # Connect the socket to the port where the server is listening
    #                 server_address_l = (self._server_ip, self._server_port)
    #                 # print(self._Name + ": Connecting to " + str(server_address_l))
    #                 sock_l.connect(server_address_l)
    #                 print(self._Name + ": Connected to " + str(server_address_l))

    #                 i_data_len_bytes_l  = 0
    #                 cnt_same_state_thr_l= 0
    #                 pre_state_l         = -1
    #                 #TODO Make it adaptive.
    #                 N_same_state_thr_l  = 100 # If it is looping in the same for more than N_same_state_thr, we might reach an unexpected error and reboot the socket is required.                    
    #                 ##### Getting message loop.
    #                 while self._running:

    #                     recv_state_l = self.__COM_TCP_RECV_WAITFOR_DATALENGTH
    #                     pre_state_l, cnt_same_state_thr_l = self._chkIfSameStateTooLong(pre_state_p=pre_state_l, recv_state_p=recv_state_l, cnt_same_state_thr_p=cnt_same_state_thr_l, N_same_state_thr_p=N_same_state_thr_l)

    #                     # This loop is to fetch one message.
    #                     while self._running:

    #                         block_l = sock_l.recv(self._buff_socket_size)

    #                         N_block_l           = len(block_l)
    #                         i_N_block_l         = 0
    #                         remain_N_block_l    = N_block_l

    #                         if (N_block_l == 0):
    #                             raise Exception("Recreate a connection.")


    #                         while (remain_N_block_l > 0):

    #                             # Get the length of the message.
    #                             if (recv_state_l == self.__COM_TCP_RECV_WAITFOR_DATALENGTH):
    #                                 pre_state_l, cnt_same_state_thr_l = self._chkIfSameStateTooLong(pre_state_p=pre_state_l, recv_state_p=recv_state_l, cnt_same_state_thr_p=cnt_same_state_thr_l, N_same_state_thr_p=N_same_state_thr_l)
                                    
    #                                 while (i_data_len_bytes_l < 4) and (i_N_block_l < N_block_l):

    #                                     data_len_bytes_l[i_data_len_bytes_l] = block_l[i_N_block_l]

    #                                     i_data_len_bytes_l  = i_data_len_bytes_l + 1
    #                                     i_N_block_l         = i_N_block_l + 1

    #                                     remain_N_block_l    = remain_N_block_l - 1

    #                                 if (i_data_len_bytes_l == 4):
    #                                     data_len_l      = self._bytes_to_uint32(data_len_bytes_l)

    #                                     i_data_len_l    = 0

    #                                     msg_l = bytearray(data_len_l)

    #                                     recv_state_l = self.__COM_TCP_RECV_FETCH_MSG

    #                             # Get the message.
    #                             if (recv_state_l == self.__COM_TCP_RECV_FETCH_MSG): 
    #                                 pre_state_l, cnt_same_state_thr_l = self._chkIfSameStateTooLong(pre_state_p=pre_state_l, recv_state_p=recv_state_l, cnt_same_state_thr_p=cnt_same_state_thr_l, N_same_state_thr_p=N_same_state_thr_l)

    #                                 while (i_data_len_l < data_len_l) and (i_N_block_l < N_block_l):
                                    
    #                                     msg_l[i_data_len_l] = block_l[i_N_block_l]

    #                                     i_data_len_l = i_data_len_l + 1
    #                                     i_N_block_l = i_N_block_l + 1

    #                                     remain_N_block_l = remain_N_block_l - 1
                                    

    #                                 # We have a complete message.
    #                                 if (i_data_len_l == data_len_l):

    #                                     recv_state_l = self.__COM_TCP_RECV_PROCESS_MSG
                                    
    #                             # Process the message.
    #                             if (recv_state_l == self.__COM_TCP_RECV_PROCESS_MSG):
    #                                 pre_state_l, cnt_same_state_thr_l = self._chkIfSameStateTooLong(pre_state_p=pre_state_l, recv_state_p=recv_state_l, cnt_same_state_thr_p=cnt_same_state_thr_l, N_same_state_thr_p=N_same_state_thr_l)

    #                                 PACKET_HEADER_GROUPx = msg_l[0]

    #                                 if (sender_Type_p == self.__SENDER_TYPE_IAWARE):
    #                                     eff_sampling_freq_l = self._bytes_to_uint32(msg_l[1:5]) # [microsec]. It is the duration in microsec. for collecting the message.

    #                                     # print(msg_l[4])
    #                                     uint16arr_buff_l = self._combineHighByteLowByte(msg_l[5:], data_len_l - 9)

    #                                     del msg_l

    #                                     self._fct_callback(uint16arr_buff_l, eff_sampling_freq_l)  

    #                                 elif (sender_Type_p == self.__SENDER_TYPE_VAG):
    #                                     uint32arr_buff_l = self._combine24Bits(msg_l[1:], data_len_l - 1)                                    

    #                                     # print(uint32arr_buff_l[0,0])

    #                                     del msg_l

    #                                     self._fct_callback(uint32arr_buff_l)
                                    
    #                                 recv_state_l        = self.__COM_TCP_RECV_WAITFOR_DATALENGTH
    #                                 i_data_len_bytes_l  = 0

    #             finally:
    #                 # traceback.print_exc()                    

    #                 sock_l.shutdown(SHUT_RDWR)
    #                 sock_l.close()

    #                 print(self._Name + ": Close socket and resume in 10 sec.")

    #                 time.sleep(10.0)

    #         except Exception as e:
    #             print(self._Name + ": Outermost Exception and resume in 10 sec.")
    #             # traceback.print_exc()

    #             time.sleep(10.0)

# def run(main_p):

#     iaware_l = EEGClientThread(N_channels_p=1, samples_duration_p=2)
#     iaware_l.createTCPClient(buff_socket_size_p=1000, server_ip_p="192.168.4.1", server_port_p=5000, Fs_senddata_p=10, Fs_p=500, Name_p="iAwareClient")
#     iaware_l.start()

#     window_l = UI(eegclientThread_p=iaware_l, refreshRate_p=20, main_p=main_p)        

#     return window_l                

if __name__ == '__main__':
    app_l = QtWidgets.QApplication(sys.argv)

    # iaware_l = EEGClientThread(N_channels_p=4, samples_duration_p=2)
    # iaware_l.createMuseMonitorClient(server_ip_p="192.168.0.101", server_port_p=5000, Name_p="MuseMonitor")

    # iaware_l = EEGClientThread(N_channels_p=1, samples_duration_p=2)
    # iaware_l.createTCPClient(buff_socket_size_p=1000, server_ip_p="192.168.4.1", server_port_p=5000, Fs_senddata_p=20, Fs_p=15000, Name_p="iAwareClient")
    # iaware_l.start()

    window_l = UI(refreshRate_p=20)
    window_l.run()
    window_l.show()

    sys.exit(app_l.exec_())

