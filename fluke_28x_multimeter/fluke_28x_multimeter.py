# -*- coding: utf-8 -*-

"""Main module."""
import collections
import datetime
import time
import serial
from enum import Enum

__all__ = ['find_device', 'connect', 'disconnect', 'query_identification', 'query_display_data',
           'query_primary_measurement', "USB_SERIAL_NUMBER", "Fluke287"]

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
    data = {name: converter(value) for (value, (name, converter)) in zip(line_splitted, keys_id)}

    return data


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
    line_splitted = line_from_serial.split(b',')
    if "HOLD" in line_splitted:
        line_splitted.pop(line_splitted.index("HOLD"))
        measurement_mode = "HOLD"
    elif "MIN_MAX_AVG" in line_splitted:
        line_splitted.pop(line_splitted.index("MIN_MAX_AVG"))
        measurement_mode = "MIN_MAX_AVG"
    else:
        measurement_mode = "NONE"

    keys_base = ['primaryFunction', 'secondaryFunction', 'autoRangeState', 'baseUnit', 'rangeNumber', 'unitMultiplier',
                 'lightningBolt', 'minMaxStartTime', 'numberOfModes', 'numberOfReadings']
    keys_data = ['readingID', 'readingValue', 'baseUnitReading', 'unitMultiplierRecording', 'decimalPlaces',
                 'displayDigits', 'readingState', 'readingAttribute', 'timeStamp']

    # initialize base dictionary
    data = collections.OrderedDict(zip(keys_base, line_splitted))
    data['measurementMode'] = measurement_mode
    data['values'] = []

    # adding recording data blocks containing the value to the base dictionary
    for x in range(len(keys_base), len(line_splitted), len(keys_data)):
        value = collections.OrderedDict(zip(keys_data, line_splitted[x: x + len(keys_data)]))

        # dict_add['readingValue'] = float(dict_add['readingValue'])
        value['unitMultiplierRecording'] = int(value['unitMultiplierRecording'])
        value['decimalPlaces'] = int(value['decimalPlaces'])
        value['displayDigits'] = int(value['displayDigits'])
        value['timeStamp'] = datetime.datetime.utcfromtimestamp(float(value['timeStamp']))
        value['timeStamp'] = str(value['timeStamp'])  # TODO: use msgpack hook to format datetimes
        value['timeStampComp'] = datetime.datetime.now()
        value['timeStampComp'] = str(value['timeStampComp'])  # TODO: use msgpack hook to format datetimes
        data['values'].append(value)

    return data


def query_primary_measurement(io) -> dict:
    """
    Reads primary measurement value, unit and mode
    :param io: serial device, must be opened
    :return: 
    """
    # Send command to multimeter
    send_command(io, b"QM")

    # Read response from multimeter
    line_from_serial = recv_response(io)
    line_splitted = line_from_serial.split(b',')

    keys_base = ['value', 'unit', 'state', 'attribute']

    dict_base = collections.OrderedDict(zip(keys_base, line_splitted))
    dict_base['value'] = float(dict_base['value'])
    dict_base['timeStampComp'] = datetime.datetime.utcnow()

    return dict_base


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
