import typer
from rich.console import Console
from specimen.services.specimen_service import SpecimenService
from specimen.exceptions import SpecimenError

console = Console()

def quit_command(
    conserved: bool = typer.Option(
        False,
        "--conserv",
        "-c",
        help="Conserva el specimen en disco en lugar de destruirlo al salir"
    )
):
    """Sale del specimen activo actual y decide si lo conserva o destruye."""
    try:
        SpecimenService.quit_specimen(conserved)
        mode_str = "conservado" if conserved else "destruido"
        console.print(f"[green]✔ Specimen activo desactivado y {mode_str} exitosamente.[/green]")
    except SpecimenError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Error inesperado:[/red] {e}")
        raise typer.Exit(code=1)
