"""
YouTube Tools Main Entry Point
Provides both CLI and GUI interfaces.
"""

import sys
from .gui.main import main as gui_main
from .cli.main import main as cli_main


def main():
    """Main entry point - launches GUI by default, CLI if args provided"""
    if len(sys.argv) > 1:
        # Command line arguments provided, use CLI
        return cli_main()
    else:
        # No arguments, launch GUI
        return gui_main()