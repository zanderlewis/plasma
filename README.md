# Plasma
A developer's toolkit for managing and automating common development tasks.

## Overview
Plasma is a command-line utility that provides a collection of useful commands for developers, organized into categories for easy access.

## Installation
Install the package using `uv`:
```bash
uv add plsma
```

Or clone and install locally:
```bash
git clone https://github.com/zanderlewis/plasma.git
cd plsma
uv install -e .
```

## Usage
The main command is `plasma`. You can:
- List all available commands: `plasma` or `plasma list`
- List commands by category: `plasma list:<category>`
- Run a specific command: `plasma <command> [args]`
- Show version: `plasma --version`
- Show help: `plasma --help`

## Requirements
- Python 3.10+
- Dependencies: click, psutil, rich

## Development
This project uses:
- `uv` for dependency management
- `ruff` for linting and formatting

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
