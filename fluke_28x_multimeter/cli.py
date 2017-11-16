# -*- coding: utf-8 -*-

"""Console script for fluke_28x_multimeter."""

import sys
import click
import timeit
import logging
from fluke_28x_multimeter import Fluke287
from fluke_28x_multimeter.out import write_csv

logger = logging.getLogger(__name__)


@click.group()
@click.option("-v", "--verbose", type=click.BOOL, is_flag=True,
              help="print more output")
@click.pass_context
def main(ctx, verbose):
    """Console script for fluke_28x_multimeter."""
    if ctx.obj is None:
        # only initialize Fluke if this is the first run
        # this is needed for click repl
        if verbose:
            click.echo("Fluke 287")

        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)-15s %(message)s')

        if ctx.invoked_subcommand == "serve":
            # monkeypatch gevent before Fluke device is initialized to ensure
            # pyserial gets patched too
            from gevent import monkey
            monkey.patch_all()

        fluke = Fluke287()
        if not fluke.is_connected:
            from serial.tools.list_ports import comports
            click.secho(f"Device not found", fg="red")
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
    :param fluke:
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
    :param fluke:
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
    :param fluke:
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
    :param fluke
    :param serve_type:
    :param endpoint:
    :return:
    """

    try:
        # monkey patching is done in main() if serve command is executed to
        # ensure that pySerial gets patched to
        import gevent
        import zerorpc
        import time
        from serial import SerialException
    except Exception as e:
        click.secho(f"Library not found not found, cant serve.\n {e}",
                    color="red")
        sys.exit(1)

    loops = {k: -1 for k in fluke.queries.keys()}
    connection_error = {k: False for k in fluke.queries.keys()}

    @zerorpc.stream
    def start_loop(query, intervalS):
        try:
            timer = timeit.default_timer
            try:
                loops[query] = float(intervalS)
            except ValueError as e:
                loops[query] = int(intervalS)

            while loops[query] > 0.0:
                start_time = timer()
                while not fluke.is_connected:
                    logger.error(f"Device is not connected {e}")
                    fluke.connect()
                try:
                    yield fluke.execute(query)
                except (TimeoutError, SerialException) as e:
                    logger.exception(
                        f"{query} failed. Check if cable is plugged "
                        "in correctly",
                        exc_info=e)
                    connection_error[query] = True
                    raise e
                while timer() - start_time < loops[query]:
                    time.sleep(0.1)
        except Exception as e:
            print(e)
            loops[query] = -1
            raise e

    def stop_loop(query):
        loops[query] = -1

    def control_loop():
        timer = timeit.default_timer
        start_time = timer()
        successful_reconnects = 0
        retries = 0
        while True:
            if fluke.is_connected is False or \
                    any(connection_error.values()) is True:
                try:
                    retries = retries + 1
                    logger.error(f"Device is not connected. retry {retries}")
                    fluke.connect()
                    if not fluke.is_connected:
                        # check if serial port is found and connected
                        logger.error("Reconnect failed. Is cable plugged in?")
                    else:
                        try:
                            # get status to ensure fluke is connected again
                            status = fluke.status
                            logger.info(
                                f"Reconnected to device. Status: {status}")

                            # reset error dict
                            for k in connection_error.keys():
                                connection_error[k] = False

                            # reset counters
                            retries = 0
                            successful_reconnects = successful_reconnects + 1
                        except TimeoutError as e:
                            logger.error(
                                "Found device, but got no answer. Check "
                                "if cable is plugged into device")
                except SerialException as e:
                    # change log level if 10 retries failed
                    if retries < 10:
                        level = logging.ERROR
                    else:
                        level = logging.CRITICAL
                    logger.log(level,
                               "Serial port not found, is cable plugged into Computer?",
                               exc_info=e)
            else:
                if all([v < 0.0 for v in loops.values()]):
                    # no loops running, print meditation msg
                    uptime = time.strftime('%Hh %Mm %Ss',
                                           time.gmtime(timer() - start_time))
                    logger.info(f"guru meditation. . ."
                                f", up since {uptime}"
                                f", reconnected {successful_reconnects} times")

            # Doesnt matter whats going on, take some rest for some seconds
            # in each case
            wait_start = timer()
            while timer() - wait_start < 3.0:
                time.sleep(1.0)

    ctx = zerorpc.Context()
    ctx.register_middleware({
        # 'resolve_endpoint':           [],
        # 'load_task_context':          [],
        'get_task_context': lambda: dict(device_name=fluke.__class__.__name__),
        # 'server_before_exec':         [],
        # 'server_after_exec':          [],
        # 'server_inspect_exception':   [],
        # 'client_handle_remote_error': [],
        # 'client_before_request':      [],
        # 'client_after_request':       [],
        # 'client_patterns_list':       [],
    })

    worker = zerorpc.Server(
        context=ctx,
        methods={
            "__name__":    fluke.__class__.__name__,
            "holdOff":     fluke.hold_off,
            "minMax":      fluke.min_max,
            "status":      lambda: fluke.status,
            "isConnected": lambda: fluke.is_connected,
            "execute":     fluke.execute,
            "startLoop":   start_loop,
            "stopLoop":    stop_loop
        })

    if serve_type == "bind":
        worker.bind(endpoint=endpoint)
        click.echo(f"Bound to {endpoint}", color="green")

    if serve_type == "connect":
        worker.connect(endpoint)
        click.echo(f"Connected to {endpoint}", color="green")

    greenlets = [gevent.spawn(worker.run),
                 gevent.spawn_later(5, control_loop)]
    gevent.joinall(greenlets)


if __name__ == "__main__":
    main()
