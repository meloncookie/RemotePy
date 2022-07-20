# -*- coding: utf-8 -*-

import serial
from serial.tools import list_ports
import time
import json

class Communication():
    """Class to communicate with the device
    
    The communication path of this class is USB-UART.
    Separate the communication path from the GUI.
    """
    # M5Stack ATOM (LITE)
    _DEFAULT_VID = 1027
    _DEFAULT_PID = 24577

    # M5Stack Core2
    # _DEFAULT_VID = 4292
    # _DEFAULT_PID = 60000

    # RaspberryPi pico
    # _DEFAULT_VID = 11914
    # _DEFAULT_PID = 5

    def __init__(self, device_name: str='', vid: int=0, pid: int=0):
        """Initialize
        
        Parameters
        ----------
        device_name: str
            USB device name (ex. 'COM12' in Windows, '/dev/ttyUSB0' in Linux)
            For the empty string, the following two parameters are valid.
        vid: int
            Vendor ID of USB device. If 0, the default value _DEFAULT_VID is applied.
            If the device_name parameter is not an empty string, it does not apply.
        pid: int
            Product ID of USB device If 0, the default value _DEFAULT_PID is applied.
            If the device_name parameter is not an empty string, it does not apply.
        """
        if device_name:
            self._device = device_name
        else:
            self._device = None
            self.connect('', vid, pid)

    def connect(self, device_name: str='', vid: int= 0, pid: int = 0) -> bool:
        """Connection

        Disable the currently connected device and connect to the new device.
        The device is active only at the moment of sending and receiving data.
        Therefore, it is not necessary to connect after disconnecting.

        Parameters
        ----------
        device_name: str
            USB device name (ex. 'COM12' in Windows, '/dev/ttyUSB0' in Linux)
            For the empty string, the following two parameters are valid.
        vid: int
            Vendor ID of USB device. If 0, the default value _DEFAULT_VID is applied.
            If the device_name parameter is not an empty string, it does not apply.
        pid: int
            Product ID of USB device If 0, the default value _DEFAULT_PID is applied.
            If the device_name parameter is not an empty string, it does not apply.
        """
        if device_name:
            self._device = device_name
            return(True)
        devlis = list_ports.comports()
        if vid <= 0 or pid <= 0:
            _vid = Communication._DEFAULT_VID
            _pid = Communication._DEFAULT_PID
        else:
            _vid = vid
            _pid = pid
        for i in devlis:
            if i.vid == _vid and i.pid == _pid:
                self._device = i.device
                return(True)
        self._device = None
        return(False)

    def disconnect(self) -> None:
        """Disconnect
        
        Disable the communication path.
        """
        self._device = None

    def is_connect(self) -> bool:
        """Whether it is connected
        
        Returns
        ----------
        bool
        """
        if self._device:
            return(True)
        else:
            return(False)

    def send(self, msg: str, timeout: float=2) -> bool:
        """Turn on the infrared signal
        
        Parameters
        ----------
        msg: str
            Data sent to the device. The format is
            "w[400, 1200, 400, ...]\r\n"
        
        Returns
        ----------
        bool
            Whether communication was successful.
        """
        if not self.is_connect():
            return(False)
        try:
            with serial.Serial(self._device, baudrate=115200, timeout=timeout,
                               write_timeout=2) as ser:
                ser.reset_input_buffer()
                ser.reset_output_buffer()
                ser.write(msg.encode())
                start_time = time.time()
                # Detect echo back
                ack = b''
                while not ack:
                    ack = ser.readline()
                    if time.time() - start_time > timeout:
                        raise Exception()
                # Detect ack
                ack = b''
                while not ack:
                    ack = ser.readline()
                    if time.time() - start_time > timeout:
                        raise Exception()
                # Wait a moment before disconnecting.
                time.sleep(0.5)
            if b'OK' in ack:
                return(True)
            else:
                return(False)
        except:
            self.disconnect()
            return(False)

    def record(self, msg: str, timeout: float=4) -> tuple:
        """Get infrared received signal
        
        Parameters
        ----------
        msg: str
            Data sent to the device. The format is
            "r[4000, 200, 1023]\r\n"
                The first factor is the reception timeout time [msec]
                The second element is the static duration [msec]
                    that recognizes the end of reception.
                The third factor is the upper limit of the received signal length.
        
        Returns
        ----------
        tuple (item1, item2)
            item1: bool
                Communication error
            item2: list
                Integer list meaning received signal.
                If it fails, an empty list is returned.
        """
        if not self.is_connect():
            return((False, []))
        try:
            with serial.Serial(self._device, baudrate=115200, timeout=timeout,
                               write_timeout=2) as ser:
                ser.reset_input_buffer()
                ser.reset_output_buffer()
                ser.write(msg.encode())
                start_time = time.time()
                # Detect echo back
                ack = b''
                while not ack:
                    ack = ser.readline()
                    if time.time() - start_time > timeout:
                        raise Exception()
                # Detect ack
                ack = b''
                while not ack:
                    ack = ser.readline()
                    if time.time() - start_time > timeout:
                        raise Exception()
                # Wait a moment before disconnecting.
                time.sleep(0.5)
            return([True, json.loads(ack)])
        except:
            self.disconnect()
            return((False, []))
