# Specimen

Isolated terminal environments CLI for command-line tools (Linux-first).

Specimen works like a "venv for terminal tools", allowing the creation of isolated terminal environments in Linux.

## Requirements
- Python 3.11+
- Linux

## Development Installation
```bash
pip install -e ".[dev]"
```

## Usage

You can use the `spec` command directly after activating the virtual environment.

For **Bash/Zsh**:
```bash
source .venv/bin/activate
```

For **Fish shell**:
```fish
source .venv/bin/activate.fish
```

### 1. Create a Specimen
Create a new isolated base environment specifying its size limit in MB:
```bash
spec new media --size 256
```

### 2. List Specimens
List all existing specimens showing their type, parent, size usage vs limit, activity state, and creation date:
```bash
spec list
```

### 3. Clone a Specimen
Create an independent copy/snapshot of an existing specimen. The cloned child inherits the parent's directory structure and tools. The child's size limit must be greater than or equal to the parent's actual size on disk:
```bash
spec clone media media-cloned --size 512
```

### 4. Show Details (Info)
Show detailed metadata, system paths, and installed tools for a specific specimen:
```bash
spec info media
```

### 5. Hierarchy Tree
Show parent-child relationships between all specimens as a visual tree:
```bash
spec tree
```

### 6. Delete a Specimen
Remove a specimen and all of its files. It prompts for confirmation unless you use the `--force` / `-f` option. Active specimens cannot be deleted:
```bash
spec rm media-cloned
# Or bypass confirmation
spec rm media-cloned --force
```

## Running Tests
Run the test suite using `pytest`:
```bash
pytest
```
