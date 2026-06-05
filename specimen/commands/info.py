import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from specimen.services.specimen_service import SpecimenService
from specimen.exceptions import SpecimenError
from specimen.paths import specimen_dir, specimen_bin, specimen_tmp, specimen_home

console = Console()

def info_command(name: str = typer.Argument(..., help="Nombre del specimen")):
    """Muestra información detallada de un specimen."""
    try:
        config, state, tools, real_size = SpecimenService.get_specimen_info(name)
        
        info_table = Table.grid(padding=(0, 2))
        info_table.add_column("Property", style="bold cyan")
        info_table.add_column("Value")
        
        info_table.add_row("Nombre:", config.name)
        info_table.add_row("Tipo:", config.type)
        if config.parent:
            info_table.add_row("Padre:", config.parent)
            
        size_val = f"{real_size} MB / {config.size_mb} MB"
        if real_size > config.size_mb:
            size_val = f"[red]{real_size} MB[/red] / {config.size_mb} MB [bold red]⚠ Excedido[/bold red]"
        info_table.add_row("Tamaño (Usado/Límite):", size_val)
        
        info_table.add_row("Creado en:", config.created_at)
        info_table.add_row("Persistente:", "Sí" if config.persistent else "No")
        info_table.add_row("Activo:", "[bold green]Sí[/bold green]" if state.active else "No")
        
        # Rutas principales
        paths_table = Table.grid(padding=(0, 2))
        paths_table.add_column("Dir", style="bold yellow")
        paths_table.add_column("Path")
        paths_table.add_row("Raíz:", str(specimen_dir(config.name)))
        paths_table.add_row("Bin:", str(specimen_bin(config.name)))
        paths_table.add_row("Home:", str(specimen_home(config.name)))
        paths_table.add_row("Tmp:", str(specimen_tmp(config.name)))

        # Herramientas registradas
        tools_table = Table(box=None)
        tools_table.add_column("Nombre", style="bold green")
        tools_table.add_column("Binario", style="green")
        tools_table.add_column("Instalada el", style="dim")
        tools_table.add_column("Versión", style="magenta")
        
        if not tools.tools:
            tools_table.add_row("—", "Ninguna herramienta registrada", "—", "—")
        else:
            for t in tools.tools:
                version_str = t.version if t.version else "N/A"
                tools_table.add_row(t.name, t.filename, t.installed_at.split("T")[0], version_str)
                
        console.print(Panel(info_table, title=f"Metadata de [bold]{config.name}[/bold]", border_style="cyan"))
        console.print(Panel(paths_table, title="Rutas de Sistema", border_style="yellow"))
        console.print(Panel(tools_table, title="Herramientas Registradas", border_style="green"))
        
    except SpecimenError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Error inesperado:[/red] {e}")
        raise typer.Exit(code=1)
