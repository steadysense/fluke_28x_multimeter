# -*- coding: utf-8 -*-

"""Main module."""
import time
from enum import IntEnum
import logging
import abc
from collections import namedtuple

USB_SERIAL_NUMBER = 'AL03L2UV'
TIMEOUT = 1.0
ENCODING = 'utf-8'
BAUDRATE = 115200
TERMINATOR = b"\r"

commands = ['find', 'connect', 'disconnect', 'settings', 'receive', 'send']
queries = ['ID', "QDDA", "QM", "PMM", "PF1"]
constants = ["USB_SERIAL_NUMBER", "TIMEOUT", "ENCODING", "BAUDRATE",
             "TERMINATOR", "RESPONSE_CODE"]

__all__ = queries + commands + constants

logger = logging.getLogger(__name__)
Response = namedtuple("Response", ["status", "data", "payload"])
Request = namedtuple("Request", ["name", "args", "payload", "response"])


class RESPONSE_CODE(IntEnum):
    RESPONSE_OK = 0
    ERROR_SYNTAX = 1
    ERROR_EXECUTION = 2
    NO_DATA = 5
    SERIAL_NOT_CONNECTED = 97
    SERIAL_TIMEOUT = 98
    NOT_SUPPORTED = 99

    @staticmethod
    def parse(response):
        if response == b"0":
            return RESPONSE_CODE.RESPONSE_OK
        elif response == b"1":
            return RESPONSE_CODE.ERROR_SYNTAX
        elif response == b"2":
            return RESPONSE_CODE.ERROR_EXECUTION
        elif response == b"5":
            return RESPONSE_CODE.NO_DATA
        else:
            return RESPONSE_CODE.NOT_SUPPORTED


class FlukeError(Exception):
    def __init__(self, response_code, msg):
        super(FlukeError, self).__init__()
        self.code = response_code.value
        self.name = response_code.name
        self.msg = msg
        self.hint = f"{response_code.name}: Check if device is turned on and cable is connected"


def find(serial_number=USB_SERIAL_NUMBER):
    """
    check connected devices to find multimeter and return device
    :return: /dev/tty.AL03L2UV or None
    """
    from serial.tools.list_ports import comports

    for port in comports():
        if port.serial_number == serial_number:
            return port.device
    return None


def connect(port=None):
    """
    Opens a serial port and configures it.
    :param port:
    :return:
    """
    from serial import Serial
    return Serial(port=port or find(USB_SERIAL_NUMBER), baudrate=BAUDRATE,
                  timeout=TIMEOUT)


def settings(io):
    return io.get_settings()


def disconnect(io):
    io.close()


def send(io, request):
    io.write(request)


def receive(io, terminator=TERMINATOR, size=None, timeout=TIMEOUT):
    """ Read until a termination sequence is found, the size is exceeded or until timeout occurs. """
    lenterm = len(terminator)
    buffer = bytearray()
    start = time.monotonic()
    while True:
        c = io.read(1)
        if c:
            buffer += c
            if buffer[-lenterm:] == terminator:
                return bytes(buffer[:-lenterm])
            if size is not None and len(buffer) >= size:
                return bytes(buffer)
        if time.monotonic() - start > TIMEOUT:
            raise TimeoutError(
                f"Timeout exceeded ({timeout}), recieved: {buffer}")


class Query(abc.ABC):
    request_format = None
    properties = []

    def __init__(self, io):
        self._io = io

    @classmethod
    def build_request(cls, request, *args, **kwargs):
        return Request(cls.__name__, args, (request % args) + TERMINATOR,
                       Response(None, None, None))

    @classmethod
    def parse_ack(cls, response, *args, **kwargs):
        return RESPONSE_CODE.parse(response)

    @classmethod
    @abc.abstractmethod
    def parse_response(cls, response, *args, **kwargs):
        pass

    @classmethod
    def execute(cls, io, *args, **kwargs):
        """
        Executes the query

        1. builds a request object from request_format, args and kwargs
        2. sends request
        3. receives and parses ack
        4. receives and parse data if any



        :param io: a class with send and recv method
        :param args: arguments to pass to query
        :param kwargs: kwargs to pass to query
        :return: request object
        """
        request = cls.build_request(cls.request_format, *args, **kwargs)
        io.send(request.payload)
        ack_response = io.recv()
        ack = cls.parse_ack(ack_response, *args, **kwargs)
        if ack != RESPONSE_CODE.RESPONSE_OK:
            return request._replace(
                response=Response(ack, FlukeError(
                    ack,
                    f"Request {request} failed with {ack}, received {ack_response}"),
                    ack_response)
            )

        response_payload = io.recv() if len(cls.properties) != 0 else None
        try:
            response_data = cls.parse_response(response_payload, *args,
                                               **kwargs)
        except (ValueError, KeyError) as e:
            response_data = e

        return request._replace(
            response=Response(ack, response_data, response_payload))

    def __call__(self, *args, **kwargs):
        self.execute(self._io, *args, **kwargs)


class ID(Query):
    request_format = b"ID"
    properties = [
        ('deviceName', str),
        ('softwareVersion', str),
        ('serialNumber', str)
    ]

    @classmethod
    def parse_response(cls, response, *args, **kwargs):
        line_splitted = response.decode(
            kwargs.get("encoding", ENCODING)).split(',')
        return {name: clazz(value) for (value, (name, clazz)) in
                zip(line_splitted, cls.properties)}


class QM(Query):
    request_format = b"QM"
    properties = [
        ('value', float),
        ('unit', str),
        ('state', str),
        ('attribute', str)
    ]

    @classmethod
    def parse_response(cls, response, *args, **kwargs):
        line_splitted = response.decode(
            kwargs.get("encoding", ENCODING)).split(',')
        return {name: clazz(value) for (value, (name, clazz)) in
                zip(line_splitted, cls.properties)}


class QDDA(Query):
    request_format = b"QDDA"
    properties = [
        ("settings", None),
        ("values", None)
    ]
    settings_properties = [
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
    values_properties = [
        ('readingID', lambda x: str(x).lower()),
        ('readingValue', float),
        ('baseUnitReading', str),
        ('unitMultiplierRecording', int),
        ('decimalPlaces', int),
        ('displayDigits', int),
        ('readingState', str),
        ('readingAttribute', str),
        ('timeStamp', float)
    ]

    @classmethod
    def parse_response(cls, response, *args, **kwargs):
        def parse_settings(ivalues, iconverters):
            for (name, formatter), item in zip(iconverters, ivalues):
                yield (name, formatter(item))

                # see remote_spec_28X.doc:
                # if numberOfModes is 0, then measurementMode is not present
                # this happens on standard operation
                if name == 'numberOfModes' and item == "0":
                    yield ('measurementMode', None)
                    next(iconverters)

        def parse_values(ivalues, iconverters):
            for (name, formatter), item in zip(iconverters, ivalues):
                yield (name, formatter(item))

        line_splitted = response.decode(
            kwargs.get("encoding", ENCODING)).split(',')

        ivalues = iter(line_splitted)
        settings = [(name, value) for name, value in
                    parse_settings(ivalues, iter(cls.settings_properties))]
        values = [[(name, value) for name, value in
                   parse_values(ivalues, iter(cls.values_properties))]
                  for _ in range(settings[-1][1])]

        return [dict(settings + value) for value in values]


class PMM(Query):
    request_format = b"PRESS MINMAX"

    @classmethod
    def parse_response(cls, response, *args, **kwargs):
        line_splitted = response.decode(kwargs.get("encoding", ENCODING))
        return {name: clazz(value) for (value, (name, clazz)) in
                zip(line_splitted, cls.properties)}


class PF1(Query):
    request_format = b"PRESS F1"


class PF4(Query):
    request_format = b"PRESS F4"
