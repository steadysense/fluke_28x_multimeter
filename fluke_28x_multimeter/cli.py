# -*- coding: utf-8 -*-

"""Console script for fluke_28x_multimeter."""

import sys
import click
from fluke_28x_multimeter import *
from fluke_28x_multimeter.out import write_csv


@click.group()
@click.option("-v", "--verbose", type=click.BOOL, is_flag=True,
              help="print more output")
@click.pass_context
def main(ctx, verbose):
    """Console script for fluke_28x_multimeter."""
    if verbose:
        click.echo("Fluke 287")

    fluke = Fluke287()
    if not fluke.is_connected:
        from serial.tools.list_ports import comports
        click.echo(f"Device with {USB_SERIAL_NUMBER} not found")
        click.echo("Available devices:")
        for port in comports():
            click.echo(f"  * {port.device} - SN:{port.serial_number}")
        sys.exit(1)

    ctx.obj = fluke


@main.command()
@click.option("-f", "--fmt", type=click.STRING, default="csv",
              help="output format")
@click.pass_obj
def values(fluke, fmt):
    """
    Displays all values shown on the multimeters screen
    :param serial:
    :param fmt:
    :return:
    """
    data = fluke.values
    if fmt == "csv":
        write_csv(data, head=True)
    return data


@main.command()
@click.option("-f", "--fmt", type=click.STRING, default="csv",
              help="output format")
@click.pass_obj
def value(fluke, fmt):
    """
    Displays primary measurement from Multimeter
    :param serial:
    :param fmt:
    :return:
    """
    data = fluke.value
    if fmt == "csv":
        write_csv(data, head=True)
    return data


@main.command()
@click.option("-f", "--fmt", type=click.STRING, default="csv",
              help="output format")
@click.pass_obj
def id(fluke, fmt):
    """
    Displays information about connected Device
    :param serial:
    :param fmt:
    :return:
    """
    data = fluke.id
    if fmt == "csv":
        write_csv(data, head=True)
    return data


@main.command()
@click.option("--server",
              "serve_type",
              flag_value="bind",
              help="server mode")
@click.option("--client",
              "serve_type",
              flag_value="connect",
              help="client mode")
@click.option("-e", "--endpoint",
              type=click.STRING,
              default="tcp://192.168.0.100:1235",
              help="endpoint of remote server or local bind",
              show_default=True)
@click.pass_obj
def serve(fluke, serve_type, endpoint):
    """
    Starts a server to expose Multimeter on network
    :param ctx:
    :param serve_type:
    :param endpoint:
    :return:
    """

    try:
        import gevent
        from gevent import monkey
        monkey.patch_all()
        import zerorpc
        import time
    except Exception as e:
        click.secho(f"zerorpc not found, cant serve. {e}", color="red")
        sys.exit(1)

    loops = {k: False for k in fluke.queries.keys()}

    @zerorpc.stream
    def start_loop(query, intervalMs):
        loops[query] = True
        intervalMs = int(intervalMs)
        while loops[query] is True:
            if not fluke.is_connected:
                logger.error(f"Device is not connected {e}")
                fluke.connect()
            try:
                yield fluke.execute(query)
            except TimeoutError as e:
                FlukeError(f"Timeout error, check device connection. {e}")
                logger.error()

            time.sleep(intervalMs)

    def stop_loop(query):
        loops[query] = False

    worker = zerorpc.Server(methods={
        "status": lambda: fluke.status,
        "isConnected": lambda: fluke.is_connected,
        "execute":     fluke.execute,
        "startLoop":   start_loop,
        "stopLoop":    stop_loop
    })

    if serve_type == "bind":
        worker.bind(endpoint=endpoint)
        click.secho(f"Bound to {endpoint}", color="green")

    if serve_type == "connect":
        worker.connect(endpoint)
        click.secho(f"Connected to {endpoint}", color="green")

    greenlets = [gevent.spawn(worker.run)]
    gevent.joinall(greenlets)


if __name__ == "__main__":
    main()
