from rich.console import Console, Group
from rich.markdown import Markdown
from .system import SystemAnalyzer
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich.text import Text
from rich import box

console = Console()

def show_interface(mode, args, analyzer: SystemAnalyzer | None = None):
    title = Text("🛡️ GEM Guard AI", style="bold cyan", justify="center")
    subtitle = Text(f"System Analysis Module [{mode.upper()}]", style="dim white", justify="center")

    grid = Table.grid(expand=False, padding=(0, 2))
    grid.add_column(justify="right", style="dim")
    grid.add_column(justify="left", style="bold white")
    
    grid.add_row("Model:", args.model)
    grid.add_row("Language:", args.lang)

    header_content = Group(
        title,
        subtitle,
        Text("\n"),
        Align.center(grid) 
    )

    header_panel = Panel(
        header_content,
        style="blue",
        box=box.ROUNDED,
        padding=(1, 2),
    )
    
    console.print(header_panel)
    console.print() 

    analyzer_status = Text("Synthesizing security insights...", justify="center")
    analyzer = analyzer or SystemAnalyzer()
    with console.status(analyzer_status, spinner="dots"):
        analysis = analyzer.perform_analysis(mode, args.model, args.lang)


    result_panel = Panel(
        Markdown(analysis.ai_markdown), 
        title="[bold green]Analysis Result[/bold green]", 
        border_style="grey50",
        box=box.ROUNDED,
        expand=True
    )
    
    console.print(result_panel)
    return analysis