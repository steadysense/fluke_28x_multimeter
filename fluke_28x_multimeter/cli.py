# -*- coding: utf-8 -*-

"""Console script for fluke_28x_multimeter."""

import sys
import click
import zerorpc
import time
from fluke_28x_multimeter import *


@click.group()
@click.option("-v", "--verbose", type=click.BOOL, is_flag=True, help="print more output")
@click.pass_context
def main(ctx, verbose):
    """Console script for fluke_28x_multimeter."""
    if verbose:
        click.echo("Fluke 287")

    port = find_device()
    if port is None:
        if port is None:
            click.echo(f"Device with {USB_SERIAL_NUMBER} not found")
            click.echo("Available devices:")
            for port in comports():
                click.echo("  * " + port.device)
            sys.exit(1)

    if verbose:
        click.echo(f"Connecting to {port}")

    ser = connect(port)
    if not ser.is_open:
        click.echo("Could not open {port}, exiting")
        sys.exit(1)

    ctx.obj = Fluke287(ser)


@main.command()
@click.option("-f", "--fmt", type=click.STRING, default="csv", help="output format")
@click.pass_context
def display(ctx, fmt):
    """
    Displays all values shown on the multimeters screen
    :param ctx:
    :param fmt:
    :return:
    """
    data = ctx.obj.query_display_data()
    if fmt == "csv":
        if ctx.obj.query_count == 1:
            click.echo(",".join(data.keys()))
        click.echo(",".join([str(val) for val in data.values()]))

    return data


@main.command()
@click.option("-f", "--fmt", type=click.STRING, default="csv", help="output format")
@click.pass_context
def primary(ctx, fmt):
    """
    Displays primary measurement from Multimeter
    :param ctx:
    :param fmt:
    :return:
    """
    data = ctx.obj.query_primary_measurement()
    if fmt == "csv":
        if ctx.obj.query_count == 1:
            click.echo(",".join(data.keys()))
        click.echo(",".join([str(val) for val in data.values()]))
    return data


@main.command()
@click.option("-f", "--fmt", type=click.STRING, default="csv", help="output format")
@click.pass_context
def identify(ctx, fmt):
    """
    Displays information about connected Device
    :param ctx:
    :param fmt:
    :return:
    """
    data = ctx.obj.query_identification()
    if fmt == "csv":
        click.echo(",".join([str(val) for val in data.keys()]))
        click.echo(",".join([str(val) for val in data.values()]))

@main.command()
@click.option("--server", "serve_type", flag_value="bind", help="server mode")
@click.option("--client", "serve_type", flag_value="connect", help="client mode")
@click.option("-e", "--endpoint", type=click.STRING, default="tcp://0.0.0.0:20010", help="endpoint to use")
@click.pass_context
def serve(ctx, serve_type, endpoint):

    """
    Starts a server to expose Multimeter on network
    :param ctx:
    :param serve_type:
    :param endpoint:
    :return:
    """
    if serve_type in ['bind', 'connect']:
        server = zerorpc.Server(ctx.obj)

        if serve_type == "bind":
            click.echo(f"Bind to {endpoint}")
            server.bind(endpoint=endpoint)

        if serve_type == "connect":
            click.echo(f"Connecting to {endpoint}")
            server.connect(endpoint)

        import gevent
        from gevent import monkey
        monkey.patch_all()
        greenlets = [gevent.spawn(server.run), gevent.spawn(main_loop, ctx.obj)]

        gevent.joinall(greenlets)


def main_loop(fluke):
    while True:
        if not fluke.ser.is_open:
            click.echo("Lost connection, retry. . .")
            port = find_device()
            if port is not None:
                fluke.ser = connect(port)
                click.echo(f"reestablished connection on port {port}")
        time.sleep(1)

if __name__ == "__main__":
    main()
