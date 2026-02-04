"""ASCII graph generation for performance visualization."""
from typing import List, Dict


class GraphGenerator:
    def __init__(self, height: int = 15, width: int = 60):
        self.height = height
        self.width = width
    
    def generate(self, measurements: List[Dict]) -> str:
        """Generate ASCII graph from measurements."""
        if not measurements or all(m['duration'] is None for m in measurements):
            return "No data to graph"
        
        durations = [m['duration'] for m in measurements if m['duration'] is not None]
        if not durations:
            return "No valid measurements"
        
        min_val = min(durations)
        max_val = max(durations)
        
        if max_val == min_val:
            max_val = min_val + 1
        
        lines = []
        
        for i in range(self.height, 0, -1):
            threshold = min_val + (max_val - min_val) * (i / self.height)
            line = f"{threshold:6.2f}s |"
            
            for m in measurements[:self.width]:
                if m['duration'] is None:
                    line += " "
                elif m['duration'] >= threshold:
                    line += "█" if m['passed'] else "▓"
                else:
                    line += " "
            
            lines.append(line)
        
        lines.append("       " + "-" * min(len(measurements), self.width))
        
        commit_line = "        "
        for i, m in enumerate(measurements[:self.width]):
            if i % 5 == 0:
                commit_line += "|"
            else:
                commit_line += " "
        lines.append(commit_line)
        
        return "\n".join(lines)