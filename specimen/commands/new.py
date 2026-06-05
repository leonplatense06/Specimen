import typer
from specimen.console import console
from specimen.services.specimen_service import SpecimenService
from specimen.exceptions import SpecimenError

def new_command(
    name: str = typer.Argument(..., help="Name of the specimen"),
    size: int = typer.Option(..., "--size", help="Size limit in MB for the specimen"),
):
    """Creates a new base specimen."""
    try:
        config = SpecimenService.create_specimen(name, size)
        console.print(f"[green]✔ Specimen '[bold]{config.name}[/bold]' created successfully ({config.size_mb} MB).[/green]")
    except SpecimenError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        raise typer.Exit(code=1)

