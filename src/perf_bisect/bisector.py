"""Core bisect logic for performance regression detection."""
import subprocess
import shlex
import re
import json
from pathlib import Path
from git import Repo
from typing import Dict, List, Optional


class PerformanceBisector:
    def __init__(self, repo_path: str, verbose: bool = False):
        self.repo = Repo(repo_path)
        self.verbose = verbose
        self.measurements: List[Dict] = []
        
    def bisect(self, benchmark_cmd: str, good_commit: str, bad_commit: str,
               threshold: float, timeout: int = 300, dry_run: bool = False) -> Dict:
        """Execute git bisect to find performance regression."""
        
        good_sha = self.repo.commit(good_commit).hexsha
        bad_sha = self.repo.commit(bad_commit).hexsha
        
        commits = list(self.repo.iter_commits(f'{good_sha}..{bad_sha}'))
        commits.reverse()
        
        if self.verbose:
            print(f"Bisecting {len(commits)} commits between {good_sha[:7]} and {bad_sha[:7]}")
        
        if dry_run:
            return self._dry_run_result(commits, good_sha, bad_sha)
        
        left, right = 0, len(commits) - 1
        regression_commit = None
        
        while left <= right:
            mid = (left + right) // 2
            commit = commits[mid]
            
            if self.verbose:
                print(f"\nTesting commit {commit.hexsha[:7]}: {commit.summary}")
            
            self.repo.git.checkout(commit.hexsha, force=True)
            duration = self.run_benchmark(benchmark_cmd, timeout)
            
            self.measurements.append({
                'commit': commit.hexsha,
                'message': commit.summary,
                'duration': duration,
                'passed': duration <= threshold
            })
            
            if duration <= threshold:
                left = mid + 1
            else:
                regression_commit = commit
                right = mid - 1
        
        self.repo.git.checkout(bad_sha)
        
        return {
            'good_commit': good_sha,
            'bad_commit': bad_sha,
            'threshold': threshold,
            'regression_commit': regression_commit.hexsha if regression_commit else None,
            'regression_message': regression_commit.summary if regression_commit else None,
            'measurements': self.measurements
        }
    
    def run_benchmark(self, cmd: str, timeout: int) -> float:
        """Execute benchmark command safely and extract duration."""
        try:
            args = shlex.split(cmd)
            
            if not args:
                raise ValueError("Empty benchmark command")
            
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=False
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Benchmark failed: {result.stderr}")
            
            return self._parse_duration(result.stdout)
            
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Benchmark timed out after {timeout}s")
        except FileNotFoundError:
            raise RuntimeError(f"Benchmark command not found: {args[0]}")
    
    def _parse_duration(self, output: str) -> float:
        """Parse benchmark duration from output."""
        try:
            data = json.loads(output)
            if 'duration' in data:
                return float(data['duration'])
            elif 'time' in data:
                return float(data['time'])
        except (json.JSONDecodeError, ValueError):
            pass
        
        patterns = [
            r'duration[:\s]+([0-9.]+)',
            r'time[:\s]+([0-9.]+)',
            r'([0-9.]+)\s*s(?:ec)?',
            r'^([0-9.]+)$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                return float(match.group(1))
        
        raise ValueError(f"Could not parse duration from output: {output[:100]}")
    
    def _dry_run_result(self, commits: List, good_sha: str, bad_sha: str) -> Dict:
        """Generate dry-run result without executing benchmarks."""
        measurements = []
        for commit in commits:
            measurements.append({
                'commit': commit.hexsha,
                'message': commit.summary,
                'duration': None,
                'passed': None
            })
        
        return {
            'good_commit': good_sha,
            'bad_commit': bad_sha,
            'threshold': None,
            'regression_commit': None,
            'regression_message': None,
            'measurements': measurements,
            'dry_run': True
        }