#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Program do podgldu stanu wentylatora

author: Damian Karbowiak
mail: dk.karbowiak@gmail.com
last edited: 12-07-2017
"""

import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import datetime
import bme280
import random
import csv
import pyqtgraph as pg
import numpy as np
import RPi.GPIO as GPIO
import pygatt
import logging
import pkg_resources
from TestoDevice import TestoDevice

class AckDialog(QMessageBox):
    def __init__(self, text, textExtra=''):
        super(AckDialog, self).__init__()
        self.setIcon(QMessageBox.Question)
        self.setWindowTitle('Potwierdzenie')
        self.setText(text)
        self.setInformativeText(textExtra)
        self.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
        self.buttonY = self.button(QMessageBox.Yes)
        self.buttonY.setText('Tak')
        self.buttonY.setFixedSize(80, 80)
        self.buttonN = self.button(QMessageBox.No)
        self.buttonN.setText('Nie')
        self.buttonN.setFixedSize(80, 80)
        self.exec_()
        
    def buttonSelected(self):
        return self.clickedButton()
    
    def YesOrNo(self):
        if self.clickedButton() == self.buttonY:
            return True
        elif self.clickedButton() == self.buttonN:
            return False
        else:
            return False
        
    
class MainWindow(QMainWindow):
    
    def __init__(self, adapters):
        super(MainWindow, self).__init__()
        
        self.adapters = adapters
        self.version = pkg_resources.get_distribution("dk_wm").version
        self.initUI()
        self.velocitySensor = None
        self.diffSensor = None
        
    
        #function check if dir exists
    def checkPathAndCreate(self, path):
        #print "Checking path", path

        if not os.path.exists(path):
            #print "Creating", path
            os.makedirs(path)
            
    def setColorText(self, label, text, color):
        if color == Qt.white:
            label.setText(text)
        elif color == Qt.yellow:
            label.setText("<font color='yellow'>" + text + "</font>")
        elif color == Qt.red:
            label.setText("<font color='red'>" + text + "</font>")
        else:
            label.setText(text)
        
    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowState(Qt.WindowMaximized)
        self.statusBar()
        
        font = QFont('Roboto', 14)                
        fontU = QFont('Roboto', 14)
        fontU.setUnderline(True)
        fontB = QFont('Roboto', 14)
        fontB.setBold(True)        
        fontUB = QFont('Roboto', 14)
        fontUB.setBold(True)
        fontUB.setUnderline(True)
        fontUB18 = QFont('Roboto', 18)
        fontUB18.setBold(True)
        fontUB18.setUnderline(True)
        
        self.headerText = QLabel("System monitorowania wentylatora wersja "+self.version)
        self.headerText.setFont(fontUB18)
        self.headerText.setAlignment(Qt.AlignCenter)
        #self.headerText.setStyleSheet("QLabel {background-color: red;}")
        self.headerIcon1 = QLabel("System monitorowania wentylatora")
        self.headerIcon1.setPixmap(QPixmap("/opt/dk/wm/images/icon1_small.png"))
        self.headerIcon2 = QLabel("System monitorowania wentylatora")
        self.headerIcon2.setPixmap(QPixmap("/opt/dk/wm/images/icon1_small.png"))
        self.header = QWidget()
        headerLayout = QGridLayout()
        headerLayout.addWidget(self.headerIcon1, 0, 0)
        headerLayout.addWidget(self.headerText, 0, 1)
        headerLayout.addWidget(self.headerIcon2, 0, 2)
        headerLayout.setColumnStretch(1, 1)
        self.header.setLayout(headerLayout)
        
        self.dateTime = QLabel("Aktualna data i godzina: ")
        self.dateTime.setFont(fontB)
        
        topleft = QWidget()
        #topleft.setStyleSheet("QWidget {border:2px solid rgb(0, 0, 0); }")
        topleft.setFont(font)
        
        layoutL = QGridLayout()        
        layoutL.setColumnStretch(2, 1)
        layoutL.setColumnMinimumWidth(0, 150)
        layoutL.setColumnMinimumWidth(1, 150)
        layoutL.setColumnMinimumWidth(2, 150)
        
        self.temperatureValue = QLabel("0.0")        
        self.pressureValue = QLabel("0.0")
        self.humidityValue = QLabel("0.0")
        
        layoutL.addWidget(QLabel("Temperatura"), 0, 0)
        layoutL.addWidget(self.temperatureValue, 0, 1, Qt.AlignCenter)
        layoutL.addWidget(QLabel("°C"), 0, 2)
        layoutL.addWidget(QLabel("Ciśnienie"), 1, 0)
        layoutL.addWidget(self.pressureValue, 1, 1, Qt.AlignCenter)
        layoutL.addWidget(QLabel("hPa"), 1, 2)
        layoutL.addWidget(QLabel("Wilgotność"), 2, 0)
        layoutL.addWidget(self.humidityValue, 2, 1, Qt.AlignCenter)
        layoutL.addWidget(QLabel("%"), 2, 2)
        
        topleft.setLayout(layoutL)
        
        topright = QWidget()
        #stopright.setStyleSheet("QWidget {border:2px solid rgb(0, 0, 0); }")
        topright.setFont(font)
        layoutR = QGridLayout()
        layoutR.setColumnStretch(2, 1)
        layoutR.setColumnMinimumWidth(0, 150)
        layoutR.setColumnMinimumWidth(1, 150)
        layoutR.setColumnMinimumWidth(2, 150)
        
        self.temperatureCanalValue = QLabel("0.0")
        self.velocityValue = QLabel("0.0")
        self.pressureDiffValue = QLabel("0.0")
        self.batteryDev1 = QLabel("0.0")        
        self.batteryDev2 = QLabel('0.0')        
        
        layoutR.addWidget(QLabel("Poziom baterii T405i"), 0, 0)
        layoutR.addWidget(self.batteryDev1, 0, 1, Qt.AlignCenter)
        layoutR.addWidget(QLabel("%"), 0, 2)
        layoutR.addWidget(QLabel("Temperatura"), 1, 0)
        layoutR.addWidget(self.temperatureCanalValue, 1, 1, Qt.AlignCenter)
        layoutR.addWidget(QLabel("°C"), 1, 2)
        layoutR.addWidget(QLabel("Prędkość powietrza"), 2, 0)
        layoutR.addWidget(self.velocityValue, 2, 1, Qt.AlignCenter)
        layoutR.addWidget(QLabel("m/s"), 2, 2)
        layoutR.addWidget(QLabel("Poziom baterii T510i"), 3, 0)
        layoutR.addWidget(self.batteryDev2, 3, 1, Qt.AlignCenter)
        layoutR.addWidget(QLabel("%"), 3, 2)
        layoutR.addWidget(QLabel("Różnica ciśnienień"), 4, 0)
        layoutR.addWidget(self.pressureDiffValue, 4, 1, Qt.AlignCenter)
        layoutR.addWidget(QLabel("hPa"), 4, 2)                
        
        topright.setLayout(layoutR)

        self.logCount = 0     
        
        label1 = QLabel("Stan otoczenia")
        label2 = QLabel("Stan wewnątrz kanału")
        label1.setFont(fontUB)
        label2.setFont(fontUB)
        
        self.staticPlt = pg.GraphicsWindow(title="Wykres")
        #self.staticPlt.setInteractive(True)
        self.p1 = self.staticPlt.addPlot(title="Temperatura [°C]")
        self.p2 = self.staticPlt.addPlot(title="Prędkośc powietrza [m/s]")
        self.p3 = self.staticPlt.addPlot(title="Różnica ciśnień [hPa]")
        self.curve = self.p1.plot(pen=(255,0,0), name="Red X curve")
        self.curve2 = self.p2.plot(pen=(0,255,0), name="Green Y curve")
        self.curve3 = self.p3.plot(pen=(0,0,255), name="Blue Z curve")
        self.p1.setYRange(-20.0, 60.0)
        self.p2.setYRange(0.0, 30.0)
        self.p3.setYRange(-1500.0, 1500.0)
        self.data = [0]*100
        self.data2 = [0]*100
        self.data3 = [0]*100
        
        main = QWidget()
        layout = QGridLayout()
        layout.addWidget(self.header)
        layout.addWidget(self.dateTime)
        layout.addWidget(label1)
        layout.addWidget(topleft)
        layout.addWidget(label2)
        layout.addWidget(topright)
        layout.addWidget(self.staticPlt)
        main.setLayout(layout)

        self.setCentralWidget(main)
        
        startAction = QAction(QIcon('/opt/dk/wm/images/start.png'), 'Start', self)
        startAction.setShortcut('Ctrl+A')
        startAction.setStatusTip('Rozpoczęcie logowania danych')
        startAction.triggered.connect(self.start)
        
        stopAction = QAction(QIcon('/opt/dk/wm/images/stop.png'), 'Stop', self)
        stopAction.setShortcut('Ctrl+O')
        stopAction.setStatusTip('Zakończenie logowania danych')
        stopAction.triggered.connect(self.stop)
        #stopAction.setEnabled(False)
        
        exitAction = QAction(QIcon('/opt/dk/wm/images/exit.png'), 'Wyjście', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Wyjście z aplikacji')
        exitAction.triggered.connect(self.close)
        
        restartAction = QAction(QIcon('/opt/dk/wm/images/restart.png'), 'Restart', self)
        restartAction.setShortcut('Ctrl+R')
        restartAction.setStatusTip('Restart systemu operacyjnego')
        restartAction.triggered.connect(self.restart)
        
        shutdownAction = QAction(QIcon('/opt/dk/wm/images/shutdown.png'), 'Wyłączenie', self)
        shutdownAction.setShortcut('Ctrl+S')
        shutdownAction.setStatusTip('Wyłączenie systemu operacyjnego')
        shutdownAction.triggered.connect(self.shutdown)
        
        aboutAction = QAction(QIcon('/opt/dk/wm/images/about.png'), 'O programie', self)
        aboutAction.setStatusTip('Informacje o programie')
        aboutAction.triggered.connect(self.about)
 
        #helpAction = QAction(QIcon('/opt/dk/wm/images/help.png'), 'Pomoc', self)
        #helpAction.setStatusTip('Pomoc do pgoramu')
        #helpAction.triggered.connect(self.help)
        
        #menubar = self.menuBar()
        
        #fileMenu = menubar.addMenu('&Plik')
        #fileMenu.addAction(exitAction)
        
        #logMenu = menubar.addMenu("&Logowanie")
        #logMenu.addAction(startAction)
        #logMenu.addAction(stopAction)
        
        #helpMenu = menubar.addMenu("P&omoc")
        #helpMenu.addAction(aboutAction)
        #helpMenu.addAction(helpAction)
        
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(64,64))
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon|Qt.AlignLeading) #<= Toolbuttonstyle
        self.addToolBar(Qt.LeftToolBarArea, toolbar)
        toolbar.addActions((startAction, stopAction))
        toolbar.addSeparator()
        toolbar.addSeparator()
        toolbar.addSeparator()
        toolbar.addSeparator()
        toolbar.addAction(exitAction)
        toolbar.addSeparator()
        toolbar.addSeparator()
        toolbar.addSeparator()
        toolbar.addSeparator()
        toolbar.addActions((restartAction, shutdownAction))
        toolbar.addSeparator()
        toolbar.addSeparator()
        toolbar.addSeparator()
        toolbar.addSeparator()
        toolbar.addAction(aboutAction)
        
        self.timer = QBasicTimer()
        self.timer.start(250, self)
        #print "Main timer", self.timer.timerId()
        
        self.timerGATTConnect = QBasicTimer()
        self.timerGATTConnect.start(10000, self)
        
        self.timerLogging = QBasicTimer()        
        
        self.setGeometry(300, 300, 300, 300)        
        self.setWindowTitle('System monitorowania wentylatora')
        self.setWindowIcon(QIcon('/opt/dk/wm/images/icon1.png'))    
        
        self.statusBar().showMessage('Uruchomienie aplikacji')
    
        self.show()
        
            
    def start(self):
        GPIO.output(16,GPIO.HIGH)
        self.logCount = 0
        pen = os.listdir('/media/pi/')
        #print pen, type(pen), len(pen)
        if len(pen) == 0:
            self.path = '/home/pi/Desktop/Dane_z_systemu/'
        else:
            self.path = '/media/pi/' + pen[0] + '/Dane_z_systemu/'
        
        #print "Path", path
        
        self.checkPathAndCreate(self.path)
        self.fileName = self.path + datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S.csv")
        #print "Filename", self.fileName
        self.csvFile = open(self.fileName, 'w')
        self.fieldnames = ['Data', 'Godzina', \
                            'Temperatura otoczenia', 'Wilgotność powietrza', 'Ciśnienie atmosferyczne', \
                           'Temperatura w kanale', 'Prędkość powietrza w kanale', 'Różnica ciśnienień w kanale']
        self.writer = csv.DictWriter(self.csvFile, delimiter=';', fieldnames=self.fieldnames)
        
        self.writer.writeheader()
        
        self.timerLogging.start(1000, self)
        self.statusBar().showMessage('Rozpoczęto logowanie do pliku: '+str(self.fileName))
    
    def stop(self):
        GPIO.output(16, GPIO.HIGH)
        self.timerLogging.stop()
        self.csvFile.close()
        self.statusBar().showMessage('Zakończono logowanie do pliku: '+str(self.fileName))
        time.sleep(1)
        GPIO.output(16, GPIO.LOW)
    
    def about(self):
        pass
    
    #def help(self):
    #    pass
    
    def timerEvent(self, e):
        #print  e.timerId()        
        if e.timerId()==self.timer.timerId(): # data refresh
            date = datetime.datetime.now().strftime("%d-%m-%Y")
            time = datetime.datetime.now().strftime("%H:%M:%S\t\t")
            self.dateTime.setText("Aktualna data i godzina:\t\t" + time + date)
            
            temperature,pressure,humidity = bme280.readBME280All()
            #self.statusBar().showMessage('Odczytano czujnik BME280')
            #print "Temperature : ", temperature, "C",
            #print "Pressure : ", pressure, "hPa",
            #print "Humidity : ", humidity, "%"
            self.temperatureValue.setText("{0:.2f}".format(temperature))
            self.pressureValue.setText("{0:.2f}".format(pressure))
            self.humidityValue.setText("{0:.2f}".format(humidity))
            
            if self.velocitySensor <> None:
                self.temperatureCanalValue.setText("{0:.2f}".format(self.velocitySensor.temperature))
                self.velocityValue.setText("{0:.2f}".format(self.velocitySensor.velocity))
                self.batteryDev1.setText("{0:.2f}".format(self.velocitySensor.battery))
            else:
                self.temperatureCanalValue.setText("{0:.2f}".format(0))
                self.velocityValue.setText("{0:.2f}".format(0))
                self.batteryDev1.setText("{0:.2f}".format(0))
                self.setColorText(self.temperatureCanalValue, "{0:.2f}".format(0), Qt.yellow)
                self.setColorText(self.velocityValue, "{0:.2f}".format(0), Qt.yellow)
                self.setColorText(self.batteryDev1, "{0:.2f}".format(0), Qt.yellow)
            
            if self.diffSensor <> None:
                self.pressureDiffValue.setText("{0:.2f}".format(-100))                
                self.batteryDev2.setText("{0:.2f}".format(self.diffSensor.battery))                
            else:
                self.setColorText(self.pressureDiffValue, "{0:.2f}".format(0), Qt.yellow)
                self.setColorText(self.batteryDev2, "{0:.2f}".format(0), Qt.yellow)
                #self.pressureDiffValue.setText("{0:.2f}".format(0))
                #self.batteryDev2.setText("{0:.2f}".format(0))
                #self.batteryDev2.setStyleSheet('color: yellow')
            
            #s = np.array([time])
            #v = np.array([temperature])
            #self.staticPlt.plot(s, v, pen='r', symbol='o')
            X = int(temperature)
            Y = int(humidity)
            Z = int(pressure)
            if self.velocitySensor <> None:
                self.data.pop(0)
                self.data.append(self.velocitySensor.temperature)
                self.data2.pop(0)
                self.data2.append(self.velocitySensor.velocity)
            self.data3.pop(0)
            self.data3.append(int(Z))
            #xdata = np.array(data, dtype='float64')
            self.curve.setData(self.data)
            self.curve2.setData(self.data2)
            self.curve3.setData(self.data3)
            
        elif e.timerId()==self.timerLogging.timerId(): # data logging
            GPIO.output(16, GPIO.LOW)
            date = datetime.datetime.now().strftime("%Y-%m-%d")
            time = datetime.datetime.now().strftime("%H:%M:%S")
            
            self.writer.writerow({self.fieldnames[0]: date, \
                                  self.fieldnames[1]: time, \
                                  self.fieldnames[2]: self.temperatureValue.text(), \
                                  self.fieldnames[3]: self.humidityValue.text(), \
                                  self.fieldnames[4]: self.pressureValue.text(), \
                                  self.fieldnames[5]: self.temperatureCanalValue.text(), \
                                  self.fieldnames[6]: self.velocityValue.text(), \
                                  self.fieldnames[7]: self.pressureDiffValue.text() \
                                  })
            self.logCount += 1
            self.statusBar().showMessage('Wpisano rekordów do pliku z danymi: '+str(self.logCount))
        elif e.timerId()==self.timerGATTConnect.timerId():
            #print adapters            
            if self.velocitySensor == None or self.diffSensor == None:
                self.statusBar().showMessage('Wyszukiwanie urządzeń Bluetooth')
                devs = self.adapters[0].scan(timeout=5, run_as_root=True)
                for dev in devs:                    
                    #print "\tUrzadzenie ", dev["name"], " o adresie: ", dev["address"]
                    
                    if dev["name"].find('T405i')<>-1:                        
                        self.statusBar().showMessage('Łączenie z czujnikiem ' + str(dev["name"]))
                        newDevice = TestoDevice(dev["name"], dev["address"], self.adapters[1])
                        self.velocitySensor = newDevice
                    elif dev["name"].find('T510i')<>-1:
                        self.statusBar().showMessage('Łączenie z czujnikiem ' + str(dev["name"]))
                        newDevice = TestoDevice(dev["name"], dev["address"], self.adapters[2])
                        self.diffSensor = newDevice                        
    
    def restart(self):
        ack = AckDialog("Czy napewno chcesz uruchomić ponownie urzązdenie?", "Spowoduje to zakończenie aktualnej sesji logowania")
        
        if ack.YesOrNo():
            os.system("shutdown now -r")
        
    def shutdown(self):
        ack = AckDialog("Czy napewno chcesz wyłączyć urzązdenie?")
        
        if ack.YesOrNo():
            os.system("shutdown now -h")
            #os.system('systemctl poweroff') 
    
    def closeEvent(self, event):
        #event.accept()
        #return
        ack = AckDialog("Czy napewno chcesz opuścić aplikacje?")        

        if ack.YesOrNo():
            event.accept()
        else:
            event.ignore()        
            
class VentilatorMonitor:
    ##################################################################################################################
    # variables
    ##################################################################################################################
    #logger = FileLogger()                   # initialisation of logger
    configuration = None
    
    ##################################################################################################################
    # FUNCTIONS DEFINITION
    ##################################################################################################################
    # contructor
    def __init__(self):
        self.cofiguration = None
        
    def main(self):
        try:
            adapters = []
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(16,GPIO.OUT)
            
            logging.basicConfig()
            logging.getLogger('pygatt').setLevel(logging.WARN)
            
            for i in range(0, 3):
                adapters.append(pygatt.GATTToolBackend())
            
            #print "Created adapters count: ", len(adapters), adapters[0]._hci_device
            
            for adapter in adapters:
                adapter.start()
            
            #devs = adapters[0].scan(timeout=5, run_as_root=True)
            #for dev in devs:                    
            #    print "\tUrzadzenie ", dev["name"], " o adresie: ", dev["address"]
            #    newDevice = TestoDevice(dev["name"], dev["address"], adapters[1])
            #print adapters
        
            app = QApplication(sys.argv)
            app.setStyle('Fusion')
            
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(53,53,53))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(15,15,15))
            palette.setColor(QPalette.AlternateBase, QColor(53,53,53))
            palette.setColor(QPalette.ToolTipBase, Qt.black)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(53,53,53))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.BrightText, Qt.red)
                 
            palette.setColor(QPalette.Highlight, QColor(40,60,160))
            palette.setColor(QPalette.HighlightedText, Qt.white)
            app.setPalette(palette)
            
            translator = QTranslator(app)
            locale = QLocale.system().name()
            
            path = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
            translator.load('qt_%s' % locale, path)
            app.installTranslator(translator)
            
            mw = MainWindow(adapters)
            
            sys.exit(app.exec_())
        finally:
            print "Unexpected error:", sys.exc_info()[0]
            print "Stopping bluetooth adapters", adapters
            for adapter in adapters:
                adapter.stop()        