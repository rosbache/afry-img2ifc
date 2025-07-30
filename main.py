"""
Main entry point for Image GPS to IFC Converter
"""

import tkinter as tk
import os
import sys

# Add parent directory to path for more reliable imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Use explicit import from src package
try:
    from src.gui.main_window import ImageToIFCGUI
except ImportError:
    # Fallback for when running from PyInstaller bundle
    try:
        # Try direct import (may work in PyInstaller context)
        from gui.main_window import ImageToIFCGUI
    except ImportError:
        print("Error: Could not import GUI module. Make sure you're running from the correct directory.")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)


def main():
    """Main function to run the GUI application"""
    try:
        root = tk.Tk()
        app = ImageToIFCGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()


