import typer
from rich.console import Console
from specimen.services.specimen_service import SpecimenService
from specimen.services.runtime_service import RuntimeService
from specimen.paths import specimen_config_json
from specimen.storage.json_storage import load_json
from specimen.models import SpecimenConfig
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
        active_name = RuntimeService.get_active_specimen()
        is_persistent = False
        if active_name:
            try:
                config = load_json(specimen_config_json(active_name), SpecimenConfig)
                is_persistent = config.persistent
            except Exception:
                pass

        if not conserved and not is_persistent:
            if active_name:
                if not typer.confirm(f"¿Estás seguro de que quieres salir? Se eliminará el specimen '{active_name}'."):
                    console.print("Operación cancelada.")
                    raise typer.Exit(code=1)

        SpecimenService.quit_specimen(conserved)
        was_conserved = conserved or is_persistent
        mode_str = "conservado" if was_conserved else "destruido"
        console.print(f"[green]✔ Specimen activo desactivado y {mode_str} exitosamente.[/green]")
    except SpecimenError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Error inesperado:[/red] {e}")
        raise typer.Exit(code=1)

