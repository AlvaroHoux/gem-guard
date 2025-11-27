#!/usr/bin/env python3

from .system import SystemAnalyzer
from rich.console import Console
from .cli import show_interface
from rich.align import Align
from rich.panel import Panel
from .app import GemGuardApp
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
    parser.add_argument("--lang", type=str, choices=["pt-br", "en"], default="en", help="Response language (pt-br or en)")

    args = parser.parse_args()

    mode = None
    if args.network: mode = "network"
    elif args.processes: mode = "processes"
    elif args.packages: mode = "packages"
    elif args.full: mode = "full"

    if mode:
        if args.quiet:
            analyzer = SystemAnalyzer()
            result_raw = analyzer.analyze(mode, args.model, args.lang)  
            print(result_raw)
        else:
            show_interface(mode, args) 
    elif args.gui or len(sys.argv) == 1:
        runGui()
    else:
        parser.print_help()

if __name__ == "__main__":
    run()
        
if __name__ == "__main__":
    runGui()