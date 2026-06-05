import typer
from rich.console import Console
from rich.table import Table
from specimen.services.specimen_service import SpecimenService
from specimen.exceptions import SpecimenError

console = Console()

def list_command():
    """Lists all existing specimens."""
    try:
        specimens = SpecimenService.list_specimens()
        if not specimens:
            console.print("[yellow]No specimens found. Use 'spec new' to create one.[/yellow]")
            return

        table = Table(title="Existing Specimens")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Type", style="magenta")
        table.add_column("Parent", style="blue")
        table.add_column("Size (Used/Limit)", style="green")
        table.add_column("Active", style="bold green")
        table.add_column("Persistent", style="yellow")
        table.add_column("Created", style="dim")
# ... (rest stays the same)
        for config, state, real_size in specimens:
            active_str = "✔ Yes" if state.active else "No"
            active_style = "bold green" if state.active else "dim white"
            
            size_str = f"{real_size} / {config.size_mb} MB"
            if real_size > config.size_mb:
                size_str = f"[red]{real_size}[/red] / {config.size_mb} MB ⚠"

            persistent_str = "Yes" if config.persistent else "No"
            parent_str = config.parent if config.parent else "—"
            
            created_str = config.created_at.split("T")[0]

            table.add_row(
                config.name,
                config.type,
                parent_str,
                size_str,
                f"[{active_style}]{active_str}[/{active_style}]",
                persistent_str,
                created_str
            )

        console.print(table)
    except SpecimenError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        raise typer.Exit(code=1)

