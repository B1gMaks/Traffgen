import click
from pathlib import Path
import json
import yaml
from typing import Optional
from datetime import datetime

from ..core.config import Config
from ..core.engine import Engine
from ..profiles import load_profile
from ..profiles.base import Profile
from ..exporters import PcapExporter, JSONExporter, YAMLExporter, CSVExporter, MarkdownExporter
from ..importers import PcapImporter
from ..analysis.analyzer import Analyzer
from ..statistics.stats import StatisticsEngine
from ..statistics.reports import ReportGenerator
from ..visualization.renderer import Renderer
from ..common.logger import get_logger

logger = get_logger(__name__)


@click.command('generate')
@click.option('--profile', '-p', default='enterprise', help='Network profile to use')
@click.option('--config', '-c', type=Path, help='Configuration file path')
@click.option('--duration', '-d', type=int, default=3600, help='Duration in seconds')
@click.option('--output', '-o', type=Path, default=Path('traffic.pcap'), help='Output file path')
@click.option('--format', '-f', default='pcap', help='Output format (pcap, json, yaml, csv)')
@click.option('--packets', '-n', type=int, help='Number of packets to generate (overrides duration)')
@click.option('--seed', type=int, help='Random seed for reproducibility')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def generate_command(
    profile: str,
    config: Path,
    duration: int,
    output: Path,
    format: str,
    packets: Optional[int],
    seed: Optional[int],
    verbose: bool,
) -> None:
    """Generate synthetic network traffic."""
    logger.info(f"Starting generation with profile: {profile}")
    
    # Load configuration
    if config and config.exists():
        cfg = Config.from_yaml(config)
    else:
        cfg = Config()
        cfg.profile = profile
        cfg.duration = duration
        cfg.seed = seed
    
    if packets:
        # Override duration for packet count
        # We'll generate until we reach packet count
        cfg.duration = 86400  # 24 hours max
    
    # Create engine
    engine = Engine(cfg)
    
    # Generate packets
    generated_packets = []
    for packet in engine.generate():
        generated_packets.append(packet)
        if packets and len(generated_packets) >= packets:
            break
        
        if verbose and len(generated_packets) % 100 == 0:
            click.echo(f"Generated {len(generated_packets)} packets", err=True)
    
    # Export
    output.parent.mkdir(parents=True, exist_ok=True)
    engine.export(generated_packets, format, output)
    
    click.echo(f"Generated {len(generated_packets)} packets to {output}")


@click.command('analyze')
@click.option('--input', '-i', type=Path, required=True, help='Input PCAP file')
@click.option('--format', '-f', default='pcap', help='Input format (pcap, pcapng)')
@click.option('--output', '-o', type=Path, help='Output JSON file')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def analyze_command(
    input: Path,
    format: str,
    output: Optional[Path],
    verbose: bool,
) -> None:
    """Analyze PCAP file."""
    logger.info(f"Analyzing {input}")
    
    if not input.exists():
        click.echo(f"Error: Input file {input} not found", err=True)
        return
    
    # Import packets
    engine = Engine()
    packets = engine.import_pcap(input)
    
    # Analyze
    analyzer = Analyzer()
    results = analyzer.analyze(packets)
    
    # Output
    if output:
        with open(output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        click.echo(f"Analysis results saved to {output}")
    else:
        # Pretty print to console
        click.echo(json.dumps(results, indent=2, default=str))
    
    click.echo(f"Analyzed {len(packets)} packets")


@click.command('report')
@click.option('--input', '-i', type=Path, required=True, help='Input PCAP file')
@click.option('--output', '-o', type=Path, default=Path('report.md'), help='Output report file')
@click.option('--format', '-f', default='markdown', help='Report format (markdown, html, pdf)')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def report_command(
    input: Path,
    output: Path,
    format: str,
    verbose: bool,
) -> None:
    """Generate analysis report."""
    logger.info(f"Generating report for {input}")
    
    if not input.exists():
        click.echo(f"Error: Input file {input} not found", err=True)
        return
    
    # Import and analyze
    engine = Engine()
    packets = engine.import_pcap(input)
    analyzer = Analyzer()
    results = analyzer.analyze(packets)
    
    # Generate report
    report_gen = ReportGenerator()
    
    if format == 'markdown':
        output_path = output.with_suffix('.md')
        report_gen.save_report(packets, results, output_path)
    elif format == 'html':
        # Simple HTML conversion (would use a proper template in production)
        md_content = report_gen.generate_report(packets, results)
        html_content = f"<html><body><pre>{md_content}</pre></body></html>"
        output_path = output.with_suffix('.html')
        with open(output_path, 'w') as f:
            f.write(html_content)
    else:
        click.echo(f"Unsupported format: {format}", err=True)
        return
    
    click.echo(f"Report saved to {output_path}")


@click.command('visualize')
@click.option('--input', '-i', type=Path, required=True, help='Input PCAP file')
@click.option('--output', '-o', type=Path, required=True, help='Output directory for charts')
@click.option('--type', '-t', default='all', help='Chart type (pie, histogram, timeline, top_talkers, heatmap, communication, flow, dependency, all)')
@click.option('--format', '-f', default='png', help='Output format (png, svg, pdf)')
@click.option('--dpi', type=int, default=300, help='Output DPI')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def visualize_command(
    input: Path,
    output: Path,
    type: str,
    format: str,
    dpi: int,
    verbose: bool,
) -> None:
    """Generate visualizations from PCAP."""
    logger.info(f"Generating visualizations for {input}")
    
    if not input.exists():
        click.echo(f"Error: Input file {input} not found", err=True)
        return
    
    # Import packets
    engine = Engine()
    packets = engine.import_pcap(input)
    
    if not packets:
        click.echo("Error: No packets found in input", err=True)
        return
    
    # Create renderer
    renderer = Renderer()
    
    if type == 'all':
        # Generate all visualizations
        output.mkdir(parents=True, exist_ok=True)
        results = renderer.render_all(packets, output)
        click.echo(f"Generated {len(results['charts']) + len(results['graphs'])} visualizations in {output}")
    else:
        # Generate specific visualization
        output.parent.mkdir(parents=True, exist_ok=True)
        result = renderer.render(packets, type, output)
        if result:
            click.echo(f"Visualization saved to {output}")
        else:
            click.echo(f"Failed to generate {type} visualization", err=True)


@click.command('stats')
@click.option('--input', '-i', type=Path, required=True, help='Input PCAP file')
@click.option('--output', '-o', type=Path, help='Output JSON file')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def stats_command(
    input: Path,
    output: Optional[Path],
    verbose: bool,
) -> None:
    """Show detailed statistics."""
    logger.info(f"Computing statistics for {input}")
    
    if not input.exists():
        click.echo(f"Error: Input file {input} not found", err=True)
        return
    
    # Import packets
    engine = Engine()
    packets = engine.import_pcap(input)
    
    # Compute statistics
    stats_engine = StatisticsEngine()
    results = stats_engine.analyze(packets)
    
    # Output
    if output:
        with open(output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        click.echo(f"Statistics saved to {output}")
    else:
        # Pretty print
        click.echo("=== Traffic Statistics ===")
        for section, data in results.items():
            click.echo(f"\n{section.upper()}:")
            for key, value in data.items():
                click.echo(f"  {key}: {value}")


@click.command('profile')
@click.argument('action', type=click.Choice(['list', 'show', 'generate']))
@click.option('--name', '-n', help='Profile name')
@click.option('--output', '-o', type=Path, help='Output file for generated profile')
def profile_command(action: str, name: Optional[str], output: Optional[Path]) -> None:
    """Manage network profiles."""
    
    if action == 'list':
        from ..profiles import load_profile
        profiles = [
            'enterprise', 'office', 'home', 'university', 'iot',
            'cloud', 'datacenter', 'isp', 'industrial', 'telecom'
        ]
        click.echo("Available profiles:")
        for p in profiles:
            click.echo(f"  - {p}")
    
    elif action == 'show':
        if not name:
            click.echo("Error: --name required for 'show' action", err=True)
            return
        
        try:
            profile = load_profile(name)
            click.echo(f"Profile: {profile.name}")
            click.echo(f"Description: {profile.description}")
            click.echo(f"Total hosts: {profile.get_total_hosts()}")
            click.echo(f"Subnets: {', '.join(profile.subnets)}")
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
    
    elif action == 'generate':
        if not name:
            click.echo("Error: --name required for 'generate' action", err=True)
            return
        
        try:
            profile = load_profile(name)
            if output:
                # Export to YAML
                import yaml
                data = {
                    'name': profile.name,
                    'description': profile.description,
                    'hosts': [
                        {
                            'name': h.name,
                            'type': h.host_type.value,
                            'ip_range': h.ip_range,
                            'count': h.count,
                        }
                        for h in profile.hosts
                    ],
                    'subnets': profile.subnets,
                }
                with open(output, 'w') as f:
                    yaml.dump(data, f, default_flow_style=False)
                click.echo(f"Profile exported to {output}")
            else:
                click.echo(f"Generated profile: {profile.name}")
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)


@click.command('validate')
@click.option('--config', '-c', type=Path, help='Configuration file to validate')
@click.option('--input', '-i', type=Path, help='PCAP file to validate')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def validate_command(
    config: Optional[Path],
    input: Optional[Path],
    verbose: bool,
) -> None:
    """Validate configuration or PCAP file."""
    
    if config:
        try:
            cfg = Config.from_yaml(config)
            click.echo(f"✓ Configuration is valid: {config}")
            if verbose:
                click.echo(f"  Profile: {cfg.profile}")
                click.echo(f"  Duration: {cfg.duration}s")
        except Exception as e:
            click.echo(f"✗ Configuration invalid: {e}", err=True)
    
    if input:
        try:
            engine = Engine()
            packets = engine.import_pcap(input)
            click.echo(f"✓ PCAP file is valid: {input}")
            click.echo(f"  Packets: {len(packets)}")
        except Exception as e:
            click.echo(f"✗ PCAP file invalid: {e}", err=True)


@click.command('benchmark')
@click.option('--profile', '-p', default='enterprise', help='Network profile')
@click.option('--duration', '-d', type=int, default=60, help='Benchmark duration in seconds')
@click.option('--output', '-o', type=Path, help='Output JSON file for results')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def benchmark_command(
    profile: str,
    duration: int,
    output: Optional[Path],
    verbose: bool,
) -> None:
    """Run performance benchmark."""
    import time
    import psutil
    import os
    
    click.echo(f"Running benchmark with profile: {profile}, duration: {duration}s")
    
    # Setup
    cfg = Config()
    cfg.profile = profile
    cfg.duration = duration
    
    engine = Engine(cfg)
    
    # Measure performance
    start_time = time.time()
    packet_count = 0
    bytes_count = 0
    
    process = psutil.Process()
    start_memory = process.memory_info().rss
    
    for packet in engine.generate():
        packet_count += 1
        bytes_count += packet.length
        
        if time.time() - start_time >= duration:
            break
    
    end_time = time.time()
    end_memory = process.memory_info().rss
    
    results = {
        'profile': profile,
        'duration': duration,
        'packets_generated': packet_count,
        'bytes_generated': bytes_count,
        'packets_per_second': packet_count / duration,
        'bytes_per_second': bytes_count / duration,
        'memory_usage_mb': (end_memory - start_memory) / 1024 / 1024,
        'total_time': end_time - start_time,
    }
    
    # Output
    if output:
        with open(output, 'w') as f:
            json.dump(results, f, indent=2)
        click.echo(f"Benchmark results saved to {output}")
    else:
        click.echo("\n=== Benchmark Results ===")
        for key, value in results.items():
            click.echo(f"  {key}: {value}")
    
    click.echo("Benchmark complete!")


@click.command('config')
@click.argument('action', type=click.Choice(['create', 'validate', 'show']))
@click.option('--output', '-o', type=Path, help='Output file')
@click.option('--profile', '-p', default='enterprise', help='Profile to use')
def config_command(action: str, output: Optional[Path], profile: str) -> None:
    """Manage configuration."""
    
    if action == 'create':
        cfg = Config()
        cfg.profile = profile
        
        if output:
            cfg.to_yaml(output)
            click.echo(f"Configuration saved to {output}")
        else:
            # Print to console
            import yaml
            click.echo(yaml.dump(cfg.dict(), default_flow_style=False))
    
    elif action == 'validate':
        if not output:
            click.echo("Error: --output required for 'validate' action", err=True)
            return
        
        try:
            cfg = Config.from_yaml(output)
            click.echo(f"✓ Configuration is valid: {output}")
        except Exception as e:
            click.echo(f"✗ Configuration invalid: {e}", err=True)
    
    elif action == 'show':
        if output:
            try:
                cfg = Config.from_yaml(output)
                import yaml
                click.echo(yaml.dump(cfg.dict(), default_flow_style=False))
            except Exception as e:
                click.echo(f"Error: {e}", err=True)
        else:
            cfg = Config()
            import yaml
            click.echo("Default configuration:")
            click.echo(yaml.dump(cfg.dict(), default_flow_style=False))
