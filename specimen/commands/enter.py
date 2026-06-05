import typer
from specimen.console import console
from specimen.services.specimen_service import SpecimenService
from specimen.exceptions import SpecimenError

def enter_command(
    name: str = typer.Argument(..., help="Name of the specimen to enter")
):
    """Enters a specimen and launches an isolated shell."""
    try:
        console.print(f"[green]Entering specimen '{name.lower()}'...[/green]")
        SpecimenService.enter_specimen(name)
        console.print(f"[green]Exited specimen '{name.lower()}'.[/green]")
    except SpecimenError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        raise typer.Exit(code=1)

