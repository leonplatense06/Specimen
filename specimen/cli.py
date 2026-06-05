import typer
from specimen.console import console
from specimen.commands import (
    new_command,
    list_command,
    info_command,
    rm_command,
    clone_command,
    tree_command,
    enter_command,
    quit_command,
    persist_command,
    unpersist_command,
)
from specimen.services.runtime_service import RuntimeService

app = typer.Typer(
    name="spec",
    help="Isolated terminal environments CLI for command-line tools (Linux-first)",
    no_args_is_help=True,
)

@app.callback()
def main_callback(ctx: typer.Context):
    """
    Main callback executed before any command.
    Checks if there is an active specimen whose shell process has died, and cleans it up.
    """
    # get_active_specimen(auto_cleanup=True) checks the PID
    # and performs automatic cleanup if the process is no longer alive.
    RuntimeService.get_active_specimen(auto_cleanup=True)

# Register commands
app.command(name="new")(new_command)
app.command(name="list")(list_command)
app.command(name="info")(info_command)
app.command(name="rm")(rm_command)
app.command(name="clone")(clone_command)
app.command(name="tree")(tree_command)
app.command(name="enter")(enter_command)
app.command(name="quit")(quit_command)
app.command(name="persist")(persist_command)
app.command(name="unpersist")(unpersist_command)

if __name__ == "__main__":
    app()
