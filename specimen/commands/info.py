import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from specimen.services.specimen_service import SpecimenService
from specimen.exceptions import SpecimenError
from specimen.paths import specimen_dir, specimen_bin, specimen_tmp, specimen_home

console = Console()

def info_command(name: str = typer.Argument(..., help="Name of the specimen")):
    """Shows detailed information about a specimen."""
    try:
        config, state, tools, real_size = SpecimenService.get_specimen_info(name)
        
        info_table = Table.grid(padding=(0, 2))
        info_table.add_column("Property", style="bold cyan")
        info_table.add_column("Value")
        
        info_table.add_row("Name:", config.name)
        info_table.add_row("Type:", config.type)
        if config.parent:
            info_table.add_row("Parent:", config.parent)
            
        size_val = f"{real_size} MB / {config.size_mb} MB"
        if real_size > config.size_mb:
            size_val = f"[red]{real_size} MB[/red] / {config.size_mb} MB [bold red]⚠ Exceeded[/bold red]"
        info_table.add_row("Size (Used/Limit):", size_val)
        
        info_table.add_row("Created at:", config.created_at)
        info_table.add_row("Persistent:", "Yes" if config.persistent else "No")
        info_table.add_row("Active:", "[bold green]Yes[/bold green]" if state.active else "No")
        
        # System Paths
        paths_table = Table.grid(padding=(0, 2))
        paths_table.add_column("Dir", style="bold yellow")
        paths_table.add_column("Path")
        paths_table.add_row("Root:", str(specimen_dir(config.name)))
        paths_table.add_row("Bin:", str(specimen_bin(config.name)))
        paths_table.add_row("Home:", str(specimen_home(config.name)))
        paths_table.add_row("Tmp:", str(specimen_tmp(config.name)))

        # Registered tools
        tools_table = Table(box=None)
        tools_table.add_column("Name", style="bold green")
        tools_table.add_column("Binary", style="green")
        tools_table.add_column("Installed at", style="dim")
        tools_table.add_column("Version", style="magenta")
        
        if not tools.tools:
            tools_table.add_row("—", "No tools registered", "—", "—")
        else:
            for t in tools.tools:
                version_str = t.version if t.version else "N/A"
                tools_table.add_row(t.name, t.filename, t.installed_at.split("T")[0], version_str)
                
        console.print(Panel(info_table, title=f"Metadata for [bold]{config.name}[/bold]", border_style="cyan"))
        console.print(Panel(paths_table, title="System Paths", border_style="yellow"))
        console.print(Panel(tools_table, title="Registered Tools", border_style="green"))
        
    except SpecimenError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        raise typer.Exit(code=1)
