"""Generate and display performance reports."""
import json
import csv
from pathlib import Path
from typing import Dict, List
from tabulate import tabulate
from .graph import GraphGenerator


class Reporter:
    def __init__(self):
        self.allowed_base = Path.cwd()
    
    def print_summary(self, result: Dict) -> None:
        """Print bisect summary to terminal."""
        if result.get('dry_run'):
            print("\n=== DRY RUN ===")
            print(f"Would test {len(result['measurements'])} commits")
            print(f"Range: {result['good_commit'][:7]}..{result['bad_commit'][:7]}")
            return
        
        print("\n=== Performance Bisect Results ===")
        print(f"Good commit: {result['good_commit'][:7]}")
        print(f"Bad commit:  {result['bad_commit'][:7]}")
        print(f"Threshold:   {result['threshold']}s")
        
        if result['regression_commit']:
            print(f"\n🔴 Regression found at: {result['regression_commit'][:7]}")
            print(f"Message: {result['regression_message']}")
        else:
            print("\n✅ No regression found")
        
        print(f"\nTested {len(result['measurements'])} commits\n")
        
        table_data = []
        for m in result['measurements']:
            status = '✅' if m['passed'] else '❌'
            table_data.append([
                m['commit'][:7],
                f"{m['duration']:.3f}s",
                status,
                m['message'][:50]
            ])
        
        print(tabulate(table_data, headers=['Commit', 'Duration', 'Status', 'Message']))
    
    def save_report(self, result: Dict, output_path: str) -> None:
        """Save report to file with path validation."""
        output_path = self._validate_path(output_path)
        
        if output_path.suffix == '.json':
            self._save_json(result, output_path)
        elif output_path.suffix == '.csv':
            self._save_csv(result, output_path)
        else:
            raise ValueError(f"Unsupported format: {output_path.suffix}")
    
    def _validate_path(self, path: str) -> Path:
        """Validate output path is safe."""
        output_path = Path(path).resolve()
        
        try:
            output_path.relative_to(self.allowed_base)
        except ValueError:
            raise ValueError(f"Output path must be within {self.allowed_base}")
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        return output_path
    
    def _save_json(self, result: Dict, path: Path) -> None:
        """Save results as JSON."""
        with open(path, 'w') as f:
            json.dump(result, f, indent=2)
    
    def _save_csv(self, result: Dict, path: Path) -> None:
        """Save results as CSV."""
        with open(path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Commit', 'Duration', 'Passed', 'Message'])
            
            for m in result['measurements']:
                writer.writerow([
                    m['commit'],
                    m['duration'],
                    m['passed'],
                    m['message']
                ])
    
    def load_and_display(self, results_file: str, format: str) -> None:
        """Load and display saved results with validation."""
        with open(results_file, 'r') as f:
            data = json.load(f)
        
        if not self._validate_result_schema(data):
            raise ValueError("Invalid results file schema")
        
        if format in ['table', 'both']:
            self.print_summary(data)
        
        if format in ['graph', 'both'] and not data.get('dry_run'):
            print("\n=== Performance Graph ===")
            generator = GraphGenerator()
            graph = generator.generate(data['measurements'])
            print(graph)
    
    def _validate_result_schema(self, data: Dict) -> bool:
        """Validate loaded JSON has expected structure."""
        required_keys = ['good_commit', 'bad_commit', 'measurements']
        if not all(key in data for key in required_keys):
            return False
        
        if not isinstance(data['measurements'], list):
            return False
        
        for m in data['measurements']:
            if not isinstance(m, dict):
                return False
            if 'commit' not in m or 'message' not in m:
                return False
        
        return True