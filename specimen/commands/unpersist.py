import typer
from specimen.console import console
from specimen.services.specimen_service import SpecimenService
from specimen.exceptions import SpecimenError

def unpersist_command(
    name: str = typer.Argument(..., help="Name of the specimen to remove persistence from")
):
    """Removes the persistence of a specimen."""
    try:
        SpecimenService.set_persistence(name, False)
        console.print(f"[green]✔ Specimen '[bold]{name.lower()}[/bold]' is now non-persistent.[/green]")
    except SpecimenError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        raise typer.Exit(code=1)
