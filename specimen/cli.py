import typer
from rich.console import Console
from specimen.commands import (
    new_command,
    list_command,
    info_command,
    rm_command,
    clone_command,
    tree_command,
)
from specimen.services.runtime_service import RuntimeService

app = typer.Typer(
    name="spec",
    help="CLI de entornos aislados para herramientas de terminal (Linux-first)",
    no_args_is_help=True,
)

console = Console()

@app.callback()
def main_callback(ctx: typer.Context):
    """
    Callback principal que se ejecuta antes de cualquier comando.
    Verifica si hay un specimen activo cuyo proceso de shell haya muerto y lo limpia.
    """
    # get_active_specimen(auto_cleanup=True) realiza el chequeo del PID
    # y la limpieza automática si el proceso ya no está vivo.
    RuntimeService.get_active_specimen(auto_cleanup=True)

# Registrar comandos
app.command(name="new")(new_command)
app.command(name="list")(list_command)
app.command(name="info")(info_command)
app.command(name="rm")(rm_command)
app.command(name="clone")(clone_command)
app.command(name="tree")(tree_command)

if __name__ == "__main__":
    app()
