import typer
from rich.console import Console
from specimen.services.specimen_service import SpecimenService
from specimen.exceptions import SpecimenError

console = Console()

def rm_command(
    name: str = typer.Argument(..., help="Nombre del specimen a borrar"),
    force: bool = typer.Option(False, "--force", "-f", help="Borra sin pedir confirmación"),
):
    """Borra un specimen manualmente."""
    try:
        # Normalizar para mostrar la confirmación correcta
        normalized_name = name.lower()
        
        # Primero validamos existencia y actividad antes de pedir confirmación para evitar confirmaciones inútiles
        # llamando a get_specimen_info que valida existencia.
        SpecimenService.get_specimen_info(normalized_name)
        
        if not force:
            confirm = typer.confirm(f"¿Eliminar specimen '{normalized_name}'?")
            if not confirm:
                console.print("[yellow]Operación cancelada.[/yellow]")
                raise typer.Abort()

        SpecimenService.remove_specimen(normalized_name)
        console.print(f"[green]✔ Specimen '[bold]{normalized_name}[/bold]' eliminado exitosamente.[/green]")
    except typer.Abort:
        raise
    except SpecimenError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Error inesperado:[/red] {e}")
        raise typer.Exit(code=1)
