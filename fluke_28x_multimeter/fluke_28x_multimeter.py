# -*- coding: utf-8 -*-

"""Main module."""
import collections
import datetime
import time
import serial

__all__ = ['find_device', 'connect', 'disconnect', 'query_identification', 'query_display_data',
           'query_primary_measurement', "USB_SERIAL_NUMBER"]

USB_SERIAL_NUMBER = 'AL03L2UV'
SERIAL_TIMEOUT = 1.0
SERIAL_ENCODING = 'utf-8'
SERIAL_BAUDRATE = 115200


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
    io.write(out.encode(SERIAL_ENCODING))


def read(io, n):
    """ """
    return io.read(n).decode(SERIAL_ENCODING)


def read_until(io, terminator, timeout=SERIAL_TIMEOUT, size=None):
    """
    Read until a termination sequence is found ('\n' by default), the size
    is exceeded or until timeout occurs.
    """
    lenterm = len(terminator)
    buffer = []
    start = time.monotonic()
    while True:
        c = read(io, 1)
        if c:
            buffer += c
            if buffer[-lenterm:] == terminator:
                break
            if size is not None and len(buffer) >= size:
                break
        else:
            break
        if time.monotonic()-start > SERIAL_TIMEOUT:
            raise TimeoutError(f"Timeout exceeded ({timeout}), recieved: {line}")
    return "".join(buffer)


def query_identification(io) -> dict:
    """
    Reads identification data from multimeter
    :param io
    :return:
    """
    # Send command to multimeter
    write(io, "ID\r")

    answer = read_until(io, "\r").strip()
    if answer != "0":
        raise ValueError("Invalid Answer: {}".format(answer))

    # Read response from multimeter
    line_from_serial = read_until(io, "\n")
    line_splitted = line_from_serial.strip('\r').split(',')

    keys_id = ['deviceName', 'softwareVersion', 'serial']
    data = collections.OrderedDict(zip(keys_id, line_splitted))
    data['serial'] = int(data['serial'])
    return data


def query_display_data(io) -> dict:
    """
    Reads all data that is shown on screen. WARNING: data changes on configuration change. see docs for examples.
    :param io: serial device, must be opened
    :return: 
    """

    # Send command to multimeter
    write(io, "QDDA\r")
    answer = read_until(io, "\r").strip()
    if answer != "0":
        raise ValueError("Invalid Answer: {}".format(answer))

    # Read response from multimeter
    line_from_serial = read_until(io, "\n")
    line_splitted = line_from_serial.strip('\r').split(',')
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
    io.write("QM\r")

    answer = read_until(io, "\r").strip()
    if answer != "0":
        raise Exception("Invalid Answer: {}".format(answer))

    # Read response from multimeter
    line_from_serial = read_until("\n")
    line_splitted = line_from_serial.strip('\r').split(',')

    keys_base = ['value', 'unit', 'state', 'attribute']

    dict_base = collections.OrderedDict(zip(keys_base, line_splitted))
    dict_base['value'] = float(dict_base['value'])
    dict_base['timeStampComp'] = datetime.datetime.now()
    dict_base['timeStampComp'] = str(dict_base['timeStampComp'])  # TODO: use msgpack hook to format datetimes

    return dict_base


class Fluke287(object):
    """
    Base object for communication with Fluke287 Multimeter
    """

    def __init__(self, io):
        """
        
        :param io: Any object with read and write methods attached. 
        """
        self.io = io

    def query_identification(self):
        """ return identification dict """
        return query_identification(self.io)

    def query_display_data(self):
        """ returns all displayed data"""
        return query_display_data(self.io)

    def query_primary_measurement(self):
        """ returns primary value, unit and mode """
        return query_primary_measurement(self.io)


class HwAdapter(object):

    def __init__(self, io):
        """

        :param io: Any object with read and write methods attached. 
        """
        self.io = io

    def read(self) -> str:
        return read(self.io, 1)

    def write(self, out: str):
        return write(self.io, out)

    def read_until(self, terminator: str, timeout=SERIAL_TIMEOUT, size=None) -> str:
        return read_until(self, terminator, timeout, size)



