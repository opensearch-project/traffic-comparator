import logging
import sys
from typing import IO, List, Tuple

import click

from traffic_comparator.analyzer import StreamingAnalyzer
from traffic_comparator.data_loader import StreamingDataLoader
from traffic_comparator.report_generator import StreamingReportGenerator


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


@cli.command()
def stream():
    """Process streaming input and print comparisons to OUTPUT (defaults to stdout).
    
    Accept streaming input from stdin in the form of Replayer-generated triples, compare them and
    ouptut (to stdout) json objects with a comparison of the primary and shadow responses."""
    # These set up the data_loader and analyzer listen on stdin and process (compare) data whenever it arrives.
    data_loader = StreamingDataLoader()
    analyzer = StreamingAnalyzer(data_loader)

    # This will actually kick-off accepting stdin input and outputing comparison results to stdout.
    analyzer.start()


@click.option("--export-reports", type=click.Tuple([str, click.File('w')]), multiple=True,
              help="A list of reports to export and the file path to export it to. This can be '-' for stdout.")
@cli.command()
def stream_report(export_reports: List[Tuple[str, IO]]):
    """Process streaming comparisons and print summarized statistics to OUTPUT (defaults to stdout), and exports
    specified reports to the files provided.
    
    Accept streaming input from stdin in the form of trafficreplayer comparisons, and compile statistics on the
    correctness and performance. When the streaming input finishes, reports are also exported to the specified files.
    """
    # The report generator will accept new lines (via `update`) and periodically update the display with
    # the correctness and performance report stats.
    report_generator = StreamingReportGenerator()
    for line in sys.stdin:
        report_generator.update(line)

    report_generator.finalize()

    for report, export_file in export_reports:
        report_generator.generate_final_report(report, export_file)
        click.echo(f"{report} was exported to {export_file.name}")


@cli.command()
def available_reports():
    reports = StreamingReportGenerator.available_reports()
    for report, description in reports.items():
        click.echo(f"{report}: {description}")
