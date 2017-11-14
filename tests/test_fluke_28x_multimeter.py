#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `fluke_28x_multimeter` package."""


from unittest import TestCase
from click.testing import CliRunner

from fluke_28x_multimeter import *

import logging
import pprint

class TestSerialConnection(TestCase):
    """Tests for `fluke_28x_multimeter` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_find_port(self):
        device = find()
        assert device is not None, "Device not found"

    def test_connect(self):
        device = find()
        ser = connect(device)
        assert ser.is_open is True, "Port could not be opened"
        ser.close()

    def test_find_with_class(self):
        device = Fluke287.find_serial()
        assert device is not None, "Device not found"

    def test_connect_with_class(self):
        fluke = Fluke287()
        assert fluke.is_connected is True, "Connecting failed"
        fluke.disconnect()
        assert fluke.is_connected is False, "Disconnecting failed"



class TestCommandLine():
    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_command_line_interface(self):
        """Test the CLI."""
        pass
        #runner = CliRunner()
        #result = runner.invoke(cli.main)
        #assert result.exit_code == 0
        #help_result = runner.invoke(cli.main, ['--help'])
        #assert help_result.exit_code == 0
        #assert 'Show this message and exit.' in help_result.output


def benchmark(iterations, func, *args, **kwargs):
    print(f"running {func} with args {args} {iterations} times ")
    import timeit
    timer = timeit.default_timer
    times = []
    for i in range(iterations):
        times.append(timer())
        func(*args)
        times.append(timer())

    deltas = [times[i] - times[i - 1] for i in range(1, len(times))]

    print(deltas)
    from text_histogram import histogram
    print(histogram(deltas))



class TestQueryClasses(TestCase):
    """Tests for `fluke_28x_multimeter` package."""
    fluke = None

    logging.basicConfig(level=logging.INFO)

    def setUp(self):
        device = find()
        ser = connect(device)
        assert ser.is_open is True, "Port could not be opened"
        self.fluke = Fluke287(ser)

    def tearDown(self):
        self.fluke.disconnect()

    def testID(self):
        request = ID.execute(self.fluke)
        print_request(request)

    def testQM(self):
        request = QM.execute(self.fluke)
        if request.response.status == RESPONSE_CODE.ERROR_EXECUTION:
            self.fluke.restart()
            request = QM.execute(self.fluke)
        print_request(request)

    def testQDDA(self):
        request = QDDA.execute(self.fluke)
        if request.response.status == RESPONSE_CODE.ERROR_EXECUTION:
            self.fluke.restart()
            request = QDDA.execute(self.fluke)
        print_request(request)

    def testPF1(self):
        request = PF1.execute(self.fluke)
        print_request(request)

    def testPMM(self):
        request = QDDA.execute(self.fluke)
        if request.response.status == RESPONSE_CODE.ERROR_EXECUTION:
            self.fluke.restart()
            request = QDDA.execute(self.fluke)
        if request.response.data[1]['measurementMode'] is None:
            PMM.execute(self.fluke)

        # check what happens if hold is pressed


def print_request(request):
    print("request", request)
    print("ack", request.response.status)
    pprint.pprint(request.response.data)


class TestFluke287Properties(TestCase):
    """Tests for `fluke_28x_multimeter` package."""
    fluke = None

    logging.basicConfig(level=logging.INFO)

    def setUp(self):
        device = find()
        ser = connect(device)
        assert ser.is_open is True, "Port could not be opened"
        self.fluke = Fluke287(ser)

    def tearDown(self):
        self.fluke.disconnect()

    def testIdProperty(self):
        data = self.fluke.id
        pprint.pprint(data)

    def testValueProperty(self):
        data = self.fluke.value
        pprint.pprint(data)

    def testValuesProperty(self):
        data = self.fluke.values
        pprint.pprint(data)

    def testStatusProperty(self):
        data = self.fluke.status
        pprint.pprint(data)
        assert "name" in data.keys(), "key name not in data keys"
        assert "connection" in data.keys(), "connection not in data keys"
        assert "connected" in data.keys(), "connected not in data keys"

    def testMinMax(self):
        response = self.fluke.min_max

    def testHoldOff(self):
        response = self.fluke.hold_off

    def testBenchmark(self):
        # benchmark(1000, getattr, self.fluke, "value")
        pass



class TestFluke287Server(object):
    fluke = None

    logging.basicConfig(level=logging.INFO)

    def setUp(self):
        device = find()
        ser = connect(device)
        assert ser.is_open is True, "Port could not be opened"
        self.fluke = Fluke287(ser)

    def tearDown(self):
        self.fluke.disconnect()
