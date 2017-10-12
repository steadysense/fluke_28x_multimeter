###!/usr/bin/env python
#!venv_meaplot/bin/python

import pylab
import time
import datetime
import serial
import argparse
import six
import pprint
import collections
import datetime
from serial.tools import list_ports


def argsParser():

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filePath', type=str,
        help="path to the file where measurements are saved")
    parser.add_argument('-p', '--serialPort', type=str,
        help="port on which Fluke 289 is connected")
    parser.add_argument('-g', '--graphLabel', type=str,
        help="name of the graph")
    parser.add_argument('-s', '--samples', type=int,
        help="N of measurements/second")
    parser.add_argument('-d', '--duration', type=int,
        help="duration of measurement in seconds [10; 86400]")
    args = parser.parse_args()

    if args.filePath == None:
        args.filePath = '/tmp/some.file'
        print('File was not specified. Measurements are saved to /tmp/some.file')
    if args.serialPort == None:
        args.serialPort = '/dev/ttyUSB0'
        print('Serial Port was not specified. Default is set to /dev/ttyUSB0')
    if args.samples == None:
        args.samples = 10
        print('Number of samples/second is not given. Default set to 10 samples/second')
    if args.duration == None:
        args.duration = 10
        print('Duration of measurements is not specified. Default set to 10 second')
    if args.graphLabel == None:
        args.graphLabel = 'New Graph'
        print('Graph label is not specified. Default is set to New Graph')

    return args


def query_identification(filePath='/tmp/some.file', port='/dev/tty.usbserial-AL03L2UV', readTime=10, samples=10):
    """
    Examples
    =======

    Multimeter connected via serial port
    >> ID
    << b'0\rFLUKE 287,V1.16,39120112\r'

    :param filePath:
    :param port:
    :param readTime:
    :param samples:
    :return:
    """
    if samples > 25: # can't handle more samles
        samples = 25
    elif samples < 1:
        samples = 1
    if readTime > 86400: # 24 hours restriction
        readTime
    elif readTime < 10:
        readTime = 10

    ser = serial.Serial(port, 115200, timeout = 1.0/samples)
    f = open(filePath, 'w')

    start_time = time.time()

    # Send command to multimeter
    ser.write(b"ID\r")

    # Read response from multimeter
    line_from_serial = ser.read_until(terminator=b"\n")
    line_splitted = line_from_serial.decode("utf-8").strip('0\r').split(',')

    keys_id = ['deviceName', 'softwareVersion', 'serial']
    dict_id = collections.OrderedDict(zip(keys_id, line_splitted))
    dict_id['serial']=int(dict_id['serial'])

    pprint.pprint(dict_id)

'''
# doesn't work for fluke 287
def query_set_function(filePath='/tmp/some.file', port='auto', readTime=10, samples=10):
    if samples > 25: # can't handle more samles
        samples = 25
    elif samples < 1:
        samples = 1
    if readTime > 86400: # 24 hours restriction
        readTime
    elif readTime < 10:
        readTime = 10

    # find device port
    if port == 'auto':
        port = find_port()

    ser = serial.Serial(port, 115200, timeout = 1.0/samples)
    f = open(filePath, 'w')

    start_time = time.time()

    ser.write(b"SF 11 \r")

    # Read response from multimeter
    line_from_serial = ser.read_until(terminator=b"\n")
    line_splitted = line_from_serial.decode("utf-8").strip('0\r').split(',')
    print(line_splitted)

'''


def query_primary_measurement(filePath='/tmp/some.file', port='auto', readTime=10, samples=10):
    """
  Examples
    =======

    Multimeter set to VDC, Power supply set to 0.7V
    >> QM
    << 0.7E0,VDC,NORMAL,NONE


    :param filePath:
    :param port:
    :param readTime:
    :param samples:
    :return:
    """
    '''
    Read specified Serial port
    where Fluke 289 is connected
    '''

    if samples > 25: # can't handle more samles
        samples = 25
    elif samples < 1:
        samples = 1
    if readTime > 86400: # 24 hours restriction
        readTime
    elif readTime < 10:
        readTime = 10

    # find device port
    if port == 'auto':
        port = find_port()

    try:
        ser = serial.Serial(port, 115200, timeout = 1.0/samples)
        f = open(filePath, 'w')

        start_time = time.time()

        # keep reading serial until specified time elapsed
        while (start_time + readTime) > time.time():
            try:
                # Send command to multimeter
                ser.write(b"QM\r")

                # Read response from multimeter
                line_from_serial = ""
                line_from_serial += ser.read(32).decode("utf-8")
                #print(line_from_serial)
                line_from_serial = line_from_serial[2:-1] # cut '0\n'
                #print(line_from_serial)
                line_splited = line_from_serial.split(',')
                #print(line_splited)

                keys_base = ['Value', 'Unit', 'State', 'Attribute']

                dict_base = collections.OrderedDict (zip(keys_base, line_splited))
                dict_base['Value'] = float(dict_base['Value'])
                dict_base.update({'timeStampComp':datetime.datetime.now()})

                pprint.pprint(dict_base)

                value_amperes = float(line_splited[0])
                # print value_amperes
                #f.write(str(value_amperes) + ',' + str(datetime.datetime.now()) + '\n')
            except serial.SerialException:
                print('Error occured!\n')
                continue
            except ValueError:
                print('Lost value!')
                continue
    except OSError:
        print('ERROR: Multimeter is not connected!')
        print('Check /dev/ folder for ttyUSBx port and do sudo chmod 777 /dev/ttyUSBx')


def query_display_data(filePath='/tmp/some.file', port='auto', readTime=10, samples=10):
    """
    Examples
    =======

    Multimeter set to VDC, AutoRange, MinMax
    >> QDDA
    << b'0\rV_DC,NONE,AUTO,VDC,5,0,OFF,1507700706.371,1,MIN_MAX_AVG,5,LIVE,0.6984,VDC,0,4,5,NORMAL,NONE,1507703969.077,
        PRIMARY,0.6984,VDC,0,4,5,NORMAL,NONE,1507703969.077,MINIMUM,0.6979,VDC,0,4,5,NORMAL,NONE,1507700706.371,MAXIMUM,
        0.6984,VDC,0,4,5,NORMAL,NONE,1507703759.355,AVERAGE,0.6982,VDC,0,4,5,NORMAL,NONE,1507703969.077\r'

    :param filePath:
    :param port:
    :param readTime:
    :param samples:
    :return:
    """
    '''
    Read specified Serial port
    where Fluke 289 is connected
    '''

    if samples > 25: # can't handle more samles
        samples = 25
    elif samples < 1:
        samples = 1
    if readTime > 86400: # 24 hours restriction
        readTime
    elif readTime < 10:
        readTime = 10

    # find device port
    if port == 'auto':
        port = find_port()

    ser = serial.Serial(port, 115200, timeout = 1.0/samples)
    f = open(filePath, 'w')

    start_time = time.time()

    # keep reading serial until specified time elapsed
    # while(start_time + readTime) > time.time():

    # keep reading serial until terminated manually
    while True:
        # Send command to multimeter
        ser.write(b"QDDA\r")

        # Read response from multimeter
        line_from_serial = ser.read_until(terminator=b"\n")
        line_splitted = line_from_serial.decode("utf-8").strip('0\r').split(',')

        if "HOLD" in line_splitted:
            line_splitted.pop(9)
            hold = True
        else:
            hold = False

        keys_base = ['primaryFunction','secondaryFunction', 'autoRangeState', 'baseUnit', 'rangeNumber', 'unitMultiplier',
                   'lightningBolt', 'minMaxStartTime', 'numberOfModes',  'measurementMode', 'numberOfReadings']
        keys_readingData = ['readingID', 'readingValue', 'baseUnitReading', 'unitMultiplierRecording', 'decimalPlaces',
                            'displayDigits', 'readingState', 'readingAttribute', 'timeStamp']

        # initialize base dictionary
        dict_base = collections.OrderedDict (zip(keys_base, line_splitted))
        dict_base.update({'hold':hold})

        dict_base['values'] = []

        # adding recording data blocks containing the value to the base dictionary
        for x in range(len(keys_base), len(line_splitted), len(keys_readingData)):
            dict_add = collections.OrderedDict(zip(keys_readingData, line_splitted[x: x + len(keys_readingData)]))

            # dict_add['readingValue'] = float(dict_add['readingValue'])
            dict_add['unitMultiplierRecording'] = int(dict_add['unitMultiplierRecording'])
            dict_add['decimalPlaces'] = int(dict_add['decimalPlaces'])
            dict_add['displayDigits'] = int(dict_add['displayDigits'])
            dict_add['timeStamp'] = datetime.datetime.utcfromtimestamp(float(dict_add['timeStamp']))
            dict_add.update({'timeStampComp': datetime.datetime.now()})
            dict_base['values'].append(dict_add)

        pprint.pprint(dict_base)




def chargingRatePlot(filePath='/tmp/some.file', plotLabel = 'New Plot'):
    '''
    Plots a graph A(t)
    where:
    A - current measured from multimeter
    t - time stamp
    Throws IOError exeption if file doesn't exist
    returns None
    '''

    try:
        # check if file exists, throws exeption otherwise
        times, measurements = getMeasurements(filePath)
        average = sum(measurements) / len(measurements)
        print(('avg = ' + str(average)))
        # plotting related stuff
        pylab.figure(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")), figsize=(22.0, 9.0))
        pylab.title(plotLabel)
        pylab.xlabel('time, hour')
        pylab.ylabel('current, A')
        pylab.grid(True)
        legend_label = 'avg=' + str("{0:.4f}".format(average)) + 'A'
        pylab.plot(times, measurements, '-b', label=legend_label)
        mng = pylab.get_current_fig_manager() # get figure manager for
        # mng.resize(*mng.window.maxsize())     # setting window size to max
        mng.full_screen_toggle()
        pylab.legend(loc='best') # should be placed after pylab.plot()
        pylab.savefig(plotLabel + ' ' + legend_label + '.png', format='png', dpi=200)
        pylab.show()

    except IOError:
        print("File does not exist! Check file in " + str(filePath))


def getMeasurements(filePath):
    '''
    Get measurements from file
    Assumes:
        - measurements are already read from multimeter
        - measurements are stored as 'float,datetime\n' on each line
    returns two lists of measurements(float) and times(datetime)
    '''
    dataFile = open(filePath, 'r')
    times = []
    measurements = []
    counter = 0 # counter to keep track of lines
    PRESCALER = 1 # allows to read only N-th line from measurements

    for line in dataFile:
        # read only each N-th line
        if counter % PRESCALER == 0:
            line = line[:-1] # cut \n from the end of the line
            value, time = line.split(',')
            times.append(datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f"))
            measurements.append(float(value))
            counter += 1
    return (times, measurements)


def find_port():

    usb_serial_number = 'AL03L2UV'

    for i in range(0, len(list_ports.comports())):
        if list_ports.comports()[i].__dict__['serial_number'] == usb_serial_number:
            serialPort = list_ports.comports()[i].__dict__['device']

    for i in range(0, len(list_ports.comports()), 1):
        if list_ports.comports()[i].__dict__['serial_number'] == 'AL03L2UV':
            serialPort = list_ports.comports()[i].__dict__['device']

    return serialPort

def main():
    #args = argsParser()
    #query_primary_measurement(args.filePath, args.serialPort, args.duration, args.samples)

    query_identification()
    #query_set_function()
    #query_primary_measurement()
    query_display_data()


    #chargingRatePlot(args.filePath, args.graphLabel)

if __name__ == "__main__":
    main()
