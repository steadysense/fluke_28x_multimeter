#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `fluke_28x_multimeter` package."""


from unittest import TestCase
from click.testing import CliRunner

from fluke_28x_multimeter import *
from fluke_28x_multimeter import cli


class TestSerialConnection(TestCase):
    """Tests for `fluke_28x_multimeter` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert 'Show this message and exit.' in help_result.output

    def test_find_port(self):
        device = find_device()
        assert device is not None, "Device not found"

    def test_connect(self):
        device = find_device()
        ser = connect(device)
        assert ser.is_open is True, "Port could not be opened"
        ser.close()

class TestQueries(TestCase):
    """Tests for `fluke_28x_multimeter` package."""
    ser = None

    def setUp(self):
        device = find_device()
        self.ser = connect(device)
        assert self.ser.is_open is True, "Port could not be opened"

    def tearDown(self):
        disconnect(self.ser)

    def test_id(self):
        d = query_identification(self.ser)
        print(d)
        assert len(d) > 0, "Got no data from query"

    def test_display(self):
        d = query_display_data(self.ser)
        assert len(d.keys()) > 0, "Got no data from query"

    def test_primary(self):
        d = query_primary_measurement(self.ser)
        assert len(d.keys()) > 0, "Got no data from query"

    def test_server(self):
        pass

