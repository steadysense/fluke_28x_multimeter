# -*- coding: utf-8 -*-

"""Main module."""
import collections
import datetime
import serial
import pprint
from pymongo import MongoClient
from bson.son import SON
from serial.tools.list_ports import comports

USB_SERIAL_NUMBER = 'AL03L2UV'


def find_device():
    """
    check connected devices to find multimeter and return device
    :return: /dev/tty.AL03L2UV or None
    """
    for port in comports():
        if port.serial_number == USB_SERIAL_NUMBER:
            return port.device
    return None


def connect(port: str) -> serial.Serial:
    return serial.Serial(port, 115200, timeout=2.0)


def disconnect(ser: serial.Serial):
    ser.close()


def query_identification(ser: serial.Serial):
    """
    Examples
    =======

    Multimeter connected via serial port
    >> ID
    << b'0\rFLUKE 287,V1.16,39120112\r'

    :param ser: serial.Serial
    :return:
    """
    # Send command to multimeter
    ser.write(b"ID\r")
    answer = ser.read_until(terminator=b"\r").strip()
    if(answer != b"0"):
        raise Exception("Invalid Answer: {}".format(answer))

    # Read response from multimeter
    line_from_serial = ser.read_until(terminator=b"\n")
    line_splitted = line_from_serial.decode("utf-8").strip('\r').split(',')

    keys_id = ['deviceName', 'softwareVersion', 'serial']
    data = collections.OrderedDict(zip(keys_id, line_splitted))
    data['serial'] = int(data['serial'])
    return data


def query_display_data(ser: serial.Serial):
    """
        Examples
    =======

    Multimeter set to VDC, AutoRange, MinMax
    >> QDDA
    << b'0\rV_DC,NONE,AUTO,VDC,5,0,OFF,1507700706.371,1,MIN_MAX_AVG,5,LIVE,0.6984,VDC,0,4,5,NORMAL,NONE,1507703969.077,
        PRIMARY,0.6984,VDC,0,4,5,NORMAL,NONE,1507703969.077,MINIMUM,0.6979,VDC,0,4,5,NORMAL,NONE,1507700706.371,MAXIMUM,
        0.6984,VDC,0,4,5,NORMAL,NONE,1507703759.355,AVERAGE,0.6982,VDC,0,4,5,NORMAL,NONE,1507703969.077\r'

    :param ser:
    :return:
    """

    # Send command to multimeter
    ser.write(b"QDDA\r")

    answer = ser.read_until(terminator=b"\r").strip()
    if answer != b"0":
        raise Exception("Invalid Answer: {}".format(answer))

    # Read response from multimeter
    line_from_serial = ser.read_until(terminator=b"\n")
    line_splitted = line_from_serial.decode("utf-8").strip('\r').split(',')
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
    #data_base = collections.OrderedDict(zip(keys_base, line_splitted))

    data = []

    # adding recording data blocks containing the value to the base dictionary
    timestamp = str(datetime.datetime.now())

    for x in range(len(keys_base), len(line_splitted), len(keys_data)):
        value = collections.OrderedDict(zip(keys_data, line_splitted[x: x + len(keys_data)]))

        value['timeStamp'] = datetime.datetime.utcfromtimestamp(float(value['timeStamp']))
        value['timeStamp'] = str(value['timeStamp'])  # TODO: use msgpack hook to format datetimes

        data.append([value['readingID'], float(value['readingValue']), value['timeStamp'], value['baseUnitReading'], timestamp])

    return data


def query_primary_measurement(ser: serial.Serial):
    """
      Examples
    =======

    Multimeter set to VDC, Power supply set to 0.7V
    >> QM
    << 0.7E0,VDC,NORMAL,NONE

    :param ser:
    :return:
    """
    # Send command to multimeter
    ser.write(b"QM\r")

    answer = ser.read_until(terminator=b"\r").strip()
    if answer != b"0":
        raise Exception("Invalid Answer: {}".format(answer))

    # Read response from multimeter
    line_from_serial = ser.read_until(terminator=b"\n")
    line_splitted = line_from_serial.decode("utf-8").strip('\r').split(',')

    keys_base = ['value', 'unit', 'state', 'attribute']

    dict_base = collections.OrderedDict(zip(keys_base, line_splitted))
    data = [float(dict_base['value']), str(datetime.datetime.now())]

    return data


class Fluke287(object):
    """
    Base object for communication with Fluke287 Multimeter
    """
    def __init__(self, ser: serial.Serial):
        self.ser = ser or serial.Serial()
        self.query_count = 0

        self.mongo = MongoClient("localhost", 27017)
        self.db = self.mongo.fluke_values


    def query_identification(self):
        self.query_count += 1
        return query_identification(self.ser)

    def query_display_data(self):
        self.query_count += 1
        return query_display_data(self.ser)

    def query_primary_measurement(self):
        self.query_count += 1
        m = query_primary_measurement(self.ser)
        self.db.a11_36.insert_one({str(datetime.datetime.now()).replace(".", "-"):m})
        return m


