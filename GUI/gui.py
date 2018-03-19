import os
import sys
import glob
import serial
import winsound
import matplotlib
import numpy as np
matplotlib.use("QT5Agg")
from time  import  sleep
from multiprocessing import Process
from matplotlib.figure  import  Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QApplication , QMainWindow, QVBoxLayout, QDial, QSlider
from PyQt5 import uic, QtCore, QtGui



Form = uic.loadUiType(os.path.join(os.getcwd(),'gui.ui',))[0]


class PulseWindow(QMainWindow, Form):

    def __init__(self):
        Form.__init__(self)
        QMainWindow.__init__(self)
        self.setupUi(self)


        self.fig = Figure(frameon=False)
        self.ax1 = self.fig.add_axes([0.05, 0.55, 0.9, 0.4])
        self.ax2 = self.fig.add_axes([0.05, 0.05, 0.9, 0.45])
        self.ax1.set_facecolor('white')
        self.x = np.linspace(0,10,2000)
        self.line1,=self.ax1.plot(self.x,np.zeros(2000),linewidth=1.5,color='red')
        self.line2,=self.ax2.plot(self.x,np.zeros(2000),linewidth=1.5,color='blue')
        self.ax1.set_ylim([-1,7])
        self.ax1.set_xlim([0,10])
        self.ax2.set_ylim([-1,7])
        self.ax2.set_xlim([0,10])        
        self.ax1.grid(True)
        self.ax2.grid(True)


        self.canvas = FigureCanvas(self.fig)
        self.navi = NavigationToolbar(self.canvas, self)
  
        self.status = True
        self.gridflag = True

        self.bkclrbox = ['white','yellow','cyan','black']
        self.linclrbox = ['white', 'yellow', 'cyan', 'black', 'red', 'green', 'brown']
        self.gridlinclrbox = ['white', 'yellow', 'cyan', 'black', 'red', 'green', 'brown']

        self.height = 0
        self.ax_bkclr = 0
        self.ax_hight = 0
        self.ax_length = 0
        self.ax_linclr = 4
        self.ax_gridlinclr = 0


        l=QVBoxLayout(self.matplotlib_widget)
        l.addWidget(self.canvas)
        l.addWidget(self.navi)


        self.start_pushButton.clicked.connect(self.start)
        self.timeSlider.sliderMoved.connect(self.time1)
        self.timeSlider2.sliderMoved.connect(self.time2)
        self.voltSlider.sliderMoved.connect(self.volt1) 
        self.voltSlider2.sliderMoved.connect(self.volt2)            
        self.bkgndclr_pushButton.clicked.connect(self.bkgndclr_change)
        self.gridlinescolor_pushButton.clicked.connect(self.gridlinclr_change)       
        self.SaveFig_pushButton.clicked.connect(self.SaveFig)

        self.SerialUpdate = serialupdate()
        self.SerialUpdate.update_trigger.connect(self.update_plot)
        self.SerialUpdate.start()



    def start(self):
        self.status = not self.status
        if self.status==False:
            self.start_pushButton.setText('Start')
            self.SerialUpdate.stop()
        else:
            self.start_pushButton.setText('Hold')
            self.SerialUpdate.start()
            
               

    def volt1(self):
        self.height = self.height + 1
        if self.height == 2:
            self.ax1.set_ylim([-1,3])
            self.fig.canvas.draw()
        elif self.height == 3:
            self.height = 0
            self.ax1.set_ylim([-1,8])
            self.fig.canvas.draw()
        elif self.height == 1:
            self.ax1.set_ylim([-1,5])
            self.fig.canvas.draw()
            

    def time1(self):
        if self.ax_length==0:
            self.ax_length=1
            self.ax1.set_xlim([4,8])
            self.fig.canvas.draw()
        elif self.ax_length==1:
            self.ax_length=2
            self.ax1.set_xlim([6,8])
            self.fig.canvas.draw()
        elif self.ax_length==2:
            self.ax_length=3
            self.ax1.set_xlim([7,8])
            self.fig.canvas.draw()
        else:
            self.ax_length=0
            self.ax1.set_xlim([0,8])
            self.fig.canvas.draw()


    def volt2(self):
        self.height = self.height + 1
        if self.height == 2:
            self.ax2.set_ylim([-1,3])
            self.fig.canvas.draw()
        elif self.height == 3:
            self.height = 0
            self.ax2.set_ylim([-1,8])
            self.fig.canvas.draw()
        elif self.height == 1:
            self.ax2.set_ylim([-1,5])
            self.fig.canvas.draw()
            

    def time2(self):
        if self.ax_length==0:
            self.ax_length=1
            self.ax2.set_xlim([4,8])
            self.fig.canvas.draw()
        elif self.ax_length==1:
            self.ax_length=2
            self.ax2.set_xlim([6,8])
            self.fig.canvas.draw()
        elif self.ax_length==2:
            self.ax_length=3
            self.ax2.set_xlim([7,8])
        else:
            self.ax_length=0
            self.ax1.set_xlim([0,8])
            self.fig.canvas.draw()


    def bkgndclr_change(self):
        self.ax_bkclr+=1
        if self.ax_bkclr==4:
            self.ax_bkclr=0
        while self.ax_bkclr==self.ax_linclr or (self.ax_bkclr==self.ax_gridlinclr and self.gridflag==True):
            self.ax_bkclr+=1
            if self.ax_bkclr==4:
                self.ax_bkclr=0
        self.ax1.set_axis_bgcolor(self.bkclrbox[self.ax_bkclr])
        self.ax2.set_axis_bgcolor(self.bkclrbox[self.ax_bkclr])
        self.fig.canvas.draw()


    def gridlinclr_change(self):
        self.ax_gridlinclr+=1
        if self.ax_gridlinclr==7:
            self.ax_gridlinclr=0

        if self.ax_gridlinclr==self.ax_bkclr:
            self.ax_gridlinclr+=1
        for xgridlin in self.ax1.xaxis.get_gridlines():
            xgridlin.set_color(self.gridlinclrbox[self.ax_gridlinclr])
        for ygridlin in self.ax1.yaxis.get_gridlines():
            ygridlin.set_color(self.gridlinclrbox[self.ax_gridlinclr])
        for xtick in self.ax1.xaxis.get_ticklines():
            xtick.set_color(self.gridlinclrbox[self.ax_gridlinclr])
        for ytick in self.ax1.yaxis.get_ticklines():
            ytick.set_color(self.gridlinclrbox[self.ax_gridlinclr])
        self.fig.canvas.draw()


    def update_plot(self, y1, y2):
        try:
            self.line1.set_ydata(y1)
            self.line2.set_ydata(y2)
            self.fig.canvas.draw()

        except:
            pass
        
 
    def SaveFig(self):
        self.fig.save("ppg.pdf")
        pass


class serialupdate(QtCore.QThread):

    update_trigger=QtCore.pyqtSignal(list, list)

    def __init__(self):
        QtCore.QThread.__init__(self)

        self.ser=serial.Serial()
        self.ser.port=serial_ports()[0]
        self.ser.baudrate=115200
        self.ser.open()
        self.ser.reset_input_buffer()
        self.ser.readline()
        
        self.y1=[0 for _ in range(2000)]
        self.y2=[0 for _ in range(2000)]
        self.list1=[]
        self.list2=[]

        self._is_running=True

	
    def run(self):

        self.ser.readline()
        self._is_running=True

        while (self._is_running):
            del self.y1[0:40]
            del self.y2[0:40]
            for j in range (40):
                try:
                    if self._is_running==True:

                        ak = self.ser.readline()
                        sk = str(ak)
                        pk = sk.split(',')[0]
                        pk2 = sk.split(',')[1]
                        gh = pk.split("'")
                        gh2 = pk2.split("\\n")

                        input1 = (float(gh[1])*(5/4096))
                        input2 = (float(gh2[0])*(5/4096))

                        print(float(gh[1]))
                        print(float(gh2[0]))

                    else:
                        input=3

                    self.list1.append(input1)
                    self.list2.append(input2)

                except:
                    self.list1.append(3)
                    self.list2.append(3)


            self.list1 = moveave(self.list1,11)
            self.y1.extend(self.list1)

            self.list2 = moveave(self.list2,11)
            self.y2.extend(self.list2)
            
            self.list1=[]
            self.list2=[]

            self.update_trigger.emit(self.y1, self.y2)
                
            sleep(0.035)
                


    def stop(self):

        self._is_running=False
        self.ser.reset_input_buffer()
        

    def __del__(self):

        self.ser.reset_input_buffer()
        self.ser.close()



def serial_ports():

    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result



def moveave(input_list,windowsize):
    tempnparray=np.array(input_list)
    oneslist=np.ones(windowsize)

    tempnparray=np.convolve(tempnparray,oneslist)/windowsize
    
    templist=list(tempnparray)

    for i in range(int(windowsize/2)):
        del templist[0]

    for j in range(int(windowsize/2)):
        del templist[len(input_list)+int(windowsize/2)-j-1]
    
    for i in range(int(windowsize/2)):
        templist[i]=templist[i]*windowsize/(int(windowsize/2)+1+i)
    
    for j in range(int(windowsize/2)):
        templist[len(input_list)-j-1]=templist[len(input_list)-j-1]*windowsize/(int(windowsize/2)+1+j)
    
    return templist





app=QApplication(sys.argv)
app.setStyle("Fusion")
window=PulseWindow()
window.show()
sys.exit(app.exec_())