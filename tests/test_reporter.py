"""Tests for Reporter functionality."""
import pytest
import json
import csv
from pathlib import Path
from perf_bisect.reporter import Reporter


@pytest.fixture
def sample_result():
    """Sample bisect result data."""
    return {
        'good_commit': 'abc123',
        'bad_commit': 'def456',
        'threshold': 1.0,
        'regression_commit': 'mid789',
        'regression_message': 'Added slow code',
        'measurements': [
            {'commit': 'abc123', 'duration': 0.5, 'passed': True, 'message': 'Good'},
            {'commit': 'mid789', 'duration': 1.5, 'passed': False, 'message': 'Bad'},
            {'commit': 'def456', 'duration': 2.0, 'passed': False, 'message': 'Worse'}
        ]
    }


@pytest.fixture
def reporter(tmp_path):
    """Create reporter with temp directory."""
    reporter = Reporter()
    reporter.allowed_base = tmp_path
    return reporter


def test_print_summary_with_regression(sample_result, capsys):
    """Test summary output with regression found."""
    reporter = Reporter()
    reporter.print_summary(sample_result)
    
    captured = capsys.readouterr()
    assert 'Regression found' in captured.out
    assert 'mid789' in captured.out
    assert 'Added slow code' in captured.out


def test_print_summary_no_regression(capsys):
    """Test summary output without regression."""
    result = {
        'good_commit': 'abc123',
        'bad_commit': 'def456',
        'threshold': 1.0,
        'regression_commit': None,
        'regression_message': None,
        'measurements': []
    }
    
    reporter = Reporter()
    reporter.print_summary(result)
    
    captured = capsys.readouterr()
    assert 'No regression found' in captured.out


def test_save_json_report(reporter, sample_result, tmp_path):
    """Test saving report as JSON."""
    output_file = tmp_path / 'results.json'
    reporter.save_report(sample_result, str(output_file))
    
    assert output_file.exists()
    with open(output_file) as f:
        data = json.load(f)
    
    assert data['regression_commit'] == 'mid789'
    assert len(data['measurements']) == 3


def test_save_csv_report(reporter, sample_result, tmp_path):
    """Test saving report as CSV."""
    output_file = tmp_path / 'results.csv'
    reporter.save_report(sample_result, str(output_file))
    
    assert output_file.exists()
    with open(output_file) as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    assert len(rows) == 4
    assert rows[0] == ['Commit', 'Duration', 'Passed', 'Message']


def test_save_report_invalid_format(reporter, sample_result, tmp_path):
    """Test error on unsupported format."""
    output_file = tmp_path / 'results.txt'
    
    with pytest.raises(ValueError, match='Unsupported format'):
        reporter.save_report(sample_result, str(output_file))


def test_validate_path_outside_base(reporter, sample_result):
    """Test path validation prevents directory traversal."""
    with pytest.raises(ValueError, match='must be within'):
        reporter.save_report(sample_result, '/tmp/evil.json')


def test_print_summary_dry_run(capsys):
    """Test dry run summary output."""
    result = {
        'dry_run': True,
        'good_commit': 'abc123',
        'bad_commit': 'def456',
        'measurements': [{'commit': 'abc'}, {'commit': 'def'}]
    }
    
    reporter = Reporter()
    reporter.print_summary(result)
    
    captured = capsys.readouterr()
    assert 'DRY RUN' in captured.out
    assert 'Would test 2 commits' in captured.out
