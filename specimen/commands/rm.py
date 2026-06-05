import typer
from specimen.console import console
from specimen.services.specimen_service import SpecimenService
from specimen.exceptions import SpecimenError

def rm_command(
    name: str = typer.Argument(..., help="Name of the specimen to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Delete without asking for confirmation"),
):
    """Deletes a specimen manually."""
    try:
        # Normalize to show the correct confirmation
        normalized_name = name.lower()
        
        # Validate existence and active status before asking for confirmation to avoid useless prompts
        # calling get_specimen_info which validates existence.
        SpecimenService.get_specimen_info(normalized_name)
        
        if not force:
            confirm = typer.confirm(f"Delete specimen '{normalized_name}'?")
            if not confirm:
                console.print("[yellow]Operation cancelled.[/yellow]")
                raise typer.Abort()

        SpecimenService.remove_specimen(normalized_name)
        console.print(f"[green]✔ Specimen '[bold]{normalized_name}[/bold]' deleted successfully.[/green]")
    except typer.Abort:
        raise
    except SpecimenError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        raise typer.Exit(code=1)

