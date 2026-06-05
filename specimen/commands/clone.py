import typer
from specimen.console import console
from specimen.services.specimen_service import SpecimenService
from specimen.exceptions import SpecimenError

def clone_command(
    parent: str = typer.Argument(..., help="Name of the original specimen (parent)"),
    child: str = typer.Argument(..., help="Name of the new cloned specimen (child)"),
    size: int = typer.Option(..., "--size", help="Size limit in MB for the new clone"),
):
    """Creates a clone of an existing specimen."""
    try:
        config = SpecimenService.clone_specimen(parent, child, size)
        console.print(
            f"[green]✔ Specimen '[bold]{config.name}[/bold]' cloned successfully "
            f"from '[bold]{config.parent}[/bold]' ({config.size_mb} MB).[/green]"
        )
    except SpecimenError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        raise typer.Exit(code=1)

