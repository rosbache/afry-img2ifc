"""
Main entry point for Image GPS to IFC Converter
"""

import tkinter as tk
import os
import sys

# Add src directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

from gui.main_window import ImageToIFCGUI


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


