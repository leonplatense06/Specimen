import typer
from specimen.console import console
from rich.tree import Tree
from specimen.services.specimen_service import SpecimenService
from specimen.exceptions import SpecimenError

def tree_command():
    """Shows the hierarchy of parent-child relationships between specimens."""
    try:
        roots, adjacency = SpecimenService.get_hierarchy()
        if not roots:
            console.print("[yellow]No specimens found. Use 'spec new' to create one.[/yellow]")
            return
        
        def add_children(node: Tree, parent_name: str):
            for child in adjacency.get(parent_name, []):
                child_node = node.add(f"[cyan]{child}[/cyan]")
                add_children(child_node, child)

        root_tree = Tree("[bold magenta]Specimens[/bold magenta]")
        for root in roots:
            node = root_tree.add(f"[cyan]{root}[/cyan]")
            add_children(node, root)
            
        console.print(root_tree)
    except SpecimenError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        raise typer.Exit(code=1)

