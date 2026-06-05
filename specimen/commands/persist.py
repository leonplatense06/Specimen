import typer
from rich.console import Console
from specimen.services.specimen_service import SpecimenService
from specimen.exceptions import SpecimenError

console = Console()

def persist_command(
    name: str = typer.Argument(..., help="Nombre del specimen a marcar como persistente"),
    unset: bool = typer.Option(
        False,
        "--unset",
        "-u",
        help="Quita la persistencia del specimen (volverá a borrarse al salir sin -c)"
    )
):
    """Establece o quita la persistencia de un specimen."""
    try:
        persistent = not unset
        SpecimenService.set_persistence(name, persistent)
        
        status_str = "persistente" if persistent else "no persistente"
        console.print(f"[green]✔ El specimen '[bold]{name.lower()}[/bold]' ahora es {status_str}.[/green]")
    except SpecimenError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Error inesperado:[/red] {e}")
        raise typer.Exit(code=1)
