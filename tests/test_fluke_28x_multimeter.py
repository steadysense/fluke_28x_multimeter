#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `fluke_28x_multimeter` package."""


from unittest import TestCase
from click.testing import CliRunner

from fluke_28x_multimeter import *
from fluke_28x_multimeter import cli


class TestFluke28xMultimeter(TestCase):
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
        assert find_device is not None, "Device not found"

    def test_connect(self):
        device = find_device()
        ser = connect(device)
        assert ser.is_open is True, "Port could not be opened"
        ser.close()

    def test_display(self):
        device = find_device()
        ser = connect(device)
        assert ser.is_open is True, "Port could not be opened"
        fluke = Fluke287(ser)
        d = fluke.query_display_data()
        assert len(d.keys()) > 0, "Got no data from query"
        disconnect(ser)

    def test_primary(self):
        device = find_device()
        ser = connect(device)
        assert ser.is_open is True, "Port could not be opened"
        fluke = Fluke287(ser)
        d = fluke.query_display_data()
        assert len(d.keys()) > 0, "Got no data from query"
        disconnect(ser)

    def test_server(self):
        pass

