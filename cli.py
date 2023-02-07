import click
import typing
import logging

from traffic_comparator.load_config_file import load_config_file
from traffic_comparator.data_loader import DataLoader
from traffic_comparator.analyzer import Analyzer


@click.group()
def cli():
    pass


@cli.command()
@click.option("config_file", '--config', type=click.File('r'), required=True,
              help="Config file that specifies the log files and other options (see README)."
              )
@click.option('-v', '--verbose')
def run(config_file: typing.TextIO, verbose: bool):
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    config = load_config_file(config_file)
    data_loader = DataLoader(config)
    analyzer = Analyzer(data_loader)
    analyzer.analyze()
    
    for report in config["reports"]:
        report_name = report["report_name"]
        if report["display"]:
            click.echo(f"{report_name}:\n")
            click.echo(analyzer.generate_report(report_name))
            click.echo()
        if "export_filename" in report:
            export_filename = report["export_filename"]
            click.echo(f"{report_name} was exported to {export_filename}")
            analyzer.generate_report(report_name, export=True, export_filename=export_filename)


@cli.command()
def available_reports():
    reports = Analyzer.available_reports()
    for report, description in reports.items():
        click.echo(f"{report}: {description}")
