import typer
from specimen.console import console
from specimen.services.specimen_service import SpecimenService
from specimen.services.runtime_service import RuntimeService
from specimen.paths import specimen_config_json
from specimen.storage.json_storage import load_json
from specimen.models import SpecimenConfig
from specimen.exceptions import SpecimenError

def quit_command(
    conserved: bool = typer.Option(
        False,
        "--conserv",
        "-c",
        help="Conserves the specimen on disk instead of destroying it upon exit"
    )
):
    """Exits the current active specimen and decides whether to conserve or destroy it."""
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
                if not typer.confirm(f"Are you sure you want to exit? The specimen '{active_name}' will be deleted."):
                    console.print("Operation cancelled.")
                    raise typer.Exit(code=1)

        SpecimenService.quit_specimen(conserved)
        was_conserved = conserved or is_persistent
        mode_str = "conserved" if was_conserved else "destroyed"
        console.print(f"[green]✔ Active specimen deactivated and {mode_str} successfully.[/green]")
    except SpecimenError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        raise typer.Exit(code=1)


