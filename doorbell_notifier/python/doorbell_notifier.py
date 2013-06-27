#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import sys
import time
import math
import logging as log
log.basicConfig(level=log.INFO)

from tinkerforge.ip_connection import IPConnection
from tinkerforge.ip_connection import Error
from tinkerforge.bricklet_industrial_digital_in_4 import IndustrialDigitalIn4

class Doorbell:
    HOST = 'localhost'
    PORT = 4223

    ipcon = None
    di = None

    def __init__(self):
        self.ipcon = IPConnection()
        while True:
            try:
                self.ipcon.connect(Doorbell.HOST, Doorbell.PORT)
                break
            except Error as e:
                log.error('Connection Error: ' + str(e.description))
                time.sleep(1)
            except socket.error as e:
                log.error('Socket error: ' + str(e))
                time.sleep(1)

        self.ipcon.register_callback(IPConnection.CALLBACK_ENUMERATE,
                                     self.cb_enumerate)
        self.ipcon.register_callback(IPConnection.CALLBACK_CONNECTED,
                                     self.cb_connected)

        while True:
            try:
                self.ipcon.enumerate()
                break
            except Error as e:
                log.error('Enumerate Error: ' + str(e.description))
                time.sleep(1)

    def cb_interrupt(self, interrupt_mask, value_mask):
        log.warn('Ring Ring Ring!')

    def cb_enumerate(self, uid, connected_uid, position, hardware_version,
                     firmware_version, device_identifier, enumeration_type):
        if enumeration_type == IPConnection.ENUMERATION_TYPE_CONNECTED or \
           enumeration_type == IPConnection.ENUMERATION_TYPE_AVAILABLE:
            if device_identifier == AnalogIn.DEVICE_IDENTIFIER:
                try:
                    self.di = IndustrialDigitalIn4(uid, self.ipcon)
                    self.di.register_callback(IndustrialDigitalIn4.CALLBACK_INTERRUPT,
                                              self.cb_interrupt)
                    self.di.set_interrupt(1 << 0) # enable interrupt on input 0
                    log.info('Digital In initialized')
                except Error as e:
                    log.error('Digital In init failed: ' + str(e.description))
                    self.di = None

    def cb_connected(self, connected_reason):
        if connected_reason == IPConnection.CONNECT_REASON_AUTO_RECONNECT:
            log.info('Auto Reconnect')

            while True:
                try:
                    self.ipcon.enumerate()
                    break
                except Error as e:
                    log.error('Enumerate Error: ' + str(e.description))
                    time.sleep(1)

if __name__ == "__main__":
    log.info('Doorbell: Start')

    doorbell = Doorbell()

    if sys.version_info < (3, 0):
        input = raw_input # Compatibility for Python 2.x
    input('Press key to exit\n')

    if doorbell.ipcon != None:
        doorbell.ipcon.disconnect()

    log.info(': End')