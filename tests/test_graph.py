"""Tests for GraphGenerator ASCII visualization."""
import pytest
from perf_bisect.graph import GraphGenerator


@pytest.fixture
def sample_measurements():
    """Sample measurement data."""
    return [
        {'commit': 'abc', 'duration': 0.5, 'passed': True, 'message': 'Fast'},
        {'commit': 'def', 'duration': 1.0, 'passed': True, 'message': 'OK'},
        {'commit': 'ghi', 'duration': 2.0, 'passed': False, 'message': 'Slow'},
        {'commit': 'jkl', 'duration': 1.5, 'passed': False, 'message': 'Bad'}
    ]


def test_generate_basic_graph(sample_measurements):
    """Test basic graph generation."""
    generator = GraphGenerator(height=10, width=40)
    graph = generator.generate(sample_measurements)
    
    assert isinstance(graph, str)
    assert '|' in graph
    assert 's' in graph
    lines = graph.split('\n')
    assert len(lines) > 10


def test_generate_empty_measurements():
    """Test graph with no data."""
    generator = GraphGenerator()
    graph = generator.generate([])
    
    assert graph == "No data to graph"


def test_generate_all_none_durations():
    """Test graph with all None durations."""
    measurements = [
        {'commit': 'abc', 'duration': None, 'passed': False, 'message': 'Failed'}
    ]
    
    generator = GraphGenerator()
    graph = generator.generate(measurements)
    
    assert graph == "No data to graph"


def test_generate_same_durations():
    """Test graph when all durations are identical."""
    measurements = [
        {'commit': 'abc', 'duration': 1.0, 'passed': True, 'message': 'Same'},
        {'commit': 'def', 'duration': 1.0, 'passed': True, 'message': 'Same'}
    ]
    
    generator = GraphGenerator(height=5, width=20)
    graph = generator.generate(measurements)
    
    assert isinstance(graph, str)
    assert '1.00s' in graph or '2.00s' in graph


def test_generate_custom_dimensions(sample_measurements):
    """Test graph with custom height and width."""
    generator = GraphGenerator(height=20, width=80)
    graph = generator.generate(sample_measurements)
    
    lines = graph.split('\n')
    assert len(lines) > 20


def test_generate_mixed_none_durations():
    """Test graph with some None durations."""
    measurements = [
        {'commit': 'abc', 'duration': 1.0, 'passed': True, 'message': 'OK'},
        {'commit': 'def', 'duration': None, 'passed': False, 'message': 'Failed'},
        {'commit': 'ghi', 'duration': 2.0, 'passed': False, 'message': 'Slow'}
    ]
    
    generator = GraphGenerator()
    graph = generator.generate(measurements)
    
    assert isinstance(graph, str)
    assert 'No valid measurements' not in graph
