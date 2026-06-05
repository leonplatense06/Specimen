import typer
from rich.console import Console
from specimen.services.specimen_service import SpecimenService
from specimen.exceptions import SpecimenError

console = Console()

def enter_command(
    name: str = typer.Argument(..., help="Nombre del specimen al que entrar")
):
    """Entra a un specimen y abre una shell aislada."""
    try:
        console.print(f"[green]Entering specimen '{name.lower()}'...[/green]")
        SpecimenService.enter_specimen(name)
        console.print(f"[green]Exited specimen '{name.lower()}'.[/green]")
    except SpecimenError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Error inesperado:[/red] {e}")
        raise typer.Exit(code=1)
