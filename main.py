import click
from pathlib import Path
import sys
from ..common.logger import setup_logging
from .commands import (
    generate_command,
    analyze_command,
    report_command,
    visualize_command,
    stats_command,
    profile_command,
    validate_command,
    benchmark_command,
    config_command,
)


@click.group()
@click.option('--debug', is_flag=True, help='Enable debug logging')
@click.option('--log-file', type=Path, help='Log to file')
@click.version_option(version='1.0.0', prog_name='TrafficLab')
def cli(debug: bool, log_file: Path) -> None:
    """TrafficLab - Advanced network traffic generation and analysis framework."""
    if debug:
        setup_logging('DEBUG', log_file)
    else:
        setup_logging('INFO', log_file)


# Add commands
cli.add_command(generate_command)
cli.add_command(analyze_command)
cli.add_command(report_command)
cli.add_command(visualize_command)
cli.add_command(stats_command)
cli.add_command(profile_command)
cli.add_command(validate_command)
cli.add_command(benchmark_command)
cli.add_command(config_command)


if __name__ == '__main__':
    cli()
