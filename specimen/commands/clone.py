import typer
from rich.console import Console
from specimen.services.specimen_service import SpecimenService
from specimen.exceptions import SpecimenError

console = Console()

def clone_command(
    parent: str = typer.Argument(..., help="Nombre del specimen original (padre)"),
    child: str = typer.Argument(..., help="Nombre del nuevo specimen clonado (hijo)"),
    size: int = typer.Option(..., "--size", help="Tamaño límite en MB para el nuevo clon"),
):
    """Crea un clon de un specimen existente."""
    try:
        config = SpecimenService.clone_specimen(parent, child, size)
        console.print(
            f"[green]✔ Specimen '[bold]{config.name}[/bold]' clonado exitosamente "
            f"a partir de '[bold]{config.parent}[/bold]' ({config.size_mb} MB).[/green]"
        )
    except SpecimenError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Error inesperado:[/red] {e}")
        raise typer.Exit(code=1)
