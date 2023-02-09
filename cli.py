import click
from typing import List, Tuple, IO
import logging
from pathlib import Path

from traffic_comparator.data_loader import DataLoader
from traffic_comparator.analyzer import Analyzer


# Click is a python library that streamlines creating command line interfaces
# in a more composable & readable way than argparse.
# This line sets up a group of cli entrypoints -- currently the commands available
# are `run` and `available_reports`.
@click.group()
def cli():
    pass


@cli.command()
@click.option("--primary-log-file", type=click.Path(), required=True,
              help="Path to the log file from the primary cluster.")
@click.option("--shadow-log-file", type=click.Path(), required=True,
              help="Path to the log file from the shadow cluster.")
@click.option("--log-file-format", type=str, required=True,
              help="Specification for the log file format (must be supported by a LogFileLoader).")
@click.option("--display-reports", multiple=True,
              help="A list of reports that should be printed (in a summary form) to stdout.")
@click.option("--export-reports", type=click.Tuple([str, click.File('w')]), multiple=True,
              help="A list of reports to export and the file path to export it to. This can be '-' for stdout.")
@click.option('-v', '--verbose', count=True)
def run(primary_log_file: Path, shadow_log_file: Path, log_file_format: str,
        display_reports: List[str], export_reports: List[Tuple[str, IO]], verbose: int):
    if verbose == 1:
        logging.getLogger().setLevel(logging.INFO)
    if verbose == 2:
        logging.getLogger().setLevel(logging.DEBUG)

    data_loader = DataLoader(primary_log_file, shadow_log_file, log_file_format)
    analyzer = Analyzer(data_loader)
    analyzer.analyze()

    # Print summary reports to stdout
    for report in display_reports:
        click.echo(f"{report}:\n")
        click.echo(analyzer.generate_report(report))
        click.echo()

    # Write exported reports to file
    for report, export_file in export_reports:
        analyzer.generate_report(report, export=True, export_file=export_file)
        click.echo(f"{report} was exported to {export_file.name}")


@cli.command()
def available_reports():
    reports = Analyzer.available_reports()
    for report, description in reports.items():
        click.echo(f"{report}: {description}")
