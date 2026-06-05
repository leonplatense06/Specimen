import typer
from rich.console import Console
from specimen.services.specimen_service import SpecimenService
from specimen.exceptions import SpecimenError

console = Console()

def persist_command(
    name: str = typer.Argument(..., help="Name of the specimen to mark as persistent"),
    unset: bool = typer.Option(
        False,
        "--unset",
        "-u",
        help="Removes persistence from the specimen (it will be deleted on exit unless -c is specified)"
    )
):
    """Sets or removes the persistence of a specimen."""
    try:
        persistent = not unset
        SpecimenService.set_persistence(name, persistent)
        
        status_str = "persistent" if persistent else "non-persistent"
        console.print(f"[green]✔ Specimen '[bold]{name.lower()}[/bold]' is now {status_str}.[/green]")
    except SpecimenError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        raise typer.Exit(code=1)

