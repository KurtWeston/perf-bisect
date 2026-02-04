"""Tests for PerformanceBisector core functionality."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from perf_bisect.bisector import PerformanceBisector


@pytest.fixture
def mock_repo():
    """Create mock git repository."""
    repo = Mock()
    repo.git = Mock()
    
    good_commit = Mock()
    good_commit.hexsha = 'abc123'
    good_commit.summary = 'Good commit'
    
    bad_commit = Mock()
    bad_commit.hexsha = 'def456'
    bad_commit.summary = 'Bad commit'
    
    mid_commit = Mock()
    mid_commit.hexsha = 'mid789'
    mid_commit.summary = 'Middle commit'
    
    repo.commit = Mock(side_effect=lambda x: good_commit if 'good' in x else bad_commit)
    repo.iter_commits = Mock(return_value=[good_commit, mid_commit, bad_commit])
    
    return repo


@patch('perf_bisect.bisector.Repo')
def test_bisect_finds_regression(mock_repo_class, mock_repo):
    """Test successful regression detection."""
    mock_repo_class.return_value = mock_repo
    bisector = PerformanceBisector('.', verbose=False)
    bisector.run_benchmark = Mock(side_effect=[0.5, 0.8, 1.5])
    
    result = bisector.bisect(
        benchmark_cmd='python bench.py',
        good_commit='HEAD~10',
        bad_commit='HEAD',
        threshold=1.0,
        timeout=300
    )
    
    assert result['regression_commit'] is not None
    assert result['threshold'] == 1.0
    assert len(result['measurements']) > 0


@patch('perf_bisect.bisector.Repo')
def test_bisect_no_regression(mock_repo_class, mock_repo):
    """Test when no regression is found."""
    mock_repo_class.return_value = mock_repo
    bisector = PerformanceBisector('.', verbose=False)
    bisector.run_benchmark = Mock(return_value=0.5)
    
    result = bisector.bisect(
        benchmark_cmd='python bench.py',
        good_commit='HEAD~10',
        bad_commit='HEAD',
        threshold=1.0
    )
    
    assert result['regression_commit'] is None


@patch('perf_bisect.bisector.Repo')
def test_bisect_dry_run(mock_repo_class, mock_repo):
    """Test dry run mode."""
    mock_repo_class.return_value = mock_repo
    bisector = PerformanceBisector('.', verbose=False)
    
    result = bisector.bisect(
        benchmark_cmd='python bench.py',
        good_commit='HEAD~10',
        bad_commit='HEAD',
        threshold=1.0,
        dry_run=True
    )
    
    assert result['dry_run'] is True
    assert 'measurements' in result


@patch('subprocess.run')
def test_run_benchmark_success(mock_run):
    """Test successful benchmark execution."""
    mock_run.return_value = Mock(returncode=0, stdout='Duration: 1.234s', stderr='')
    
    with patch('perf_bisect.bisector.Repo'):
        bisector = PerformanceBisector('.')
        duration = bisector.run_benchmark('python bench.py', timeout=300)
        
        assert duration == 1.234
        mock_run.assert_called_once()


@patch('subprocess.run')
def test_run_benchmark_timeout(mock_run):
    """Test benchmark timeout handling."""
    import subprocess
    mock_run.side_effect = subprocess.TimeoutExpired('cmd', 300)
    
    with patch('perf_bisect.bisector.Repo'):
        bisector = PerformanceBisector('.')
        
        with pytest.raises(subprocess.TimeoutExpired):
            bisector.run_benchmark('python bench.py', timeout=300)


@patch('subprocess.run')
def test_run_benchmark_json_output(mock_run):
    """Test parsing JSON benchmark output."""
    mock_run.return_value = Mock(
        returncode=0,
        stdout='{"duration": 2.5, "memory": 100}',
        stderr=''
    )
    
    with patch('perf_bisect.bisector.Repo'):
        bisector = PerformanceBisector('.')
        duration = bisector.run_benchmark('python bench.py', timeout=300)
        
        assert duration == 2.5


@patch('subprocess.run')
def test_run_benchmark_failure(mock_run):
    """Test benchmark command failure."""
    mock_run.return_value = Mock(returncode=1, stdout='', stderr='Error occurred')
    
    with patch('perf_bisect.bisector.Repo'):
        bisector = PerformanceBisector('.')
        
        with pytest.raises(RuntimeError, match='Benchmark failed'):
            bisector.run_benchmark('python bench.py', timeout=300)
