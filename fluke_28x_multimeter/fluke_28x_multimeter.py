# -*- coding: utf-8 -*-

"""Main module."""
import collections
import datetime
import time
import serial
from enum import Enum
import logging

__all__ = ['find_device', 'connect', 'disconnect', 'query_identification', 'query_display_data',
           'query_primary_measurement', "USB_SERIAL_NUMBER", "Fluke287"]

logger = logging.getLogger(__name__)

USB_SERIAL_NUMBER = 'AL03L2UV'
SERIAL_TIMEOUT = 1.0
SERIAL_ENCODING = 'utf-8'
SERIAL_BAUDRATE = 115200
LINE_END = b"\r"


class Ack(Enum):
    RESPONSE_OK = 0
    ERROR_SYNTAX = 1
    ERROR_EXECUTION = 2
    NO_DATA = 5
    NOT_SUPPORTED = 99


def find_device():
    """
    check connected devices to find multimeter and return device
    :return: /dev/tty.AL03L2UV or None
    """
    from serial.tools.list_ports import comports

    for port in comports():
        if port.serial_number == USB_SERIAL_NUMBER:
            return port.device
    return None


def connect(port: str) -> serial.Serial:
    """
    Opens a serial port and configures it.
    :param port: 
    :return: 
    """
    return serial.Serial(port, SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT)


def disconnect(io):
    """
    Closes port
    :param io:
    :return: 
    """
    io.close()


def write(io, out):
    """ """
    io.write(out)


def read(io, n):
    """ """
    return io.read(n)


def send_command(io, command: bytes):
    logger.debug("-->", command)
    write(io, command + LINE_END)


def recv_response(io, terminator=LINE_END, size=None):
    """
    Read until a termination sequence is found ('\n' by default), the size
    is exceeded or until timeout occurs.
    """
    lenterm = len(terminator)
    buffer = bytearray()
    start = time.monotonic()
    while True:
        c = read(io, 1)
        if c:
            buffer += c
            if buffer[-lenterm:] == terminator:
                logger.debug("<--", buffer)
                return bytes(buffer[:-lenterm])
            if size is not None and len(buffer) >= size:
                return bytes(buffer)
        else:
            break
        if time.monotonic() - start > SERIAL_TIMEOUT:
            raise TimeoutError(f"Timeout exceeded ({timeout}), recieved: {line}")


def execute_query(io, command: bytes):
    send_command(io, command)
    response = recv_response(io)
    ack = parse_command_ack(response)
    if ack != Ack.RESPONSE_OK:
        raise RuntimeError(f"Please check if DMM is stopped, ot {ack} on command {command}.")
    return ack


def parse_command_ack(response: bytes):
    if response == b"0":
        return Ack.RESPONSE_OK
    elif response == b"1":
        return Ack.ERROR_SYNTAX
    elif response == b"2":
        return Ack.ERROR_EXECUTION
    elif response == b"5":
        return Ack.NO_DATA
    else:
        return Ack.NOT_SUPPORTED


def query_identification(io) -> dict:
    """
    Reads identification data from multimeter
    :param io
    :return:
    """
    # Send command to multimeter
    execute_query(io, b"ID")

    # Read response from multimeter
    line_from_serial = recv_response(io)
    line_splitted = line_from_serial.decode("utf-8").split(',')

    keys_id = [
        ('deviceName', str),
        ('softwareVersion', str),
        ('serialNumber', str)
    ]

    return {name: converter(value) for (value, (name, converter)) in zip(line_splitted, keys_id)}


def query_primary_measurement(io) -> dict:
    """
    Reads primary measurement value, unit and mode
    :param io: serial device, must be opened
    :return: 
    """
    # Send command to multimeter
    execute_query(io, b"QM")

    # Read response from multimeter
    line_from_serial = recv_response(io)
    line_splitted = line_from_serial.decode("utf-8").split(',')

    keys_primary = [('value', float), ('unit', str), ('state', str), ('attribute', str)]
    return {name: converter(value) for (value, (name, converter)) in zip(line_splitted, keys_primary)}


def query_display_data(io) -> dict:
    """
    Reads all data that is shown on screen. WARNING: data changes on configuration change. see docs for examples.
    :param io: serial device, must be opened
    :return: 
    """

    # Send command to multimeter
    execute_query(io, b"QDDA")

    # Read response from multimeter
    line_from_serial = recv_response(io)
    line_splitted = line_from_serial.decode("utf-8").split(',')

    meta_converters = [
        ('primaryFunction', str),
        ('secondaryFunction', str),
        ('autoRangeState', str),
        ('baseUnit', str),
        ('rangeNumber', str),
        ('unitMultiplier', str),
        ('lightningBolt', str),
        ('minMaxStartTime', float),
        ('numberOfModes', int),
        ('measurementMode', str),
        ('numberOfReadings', int)
    ]

    meta = []
    ivalues = iter(line_splitted)
    iconverters = iter(meta_converters)

    for n, ((name, formatter), item) in enumerate(zip(iconverters, ivalues)):
        meta.append((name, formatter(item)))

        # see remote_spec_28X.doc:
        # if numberOfModes is 0, then measurementMode is not present
        # this happens on standard operation
        if name == 'numberOfModes' and item == "0":
            meta.append(('measurementMode', None))
            next(iconverters)

    converters = [
        ('readingID', str),
        ('readingValue', float),
        ('baseUnitReading', str),
        ('unitMultiplierRecording', int),
        ('decimalPlaces', int),
        ('displayDigits', int),
        ('readingState', str),
        ('readingAttribute', str),
        ('timeStamp', float)]
    values = []

    for reading_number in range(0, meta[-1][1] - 1):
        value = []
        iconverters = iter(converters)
        for n, ((name, formatter), item) in enumerate(zip(iconverters, ivalues)):
            value.append((name, formatter(item)))
        values.append(value)

    return values, meta


class SerialPortState(Enum):
    DISCONNECTED = 0
    CONNECTED = 1


class InstrumentBase(object):
    def __init__(self, io=None, serial_port=None):
        """
        :param io: Any object with read and write methods attached. 
        """
        self._state = SerialPortState.DISCONNECTED

        if io is not None:
            self.io = io
        else:
            self.connect(serial_port)

    def connect(self, port=None):
        if port is None:
            port = find_device()
        self.io = connect(port)
        if self.io.is_open:
            self.state = SerialPortState.CONNECTED

    def disconnect(self):
        disconnect(self.io)
        self.state = SerialPortState.DISCONNECTED

    def write(self, payload):
        self.io.write(payload)

    def read(self):
        return self.io.read()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state


class Fluke287(object):
    """
    Base object for communication with Fluke287 Multimeter
    """

    def __init__(self, io):
        self._io = io

    def query_identification(self):
        """ return identification dict """
        return query_identification(self._io)

    def query_display_data(self):
        """ returns all displayed data"""
        return query_display_data(self._io)

    def query_primary_measurement(self):
        """ returns primary value, unit and mode """
        return query_primary_measurement(self._io)
