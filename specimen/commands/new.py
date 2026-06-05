import typer
from rich.console import Console
from specimen.services.specimen_service import SpecimenService
from specimen.exceptions import SpecimenError

console = Console()

def new_command(
    name: str = typer.Argument(..., help="Nombre del specimen"),
    size: int = typer.Option(..., "--size", help="Tamaño límite en MB para el specimen"),
):
    """Crea un specimen base nuevo."""
    try:
        config = SpecimenService.create_specimen(name, size)
        console.print(f"[green]✔ Specimen '[bold]{config.name}[/bold]' creado exitosamente ({config.size_mb} MB).[/green]")
    except SpecimenError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Error inesperado:[/red] {e}")
        raise typer.Exit(code=1)
