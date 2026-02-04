# perf-bisect

Automatically find performance regressions in git history using bisect and benchmarks

## Features

- Automated git bisect workflow for performance regression detection
- Execute custom benchmark command on each commit during bisection
- Configurable performance threshold (execution time or memory usage)
- Support for both absolute thresholds and percentage degradation
- Parse benchmark output from various formats (JSON, plain text with regex)
- Generate visual ASCII graphs showing performance trends across commits
- Export detailed results to CSV and JSON formats
- Dry-run mode to preview bisect range without running benchmarks
- Resume interrupted bisect sessions from saved state
- Configurable timeout for benchmark execution
- Automatic detection of good/bad commits based on threshold
- Summary report showing the exact commit that introduced regression
- Support for custom git ref ranges (not just HEAD)
- Verbose logging mode for debugging bisect issues

## How to Use

Use this project when you need to:

- Quickly solve problems related to perf-bisect
- Integrate python functionality into your workflow
- Learn how python handles common patterns with click

## Installation

```bash
# Clone the repository
git clone https://github.com/KurtWeston/perf-bisect.git
cd perf-bisect

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Built With

- python using click

## Dependencies

- `click>=8.0.0`
- `gitpython>=3.1.0`
- `tabulate>=0.9.0`
- `pytest>=7.0.0`
- `pytest-cov>=4.0.0`

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
