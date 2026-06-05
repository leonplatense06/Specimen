# Specimen

Isolated terminal environments CLI for command-line tools (Linux-first).

Specimen works like a "venv for terminal tools", allowing the creation of isolated terminal environments in Linux.

## Requirements
- Python 3.11+
- Linux

## Installation

### 1. Global/User-wide Installation (Recommended)
You can install Specimen user-wide. The installer automatically sets up an isolated environment under `~/.specimen/venv` and symlinks the `spec` executable to `~/.local/bin/spec` (which is typically in your `PATH`):

```bash
./install.sh
```

To install in **development (editable) mode**, where local modifications to this codebase are instantly applied without reinstalling:
```bash
./install.sh --dev
```

To **uninstall** Specimen from your system:
```bash
./uninstall.sh
```

### 2. Local Development Environment
Alternatively, you can install the package inside your own local virtual environment:
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
spec new my-specimen --size 256
```

### 2. List Specimens
List all existing specimens showing their type, parent, size usage vs limit, activity state, and creation date:
```bash
spec list
```

### 3. Enter a Specimen (Activation)
Enter a specimen environment and launch an isolated subshell (supports Bash, Zsh, and Fish):
```bash
spec enter my-specimen
```
Within the subshell, your prompt will be prefixed (e.g. `(my-specimen) user@host:~$`) and key environment variables (`PATH`, `HOME`, `TMPDIR`, and XDG paths) will be redirected to the specimen's directories.

### 4. Quit/Exit a Specimen (Deactivation)
Exit the active specimen session.

If the specimen is **not persistent**, quitting without `-c` or `--conserv` will prompt you for confirmation, warning that the specimen will be deleted:
```bash
spec quit
# Are you sure you want to exit? The specimen 'spe' will be deleted. [y/N]:
```

If you confirm, the specimen is deactivated and destroyed. If you want to keep/conserve it on disk, use the `-c` or `--conserv` option to bypass the confirmation:
```bash
spec quit --conserv
# or
spec quit -c
```

If the specimen is marked as **persistent**, `spec quit` will automatically conserve it on disk without prompting for confirmation (even without `-c`).

### 5. Persist a Specimen
Mark a specimen as persistent so that it is automatically conserved when exiting, even if you do not specify `-c` or `--conserv` during `spec quit`. Persistent specimens do not prompt for confirmation on exit.

To make a specimen persistent:
```bash
spec persist my-specimen
```

To remove persistence (it will default to being deleted on exit unless `-c` is used):
```bash
spec unpersist my-specimen
```
Alternatively, you can also use:
```bash
spec persist my-specimen --unset
# or
spec persist my-specimen -u
```

### 6. Clone a Specimen
Create an independent copy/snapshot of an existing specimen. The cloned child inherits the parent's directory structure and tools. The child's size limit must be greater than or equal to the parent's actual size on disk:
```bash
spec clone my-specimen my-specimen-clone --size 512
```

### 7. Show Details (Info)
Show detailed metadata, system paths, and installed tools for a specific specimen:
```bash
spec info my-specimen
```

### 8. Hierarchy Tree
Show parent-child relationships between all specimens as a visual tree:
```bash
spec tree
```

### 9. Delete a Specimen
Remove a specimen and all of its files. It prompts for confirmation unless you use the `--force` / `-f` option. Active specimens cannot be deleted:
```bash
spec rm my-specimen-clone
# Or bypass confirmation
spec rm my-specimen-clone --force
```

## Running Tests
Run the test suite using `pytest`:
```bash
pytest
```
