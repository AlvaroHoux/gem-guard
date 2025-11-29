#!/usr/bin/env python3

from .system import SystemAnalyzer
from .reporting import ExportError, export_analysis
from rich.console import Console
from .cli import show_interface
from .app import GemGuardApp
from pathlib import Path
import argparse
import sys

def runGui():
    app = GemGuardApp()
    app.run()

def run():
    parser = argparse.ArgumentParser(
        prog="gem-guard",
        description="Linux security analysis tool utilizing Gemini AI"
    )

    action_group = parser.add_mutually_exclusive_group()
    
    action_group.add_argument("-g", "--gui", action="store_true", help="Launch the Terminal User Interface (TUI)")
    action_group.add_argument("-n", "--network", action="store_true", help="Analyze suspicious network connections")
    action_group.add_argument("-p", "--processes", action="store_true", help="Analyze suspicious processes")
    action_group.add_argument("-k", "--packages", action="store_true", help="Analyze recently installed packages")
    action_group.add_argument("-f", "--full", action="store_true", help="Generate a full security report")

    parser.add_argument("--quiet", action="store_true",help="Output only the raw AI response (no formatting)")

    parser.add_argument("--model", type=str, default="gemini-2.0-flash", help="Set the Gemini model (e.g., gemini-2.0-flash)")
    parser.add_argument(
        "--lang",
        type=str,
        choices=["pt-br", "en", "zh-cn"],
        default="en",
        help="Response language (pt-br, en, zh-cn)",
    )
    parser.add_argument(
        "--export",
        choices=["html", "pdf"],
        action="append",
        help="Export the analysis to HTML and/or PDF files. Specify multiple times for each format.",
    )
    parser.add_argument(
        "--export-dir",
        type=Path,
        default=Path.cwd() / "reports",
        help="Directory where exported reports will be saved (default: ./reports)",
    )
    parser.add_argument(
        "--export-name",
        type=str,
        help="Custom base filename (without extension) for exported reports.",
    )

    args = parser.parse_args()

    mode = None
    if args.network: mode = "network"
    elif args.processes: mode = "processes"
    elif args.packages: mode = "packages"
    elif args.full: mode = "full"

    if mode:
        analyzer = SystemAnalyzer()
        analysis = None

        if args.quiet:
            analysis = analyzer.perform_analysis(mode, args.model, args.lang)
            print(analysis.ai_markdown)
        else:
            analysis = show_interface(mode, args, analyzer)

        if args.export and analysis:
            console = Console()
            for fmt in args.export:
                try:
                    path = export_analysis(
                        analysis,
                        fmt,
                        directory=args.export_dir,
                        filename=args.export_name,
                    )
                    console.print(f"[green]\u2713 Saved {fmt.upper()} report -> {path}")
                except ExportError as exc:
                    console.print(f"[red]Export failed ({fmt}): {exc}")
    elif args.gui or len(sys.argv) == 1:
        runGui()
    else:
        parser.print_help()

if __name__ == "__main__":
    run()
        
if __name__ == "__main__":
    runGui()