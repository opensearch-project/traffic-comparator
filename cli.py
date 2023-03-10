import logging
import sys
from pathlib import Path
from typing import IO, List, Tuple

import click

from traffic_comparator.analyzer import Analyzer, StreamingAnalyzer
from traffic_comparator.data_loader import DataLoader, StreamingDataLoader
from traffic_comparator.report_generator import ReportGenerator, StreamingReportGenerator


# Click is a python library that streamlines creating command line interfaces
# in a more composable & readable way than argparse.
# https://click.palletsprojects.com/en/8.1.x/api/
# This line sets up a group of cli entrypoints -- currently the commands available
# are `run` and `available_reports`.
@click.group()
@click.option('-v', '--verbose', count=True)
def cli(verbose: int):
    if verbose == 1:
        logging.basicConfig(level=logging.INFO)
    if verbose >= 2:
        logging.basicConfig(level=logging.DEBUG)

    pass


log_file_documentation = """Path to a log file. This option is required at least once and can be provided many times.
If the file format has seperate primary and shadow logs,
the first use should be the primary log and the second the shadow.
"""


@cli.command()
@click.option("--log-file", "log_files", type=click.Path(), required=True, multiple=True,
              help=log_file_documentation)
@click.option("--log-file-format", type=str, required=True,
              help="Specification for the log file format (must be supported by a LogFileLoader).")
@click.option("--display-reports", multiple=True,
              help="A list of reports that should be printed (in a summary form) to stdout.")
@click.option("--export-reports", type=click.Tuple([str, click.File('w')]), multiple=True,
              help="A list of reports to export and the file path to export it to. This can be '-' for stdout.")
def run(log_files: List[Path], log_file_format: str,
        display_reports: List[str], export_reports: List[Tuple[str, IO]]):
    data_loader = DataLoader(log_files, log_file_format)
    analyzer = Analyzer(data_loader)
    report_generator = ReportGenerator(*analyzer.analyze())

    # Print summary reports to stdout
    for report in display_reports:
        click.echo(f"{report}:\n")
        click.echo(report_generator.generate(report))
        click.echo()

    # Write exported reports to file
    for report, export_file in export_reports:
        report_generator.generate(report, export=True, export_file=export_file)
        click.echo(f"{report} was exported to {export_file.name}")


@cli.command()
def stream():
    # These set up the data_loader and analyzer listen on stdin and process (compare) data whenever it arrives.
    data_loader = StreamingDataLoader()
    analyzer = StreamingAnalyzer(data_loader)

    # This will actually kick-off accepting stdin input and outputing comparison results to stdout.
    analyzer.start()


@cli.command()
def stream_report():
    # The report generator will accept new lines (via `update`) and periodically update the display with
    # the correctness and performance report stats.
    report_generator = StreamingReportGenerator()
    for line in sys.stdin:
        report_generator.update(line)

    report_generator.finalize()


@cli.command()
def available_reports():
    reports = ReportGenerator.available_reports()
    for report, description in reports.items():
        click.echo(f"{report}: {description}")
