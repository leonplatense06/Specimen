from rich.console import Console
from rich.theme import Theme

# Cyberpunk Palette
# - cyan: Neon Cyan (#00f0ff)
# - magenta: Neon Fuchsia/Pink (#ff007f)
# - green: Neon Green (#00ff66)
# - yellow: Neon Yellow/Lime (#ccff00)
# - red: Neon Red/Hot Pink (#ff3366)
# - blue: Neon Purple/Blue (#8b00ff)

cyberpunk_theme = Theme({
    "cyan": "#00f0ff",
    "magenta": "#ff007f",
    "green": "#00ff66",
    "yellow": "#ccff00",
    "red": "#ff3366",
    "blue": "#8b00ff",
    
    # Highlighting styles
    "repr.number": "#00f0ff",
    "repr.str": "#ccff00",
    "repr.bool_true": "#00ff66",
    "repr.bool_false": "#ff3366",
})

console = Console(theme=cyberpunk_theme)

# Override typer.rich_utils styles if typer is available
try:
    from typer import rich_utils
    rich_utils.STYLE_USAGE = "bold #ccff00"
    rich_utils.STYLE_USAGE_COMMAND = "bold #ff007f"
    rich_utils.STYLE_HELPTEXT = "#ffffff"
    rich_utils.STYLE_HELPTEXT_FIRST_LINE = "bold #ffffff"
    rich_utils.STYLE_METAVAR = "bold #ccff00"
    rich_utils.STYLE_OPTION = "bold #00f0ff"
    rich_utils.STYLE_SWITCH = "bold #00ff66"
    rich_utils.STYLE_NEGATIVE_OPTION = "bold #ff007f"
    rich_utils.STYLE_NEGATIVE_SWITCH = "bold #ff3366"
    rich_utils.STYLE_REQUIRED_SHORT = "bold #ff3366"
    rich_utils.STYLE_REQUIRED_LONG = "bold #ff3366"
    rich_utils.STYLE_COMMANDS_TABLE_FIRST_COLUMN = "bold #00f0ff"
    rich_utils.STYLE_OPTIONS_PANEL_BORDER = "#8b00ff"
    rich_utils.STYLE_COMMANDS_PANEL_BORDER = "#8b00ff"
    rich_utils.STYLE_ERRORS_PANEL_BORDER = "bold #ff3366"
except ImportError:
    pass
