# -*- coding: utf-8 -*-

"""Console script for fluke_28x_multimeter."""

import sys
import click
import time
from fluke_28x_multimeter import *


@click.group()
@click.option("-v", "--verbose", type=click.BOOL, is_flag=True, help="print more output")
@click.pass_obj
def main(serial, verbose):
    """Console script for fluke_28x_multimeter."""
    if verbose:
        click.echo("Fluke 287")

    port = find_device()
    if port is None:
        if port is None:
            click.echo(f"Device with {USB_SERIAL_NUMBER} not found")
            click.echo("Available devices:")
            for port in comports():
                click.echo(f"  * {port.device} - SN:{port.serial_number}")
            sys.exit(1)

    if verbose:
        click.echo(f"Connecting to {port}")

    serial = connect(port)
    if not serial.is_open:
        click.echo(f"Could not open {port}, exiting")
        sys.exit(1)



@main.command()
@click.option("-f", "--fmt", type=click.STRING, default="csv", help="output format")
@click.pass_obj
def display(serial, fmt):
    """
    Displays all values shown on the multimeters screen
    :param serial: 
    :param fmt:
    :return: 
    """
    for n, data in enumerate(loop(serial, query_display_data, ())):
        if fmt == "csv":
            if n == 1:
                click.echo(",".join(data.keys()))
            click.echo(",".join([str(val) for val in data.values()]))

    return data


@main.command()
@click.option("-f", "--fmt", type=click.STRING, default="csv", help="output format")
@click.option
@click.pass_obj
def primary(serial, fmt):
    """
    Displays primary measurement from Multimeter
    :param serial: 
    :param fmt:
    :return: 
    """
    data = query_primary_measurement(serial)
    if fmt == "csv":
        click.echo(",".join(data.keys()))
        click.echo(",".join([str(val) for val in data.values()]))
    return data


@main.command()
@click.option("-f", "--fmt", type=click.STRING, default="csv", help="output format")
@click.pass_obj
def identify(serial, fmt):
    """
    Displays information about connected Device
    :param serial: 
    :param fmt: 
    :return: 
    """
    data = query_identification(serial)
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
    import zerorpc
    import gevent
    from gevent import monkey
    monkey.patch_all()

    server = zerorpc.Server(ctx.obj)

    if serve_type == "bind":
        click.echo(f"Bind to {endpoint}")
        server.bind(endpoint=endpoint)

    if serve_type == "connect":
        click.echo(f"Connecting to {endpoint}")
        server.connect(endpoint)

    greenlets = [gevent.spawn(server.run), gevent.spawn(loop, ctx.obj)]
    gevent.joinall(greenlets)


def is_open(serial):
    """ """
    if serial.is_open:
        return True
    return False


def serial_open():
    """ """
    port = find_device()
    if port is not None:
        serial = connect(port)
        query_identification(serial)
        click.echo(f"Established connection on port {port}")
        return serial
    else:
        click.echo("Device not found. ")
        return False


def write_csv(data, head=True):
    """ """
    import csv
    writer = csv.DictWriter(sys.stdout, data.keys())
    if head is True:
        writer.writeheader()

    writer.writerow(data)


def loop(serial, func, *args, **kwargs):
    """ Main loop, used to reconnect the device, yields result of callable for each iteration """
    while True:
        if not is_open(serial):
            time.sleep(1)
            continue

        yield serial, func(serial, *args, **kwargs)


if __name__ == "__main__":
    main()
