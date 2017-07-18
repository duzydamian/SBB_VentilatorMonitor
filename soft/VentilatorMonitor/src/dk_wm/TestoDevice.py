#!/usr/bin/python
#
#
# Author : Damian Karbowiak
# Company: Silesian Softing
#
# Date   : 26.06.2017
#

##################################################################################################################
# IMPORT LIBRARIES
##################################################################################################################
import pygatt
import time
import sys
import datetime
import struct

class TestoDevice(object):
    ##################################################################################################################
    # variables
    ##################################################################################################################
    name = None
    address = None
    adapter = None
    device = None
    
    ##################################################################################################################
    # FUNCTIONS DEFINITION
    ##################################################################################################################
    # constructor        
    def __init__(self, name, address, adapter):
        self.name = name
        self.address = address
        self.adapter = adapter
        self.battery = 0.0
        self.temperature = 0.0
        self.velocity = 0.0
        self.differentialPressure = 0.0
        self.data_to_log = bytearray()
        #self.dataFileTemperature = DataFile(self.name, 'Temperature')
        #self.dataFileVelocity = DataFile(self.name, 'Velocity')
        #self.dataFileBatteryLevel = DataFile(self.name, 'BatteryLevel')
        
        #print "Create testo device with name: ", self.name, " address: ", self.address
        self.connect()
        
    def connect(self):
        #print self.adapter, self.address
        #print "Trying to connect with: ", self.name
        #self.adapter.start()
        self.device = self.adapter.connect(self.address, 10.0)
        
        if self.device._connected:
            #print "Connected with: ", self.name
            aa = self.device.discover_characteristics()
            #print "Characteristic from with: ", self.name
            for bb in aa:
                #print aa[bb].uuid, aa[bb].handle, aa[bb].descriptors,
                try:
                    if aa[bb].handle == 3 or aa[bb].handle ==24:
                        value = self.device.char_read(bb, 1)
                        #print "Characterostic handle:\t", aa[bb].handle, "value\t", value
                    #value2 = self.device.char_read_handle(aa[bb].handle, 1)
                    #print aa[bb].handle, 'value2:\t ", "%02X'% value2

                    #for ch in value:
                    #    print ch, '\t', chr(ch),         
                    if aa[bb].handle == 40:
                        #print "Subscrobe to handle: ", aa[bb].handle
                        self.device.subscribe(bb, callback=self.callback_fun)
                        time.sleep(1)                       
                except pygatt.exceptions.NotificationTimeout:
                    print "TIMEOUT"                    
                except:
                    print "Error:", sys.exc_info()
            
            self.device.char_write_handle(37, self.convert_str_bytearray('5600030000000c69023e81'), True, 5)
            self.device.char_write_handle(37, self.convert_str_bytearray('200000000000077b'), True, 5)
            self.device.char_write_handle(37, self.convert_str_bytearray('04001500000005930f0000004669726d77617265'), True, 5)
            self.device.char_write_handle(37, self.convert_str_bytearray('56657273696f6e304f'), True, 5)
            self.device.char_write_handle(37, self.convert_str_bytearray('04001500000005930f0000004669726d77617265'), True, 5)
            self.device.char_write_handle(37, self.convert_str_bytearray('56657273696f6e304f'), True, 5)
            self.device.char_write_handle(37, self.convert_str_bytearray('04001600000005d7100000004d6561737572656d'), True, 5)
            self.device.char_write_handle(37, self.convert_str_bytearray('656e744379636c656161'), True, 5)
            self.device.char_write_handle(37, self.convert_str_bytearray('110000000000035a'), True, 5)
                                
            #print self.device.get_rssi()
            #print self.device._connected
    def callback_fun(self, handle, data):
        #print handle, data
        if data[0]==16:
            self.data_to_log = bytearray()
            self.data_to_log = self.data_to_log + data
        else:
            self.data_to_log = self.data_to_log + data

            #print (datetime.datetime.now().strftime("%H:%M:%S>") + ' ' + self.name + '> '),
            if len(self.data_to_log) > 12:
                if self.data_to_log[12]==0x44: #D > DifferentialPressure
                    #file_to_log_analized.write(''.join('{:02x}'.format(x) for x in data_to_log[32:36]) + ' ')
                    #file_to_log_analized.write(''.join('{:02x}'.format(x) for x in data_to_log[36:]) + ' ')
                    #file_to_log_analized.write(data_to_log[12:32] + ' ')
                    #file_to_log_analized.write(str(struct.unpack('f', data_to_log[32:36])[0]) + '\n')
                    self.differentialPressure = struct.unpack('f', self.data_to_log[32:36])[0]
                if self.data_to_log[12]==0x42: #B > BatteryLevel
                    #print (self.data_to_log[12:24] + ' '),
                    #print (str(struct.unpack('f', self.data_to_log[24:28])[0]))
                    self.battery = struct.unpack('f', self.data_to_log[24:28])[0] 
                    #self.dataFileBatteryLevel.addRow(datetime.datetime.now().strftime("%H:%M:%S") ,self.battery)
                if self.data_to_log[12]==0x54: #T > Temperature
                    #print (self.data_to_log[12:23] + ' '),
                    #print (str(struct.unpack('f', self.data_to_log[23:27])[0]))
                    self.temperature = struct.unpack('f', self.data_to_log[23:27])[0]
                    #self.dataFileTemperature.addRow(datetime.datetime.now().strftime("%H:%M:%S") ,self.temperature) 
                if self.data_to_log[12]==0x56: #V > Velocity
                    #print (self.data_to_log[12:20] + ' '),
                    #print (str(struct.unpack('f', self.data_to_log[20:24])[0]))
                    self.velocity = struct.unpack('f', self.data_to_log[20:24])[0]
                    #self.dataFileVelocity.addRow(datetime.datetime.now().strftime("%H:%M:%S") ,self.velocity)
        
    def convert_str_bytearray(self, s):
        split_string = lambda x, n: [x[i:i+n] for i in range(0, len(x), n)]
        a = split_string(s,2)
        ba = bytearray()
        for z in a:
            ba.append(int(z,16))
    
        return ba