"""CLI interface for perf-bisect."""
import click
import json
from pathlib import Path
from .bisector import PerformanceBisector
from .reporter import Reporter
from .graph import GraphGenerator


@click.group()
@click.version_option()
def cli():
    """Find performance regressions in git history using bisect."""
    pass


@cli.command()
@click.argument('benchmark_cmd')
@click.option('--good', default='HEAD~10', help='Known good commit')
@click.option('--bad', default='HEAD', help='Known bad commit')
@click.option('--threshold', type=float, required=True, help='Performance threshold in seconds')
@click.option('--timeout', type=int, default=300, help='Benchmark timeout in seconds')
@click.option('--output', type=click.Path(), help='Save results to file (JSON/CSV)')
@click.option('--dry-run', is_flag=True, help='Preview commits without running benchmarks')
@click.option('--verbose', is_flag=True, help='Enable verbose logging')
def run(benchmark_cmd, good, bad, threshold, timeout, output, dry_run, verbose):
    """Run bisect to find performance regression."""
    bisector = PerformanceBisector('.', verbose=verbose)
    
    try:
        result = bisector.bisect(
            benchmark_cmd=benchmark_cmd,
            good_commit=good,
            bad_commit=bad,
            threshold=threshold,
            timeout=timeout,
            dry_run=dry_run
        )
        
        reporter = Reporter()
        reporter.print_summary(result)
        
        if output and not dry_run:
            reporter.save_report(result, output)
            click.echo(f"\nResults saved to: {output}")
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.argument('results_file', type=click.Path(exists=True))
@click.option('--format', type=click.Choice(['table', 'graph', 'both']), default='both')
def report(results_file, format):
    """Display report from saved results."""
    reporter = Reporter()
    try:
        reporter.load_and_display(results_file, format)
    except Exception as e:
        click.echo(f"Error loading report: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.argument('results_file', type=click.Path(exists=True))
@click.option('--height', type=int, default=15, help='Graph height in lines')
@click.option('--width', type=int, default=60, help='Graph width in characters')
def graph(results_file, height, width):
    """Generate ASCII graph from results."""
    try:
        with open(results_file, 'r') as f:
            data = json.load(f)
        
        if 'measurements' not in data:
            click.echo("Invalid results file format", err=True)
            raise click.Abort()
            
        generator = GraphGenerator(height=height, width=width)
        graph_output = generator.generate(data['measurements'])
        click.echo(graph_output)
        
    except Exception as e:
        click.echo(f"Error generating graph: {e}", err=True)
        raise click.Abort()


if __name__ == '__main__':
    cli()