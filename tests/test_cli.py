"""Tests for CLI interface."""
import pytest
from click.testing import CliRunner
from unittest.mock import patch, Mock
from perf_bisect.cli import cli


@pytest.fixture
def runner():
    """Create CLI test runner."""
    return CliRunner()


@patch('perf_bisect.cli.PerformanceBisector')
def test_run_command_success(mock_bisector_class, runner):
    """Test successful run command."""
    mock_bisector = Mock()
    mock_bisector.bisect.return_value = {
        'good_commit': 'abc123',
        'bad_commit': 'def456',
        'threshold': 1.0,
        'regression_commit': None,
        'measurements': []
    }
    mock_bisector_class.return_value = mock_bisector
    
    result = runner.invoke(cli, ['run', 'python bench.py', '--threshold', '1.0'])
    
    assert result.exit_code == 0
    mock_bisector.bisect.assert_called_once()


@patch('perf_bisect.cli.PerformanceBisector')
def test_run_command_with_output(mock_bisector_class, runner, tmp_path):
    """Test run command with output file."""
    mock_bisector = Mock()
    mock_bisector.bisect.return_value = {
        'good_commit': 'abc',
        'bad_commit': 'def',
        'threshold': 1.0,
        'regression_commit': None,
        'measurements': []
    }
    mock_bisector_class.return_value = mock_bisector
    
    output_file = tmp_path / 'results.json'
    result = runner.invoke(cli, [
        'run', 'python bench.py',
        '--threshold', '1.0',
        '--output', str(output_file)
    ])
    
    assert result.exit_code == 0
    assert 'Results saved' in result.output


@patch('perf_bisect.cli.PerformanceBisector')
def test_run_command_dry_run(mock_bisector_class, runner):
    """Test dry run mode."""
    mock_bisector = Mock()
    mock_bisector.bisect.return_value = {
        'dry_run': True,
        'good_commit': 'abc',
        'bad_commit': 'def',
        'measurements': []
    }
    mock_bisector_class.return_value = mock_bisector
    
    result = runner.invoke(cli, [
        'run', 'python bench.py',
        '--threshold', '1.0',
        '--dry-run'
    ])
    
    assert result.exit_code == 0


@patch('perf_bisect.cli.PerformanceBisector')
def test_run_command_error(mock_bisector_class, runner):
    """Test error handling in run command."""
    mock_bisector = Mock()
    mock_bisector.bisect.side_effect = Exception('Test error')
    mock_bisector_class.return_value = mock_bisector
    
    result = runner.invoke(cli, ['run', 'python bench.py', '--threshold', '1.0'])
    
    assert result.exit_code != 0
    assert 'Error' in result.output


def test_graph_command(runner, tmp_path):
    """Test graph command."""
    import json
    
    results_file = tmp_path / 'results.json'
    with open(results_file, 'w') as f:
        json.dump({
            'measurements': [
                {'commit': 'abc', 'duration': 1.0, 'passed': True, 'message': 'OK'}
            ]
        }, f)
    
    result = runner.invoke(cli, ['graph', str(results_file)])
    
    assert result.exit_code == 0


def test_version_option(runner):
    """Test version flag."""
    result = runner.invoke(cli, ['--version'])
    
    assert result.exit_code == 0
    assert '0.1.0' in result.output or 'version' in result.output.lower()
