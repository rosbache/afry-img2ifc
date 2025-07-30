"""
Main GUI window for Image GPS to IFC Converter
Two-step process: Extract images to JSON, then generate IFC
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import json
import threading
from datetime import datetime
import pyproj
import platform
import json


# Add parent directories to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(src_dir)
sys.path.insert(0, src_dir)
sys.path.insert(0, root_dir)

from core.image_processor import extract_images_to_json
from core.ifc_exporter import IFCExporter

try:
    
    # Use IFCExporter from ifc_exporter instead of ifc_generator
    
    def generate_ifc_from_json(json_path, output_path, project_settings_path):
        # Load processed images
        
        with open(json_path, 'r', encoding='utf-8') as f:
            processed_images = json.load(f)
        # Load project settings
        with open(project_settings_path, 'r', encoding='utf-8') as f:
            project_settings = json.load(f)
        exporter = IFCExporter()
        exporter.set_project_settings(project_settings)
        exporter.export_markers(processed_images, output_path)
        return True
    from utils import config
    
except ImportError:
    # Fallback: import the real implementation directly if not found in sys.path
    import importlib.util
    import_path = os.path.join(src_dir, 'core', 'image_processor.py')
    spec = importlib.util.spec_from_file_location('image_processor', import_path)
    image_processor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(image_processor)
    extract_images_to_json = image_processor.extract_images_to_json
    
    def generate_ifc_from_json(json_path, output_path, project_settings_path):
        """Placeholder function"""
        with open(output_path, 'w') as f:
            f.write("# Placeholder IFC file\n")
        return True
    
    class Config:
        TARGET_CRS = "EPSG:5110"
    config = Config()


class ImageToIFCGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Image GPS to IFC Converter")
        self.root.geometry("800x600")
        
        # Variables
        self.step1_folder_path = tk.StringVar()
        self.step1_epsg_code = tk.StringVar(value="5110")
        self.step1_json_output = tk.StringVar()
        
        self.step2_json_path = tk.StringVar()
        self.step2_project_settings_path = tk.StringVar()
        self.step2_output_folder = tk.StringVar()
        self.step2_ifc_filename = tk.StringVar(value="markers.ifc")
        self.step2_ifc_schema = tk.StringVar(value="IFC2x3")
        
        self.created_json_from_step1 = None
        
        self.setup_gui()
    
    def setup_gui(self):
        """Setup the GUI layout"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Setup menu bar
        self.setup_menu()
        
        # Title
        title_label = ttk.Label(main_frame, text="Image GPS to IFC Converter", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Step 1 Frame
        self.setup_step1_frame(main_frame, row=1)
        
        # Separator
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)
        
        # Step 2 Frame
        self.setup_step2_frame(main_frame, row=3)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(20, 0))
    
    def setup_step1_frame(self, parent, row):
        """Setup Step 1 GUI components"""
        # Step 1 Label
        step1_label = ttk.Label(parent, text="1", font=('Arial', 14, 'bold'))
        step1_label.grid(row=row, column=0, sticky=tk.W, padx=(0, 10))
        
        step1_frame = ttk.LabelFrame(parent, text="Extract Images to JSON", padding="10")
        step1_frame.grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        step1_frame.columnconfigure(1, weight=1)
        
        # Image folder path
        ttk.Label(step1_frame, text="Image folder path:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(step1_frame, textvariable=self.step1_folder_path, width=50).grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=2)
        ttk.Button(step1_frame, text="Select folder", 
                  command=self.select_step1_folder).grid(row=0, column=2, padx=(5, 0), pady=2)
        
        # Output coordinate system (EPSG Code)
        ttk.Label(step1_frame, text="Output coordinate system (EPSG Code):").grid(
            row=1, column=0, sticky=tk.W, pady=2)
        epsg_frame = ttk.Frame(step1_frame)
        epsg_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=2)
        ttk.Entry(epsg_frame, textvariable=self.step1_epsg_code, width=10).pack(side=tk.LEFT)
        ttk.Button(epsg_frame, text="Check", 
                  command=self.check_epsg_code).pack(side=tk.LEFT, padx=(5, 0))
        self.epsg_status_label = ttk.Label(epsg_frame, text="", foreground="green")
        self.epsg_status_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Bind EPSG validation
        self.step1_epsg_code.trace('w', self.validate_epsg_code)
        
        # Generate JSON button
        ttk.Button(step1_frame, text="Generate json", 
                  command=self.generate_json).grid(row=2, column=2, padx=(5, 0), pady=10)
    
    def setup_step2_frame(self, parent, row):
        """Setup Step 2 GUI components"""
        # Step 2 Label
        step2_label = ttk.Label(parent, text="2", font=('Arial', 14, 'bold'))
        step2_label.grid(row=row, column=0, sticky=tk.W, padx=(0, 10))
        
        step2_frame = ttk.LabelFrame(parent, text="Generate IFC from JSON", padding="10")
        step2_frame.grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        step2_frame.columnconfigure(1, weight=1)
        
        # JSON image processed images
        ttk.Label(step2_frame, text="Json image processed images:").grid(
            row=0, column=0, sticky=tk.W, pady=2)
        json_frame = ttk.Frame(step2_frame)
        json_frame.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        json_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(json_frame, textvariable=self.step2_json_path).grid(
            row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(json_frame, text="Select file", 
                  command=self.select_step2_json).grid(row=0, column=1)
        ttk.Label(json_frame, text="— Use json from step 1", 
                 foreground="gray").grid(row=0, column=2, padx=(10, 0))
        
        # Project settings json file
        ttk.Label(step2_frame, text="Project settings json file:").grid(
            row=1, column=0, sticky=tk.W, pady=2)
        project_frame = ttk.Frame(step2_frame)
        project_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        project_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(project_frame, textvariable=self.step2_project_settings_path).grid(
            row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(project_frame, text="Select file", 
                  command=self.select_project_settings).grid(row=0, column=1)
        ttk.Button(project_frame, text="Generate template file", 
                  command=self.generate_template_file).grid(row=0, column=2, padx=(5, 0))
        
        # Output folder for ifc file
        ttk.Label(step2_frame, text="Output folder for ifc file:").grid(
            row=2, column=0, sticky=tk.W, pady=2)
        output_frame = ttk.Frame(step2_frame)
        output_frame.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        output_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(output_frame, textvariable=self.step2_output_folder).grid(
            row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(output_frame, text="Select folder", 
                  command=self.select_output_folder).grid(row=0, column=1)
        
        # IFC filename
        ttk.Label(step2_frame, text="IFC filename:").grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Entry(step2_frame, textvariable=self.step2_ifc_filename).grid(
            row=3, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=2)
        
        # IFC Schema version
        ttk.Label(step2_frame, text="IFC Schema version:").grid(row=4, column=0, sticky=tk.W, pady=2)
        schema_frame = ttk.Frame(step2_frame)
        schema_frame.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=2)
        ttk.Radiobutton(schema_frame, text="IFC2x3", variable=self.step2_ifc_schema, 
                       value="IFC2x3").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(schema_frame, text="IFC4.3", variable=self.step2_ifc_schema, 
                       value="IFC4X3").pack(side=tk.LEFT)
        
        # Generate IFC button
        ttk.Button(step2_frame, text="Generate IFC", 
                  command=self.generate_ifc).grid(row=5, column=2, padx=(5, 0), pady=10)
    
    def validate_epsg_code(self, *args):
        """Validate EPSG code"""
        epsg_code = self.step1_epsg_code.get().strip()
        
        if not epsg_code:
            self.epsg_status_label.config(text="", foreground="gray")
            return
        
        try:
            # Try to create a CRS with the given EPSG code
            crs = pyproj.CRS.from_epsg(int(epsg_code))
            self.epsg_status_label.config(text="✓ Valid EPSG code", foreground="green")
        except Exception:
            self.epsg_status_label.config(text="✗ Invalid EPSG code", foreground="red")
    
    def check_epsg_code(self):
        """Check EPSG code and show detailed information"""
        epsg_code = self.step1_epsg_code.get().strip()
        
        if not epsg_code:
            messagebox.showerror("Error", "Please enter an EPSG code")
            return
        
        try:
            # Try to create a CRS with the given EPSG code
            crs = pyproj.CRS.from_epsg(int(epsg_code))
            
            # Get CRS information
            crs_name = crs.name
            crs_type = crs.type_name
            area_of_use = crs.area_of_use
            
            info_text = f"EPSG:{epsg_code} - {crs_name}\n\n"
            info_text += f"Type: {crs_type}\n\n"
            
            if area_of_use:
                info_text += f"Area of use: {area_of_use.name}\n"
                info_text += f"Bounds: West {area_of_use.west:.2f}°, "
                info_text += f"East {area_of_use.east:.2f}°, "
                info_text += f"South {area_of_use.south:.2f}°, "
                info_text += f"North {area_of_use.north:.2f}°"
            
            messagebox.showinfo("EPSG Code Information", info_text)
            
        except ValueError:
            messagebox.showerror("Invalid EPSG Code", "Please enter a valid numeric EPSG code")
        except Exception as e:
            messagebox.showerror("Invalid EPSG Code", 
                               f"EPSG:{epsg_code} is not a valid EPSG code.\n\n"
                               f"Error: {str(e)}")
    
    def select_step1_folder(self):
        """Select folder for step 1"""
        folder = filedialog.askdirectory(title="Select image folder")
        if folder:
            self.step1_folder_path.set(folder)
            # Set default JSON output path
            json_output = os.path.join(folder, "extracted_images.json")
            self.step1_json_output.set(json_output)
    
    def select_step2_json(self):
        """Select JSON file for step 2"""
        json_file = filedialog.askopenfilename(
            title="Select JSON file",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if json_file:
            self.step2_json_path.set(json_file)
    
    def select_project_settings(self):
        """Select project settings JSON file"""
        json_file = filedialog.askopenfilename(
            title="Select project settings JSON file",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if json_file:
            self.step2_project_settings_path.set(json_file)
    
    def select_output_folder(self):
        """Select output folder for IFC file"""
        folder = filedialog.askdirectory(title="Select output folder for IFC file")
        if folder:
            self.step2_output_folder.set(folder)
    
    def generate_template_file(self):
        """Generate project settings template file"""
        template_file = filedialog.asksaveasfilename(
            title="Save project settings template",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile="project_settings_template.json"
        )
        
        if template_file:
            try:
                # Create template based on existing project_settings.json
                template = {
                    "project_settings": {
                        "ifc_project_name": "PROJECT_NAME",
                        "ifc_project_description": "Project Description",
                        "ifc_site_name": "Site Name",
                        "ifc_site_description": "Site Description",
                        "ifc_building": "Building Name",
                        "ifc_building_description": "Building Description",
                        "ifc_building_storey": "Storey Name",
                        "ifc_building_storey_description": "Storey Description"
                    },
                    "owner_information": {
                        "person_given_name": "First Name",
                        "person_family_name": "Last Name",
                        "organization_name": "Organization Name"
                    }
                }
                
                with open(template_file, 'w', encoding='utf-8') as f:
                    json.dump(template, f, indent=4, ensure_ascii=False)
                
                messagebox.showinfo("Template Created", 
                                  f"Project settings template created:\n{template_file}\n\n"
                                  "Please edit this file with your project details.")
                
                self.step2_project_settings_path.set(template_file)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create template file:\n{str(e)}")
    
    def generate_json(self):
        """Generate JSON from images in step 1"""
        if not self.step1_folder_path.get():
            messagebox.showerror("Error", "Please select an image folder")
            return
        
        if not self.step1_epsg_code.get() or "Invalid" in self.epsg_status_label.cget("text"):
            messagebox.showerror("Error", "Please enter a valid EPSG code")
            return
        
        # Ask for output file
        json_file = filedialog.asksaveasfilename(
            title="Save extracted images JSON",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile="extracted_images.json"
        )
        
        if not json_file:
            return
        
        def run_extraction():
            try:
                self.status_var.set("Extracting GPS data from images...")
                self.root.update()
                
                # Update config with user's EPSG code
                config.TARGET_CRS = f"EPSG:{self.step1_epsg_code.get()}"
                
                result = extract_images_to_json(
                    input_folder=self.step1_folder_path.get(),
                    output_file=json_file,
                    include_no_gps=False,
                    verbose=False
                )
                
                if result:
                    self.created_json_from_step1 = json_file
                    self.step2_json_path.set(json_file)  # Auto-populate step 2
                    self.status_var.set(f"JSON created successfully: {json_file}")
                    messagebox.showinfo("Success", 
                                      f"Successfully extracted GPS data from {len(result)} images.\n"
                                      f"JSON file saved: {json_file}")
                else:
                    self.status_var.set("Failed to extract GPS data")
                    messagebox.showerror("Error", "Failed to extract GPS data from images")
                    
            except Exception as e:
                self.status_var.set("Error during extraction")
                messagebox.showerror("Error", f"Error during extraction:\n{str(e)}")
        
        # Run in thread to prevent GUI freezing
        threading.Thread(target=run_extraction, daemon=True).start()
    
    def generate_ifc(self):
        """Generate IFC file in step 2"""
        # Validate inputs
        json_path = self.step2_json_path.get()
        if not json_path:
            messagebox.showerror("Error", "Please select a JSON file")
            return
        
        if not os.path.exists(json_path):
            messagebox.showerror("Error", f"JSON file not found: {json_path}")
            return
        
        project_settings_path = self.step2_project_settings_path.get()
        if not project_settings_path:
            messagebox.showerror("Error", "Please select a project settings file")
            return
        
        if not os.path.exists(project_settings_path):
            messagebox.showerror("Error", f"Project settings file not found: {project_settings_path}")
            return
        
        output_folder = self.step2_output_folder.get()
        if not output_folder:
            messagebox.showerror("Error", "Please select an output folder")
            return
        
        ifc_filename = self.step2_ifc_filename.get().strip()
        if not ifc_filename:
            messagebox.showerror("Error", "Please enter an IFC filename")
            return
        
        if not ifc_filename.endswith('.ifc'):
            ifc_filename += '.ifc'
        
        output_path = os.path.join(output_folder, ifc_filename)
        
        def run_ifc_generation():
            try:
                self.status_var.set("Generating IFC file...")
                self.root.update()
                
                # Import IFCExporter here to avoid circular imports
                from src.core.ifc_exporter import IFCExporter
                
                # Create the exporter
                exporter = IFCExporter()
                
                # Get selected IFC schema
                ifc_schema = self.step2_ifc_schema.get()
                
                # Use the export_markers_from_json method to handle everything
                exporter.export_markers_from_json(
                    json_path, 
                    output_path, 
                    project_settings_path,
                    schema=ifc_schema
                )
                
                schema_version = "IFC2x3" if ifc_schema == "IFC2x3" else "IFC4.3"
                self.status_var.set(f"{schema_version} file created successfully: {output_path}")
                messagebox.showinfo("Success", f"{schema_version} file created successfully:\n{output_path}")
            except Exception as e:
                self.status_var.set("Error during IFC generation")
                messagebox.showerror("Error", f"Error during IFC generation:\n{str(e)}")
                import traceback
                traceback.print_exc()

        # Run in thread to prevent GUI freezing
        threading.Thread(target=run_ifc_generation, daemon=True).start()
    
    def setup_menu(self):
        """Setup the application menu bar"""
        # Create menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about_dialog)
    
    def show_about_dialog(self):
        """Show the About dialog with program information"""
        about_window = tk.Toplevel(self.root)
        about_window.title("About Image GPS to IFC Converter")
        about_window.geometry("600x700")
        about_window.resizable(False, False)
        
        # Center the window
        about_window.transient(self.root)
        about_window.grab_set()
        
        # Main frame with padding
        main_frame = ttk.Frame(about_window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        about_window.columnconfigure(0, weight=1)
        about_window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Image GPS to IFC Converter", 
                               font=("TkDefaultFont", 16, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Version info
        version_label = ttk.Label(main_frame, text="Version 1.0", 
                                 font=("TkDefaultFont", 12))
        version_label.grid(row=1, column=0, pady=(0, 20))
        
        # Description
        description = """A professional tool for extracting GPS coordinates from images and converting them to IFC format.
Supports Norwegian coordinate systems and provides accurate spatial positioning for BIM workflows."""
        
        desc_label = ttk.Label(main_frame, text=description, 
                              font=("TkDefaultFont", 10), justify=tk.CENTER, wraplength=500)
        desc_label.grid(row=2, column=0, pady=(0, 20))
        
        # Create notebook for tabbed information
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        main_frame.rowconfigure(3, weight=1)
        
        # System Information Tab
        sys_frame = ttk.Frame(notebook, padding="10")
        notebook.add(sys_frame, text="System Information")
        
        sys_info = self.get_system_info()
        sys_text = tk.Text(sys_frame, wrap=tk.WORD, height=10, width=60, 
                          font=("Courier", 9), state=tk.DISABLED)
        sys_scrollbar = ttk.Scrollbar(sys_frame, orient=tk.VERTICAL, command=sys_text.yview)
        sys_text.configure(yscrollcommand=sys_scrollbar.set)
        
        sys_text.config(state=tk.NORMAL)
        sys_text.insert(tk.END, sys_info)
        sys_text.config(state=tk.DISABLED)
        
        sys_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        sys_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        sys_frame.columnconfigure(0, weight=1)
        sys_frame.rowconfigure(0, weight=1)
        
        # Dependencies Tab
        deps_frame = ttk.Frame(notebook, padding="10")
        notebook.add(deps_frame, text="Dependencies")
        
        deps_info = self.get_dependencies_info()
        deps_text = tk.Text(deps_frame, wrap=tk.WORD, height=10, width=60, 
                           font=("Courier", 9), state=tk.DISABLED)
        deps_scrollbar = ttk.Scrollbar(deps_frame, orient=tk.VERTICAL, command=deps_text.yview)
        deps_text.configure(yscrollcommand=deps_scrollbar.set)
        
        deps_text.config(state=tk.NORMAL)
        deps_text.insert(tk.END, deps_info)
        deps_text.config(state=tk.DISABLED)
        
        deps_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        deps_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        deps_frame.columnconfigure(0, weight=1)
        deps_frame.rowconfigure(0, weight=1)
        
        # Contact Information Tab
        contact_frame = ttk.Frame(notebook, padding="10")
        notebook.add(contact_frame, text="Contact & License")
        
        contact_info = self.get_contact_info()
        contact_text = tk.Text(contact_frame, wrap=tk.WORD, height=10, width=60, 
                              font=("TkDefaultFont", 10), state=tk.DISABLED)
        contact_scrollbar = ttk.Scrollbar(contact_frame, orient=tk.VERTICAL, command=contact_text.yview)
        contact_text.configure(yscrollcommand=contact_scrollbar.set)
        
        contact_text.config(state=tk.NORMAL)
        contact_text.insert(tk.END, contact_info)
        contact_text.config(state=tk.DISABLED)
        
        contact_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        contact_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        contact_frame.columnconfigure(0, weight=1)
        contact_frame.rowconfigure(0, weight=1)
        
        # Close button
        close_button = ttk.Button(main_frame, text="Close", command=about_window.destroy)
        close_button.grid(row=4, column=0, pady=(10, 0))
        
        # Center the window on parent
        about_window.update_idletasks()
        x = (about_window.winfo_screenwidth() // 2) - (about_window.winfo_width() // 2)
        y = (about_window.winfo_screenheight() // 2) - (about_window.winfo_height() // 2)
        about_window.geometry(f"+{x}+{y}")
    
    def get_system_info(self):
        """Get system and platform information"""
        info_lines = []
        
        # Python information
        info_lines.append("PYTHON INFORMATION")
        info_lines.append("=" * 50)
        info_lines.append(f"Python Version: {sys.version}")
        info_lines.append(f"Python Executable: {sys.executable}")
        info_lines.append(f"Python Path: {sys.path[0]}")
        info_lines.append("")
        
        # Platform information
        info_lines.append("PLATFORM INFORMATION")
        info_lines.append("=" * 50)
        info_lines.append(f"Operating System: {platform.system()}")
        info_lines.append(f"OS Release: {platform.release()}")
        info_lines.append(f"OS Version: {platform.version()}")
        info_lines.append(f"Machine Type: {platform.machine()}")
        info_lines.append(f"Processor: {platform.processor()}")
        info_lines.append(f"Architecture: {platform.architecture()[0]}")
        info_lines.append(f"Node Name: {platform.node()}")
        info_lines.append("")
        
        # Tkinter information
        info_lines.append("GUI FRAMEWORK")
        info_lines.append("=" * 50)
        info_lines.append(f"Tkinter Version: {tk.TkVersion}")
        info_lines.append(f"Tcl Version: {tk.TclVersion}")
        info_lines.append("")
        
        return "\n".join(info_lines)
    
    def get_dependencies_info(self):
        """Get information about external dependencies"""
        info_lines = []
        
        info_lines.append("EXTERNAL LIBRARIES")
        info_lines.append("=" * 50)
        
        # Check pyproj
        try:
            import pyproj
            info_lines.append(f"✓ pyproj: {getattr(pyproj, '__version__', 'Unknown version')}")
            info_lines.append("  - Cartographic projections and coordinate transformations")
            info_lines.append("  - Website: https://pyproj4.github.io/pyproj/")
        except ImportError:
            info_lines.append("✗ pyproj: Not installed")
        
        info_lines.append("")
        
        # Check PIL/Pillow
        try:
            from PIL import Image
            info_lines.append(f"✓ Pillow (PIL): {getattr(Image, '__version__', 'Unknown version')}")
            info_lines.append("  - Image processing and EXIF data extraction")
            info_lines.append("  - Website: https://pillow.readthedocs.io/")
        except ImportError:
            info_lines.append("✗ Pillow (PIL): Not installed")
        
        info_lines.append("")
        
        # Check ifcopenshell (if used)
        try:
            import ifcopenshell
            info_lines.append(f"✓ ifcopenshell: {getattr(ifcopenshell, '__version__', 'Unknown version')}")
            info_lines.append("  - Industry Foundation Classes (IFC) file processing")
            info_lines.append("  - Website: https://ifcopenshell.org/")
        except ImportError:
            info_lines.append("✗ ifcopenshell: Not installed")
        
        info_lines.append("")
        
        # Standard library modules used
        info_lines.append("STANDARD LIBRARY MODULES")
        info_lines.append("=" * 50)
        
        standard_modules = [
            ("json", "JSON data processing"),
            ("os", "Operating system interface"),
            ("sys", "System-specific parameters"),
            ("threading", "Threading support"),
            ("datetime", "Date and time handling"),
            ("platform", "Platform identification"),
            ("tkinter", "GUI framework (Tcl/Tk)"),
        ]
        
        for module_name, description in standard_modules:
            try:
                module = __import__(module_name)
                version = getattr(module, '__version__', 'Built-in')
                info_lines.append(f"✓ {module_name}: {version}")
                info_lines.append(f"  - {description}")
            except ImportError:
                info_lines.append(f"✗ {module_name}: Not available")
        
        info_lines.append("")
        
        # Application modules
        info_lines.append("APPLICATION MODULES")
        info_lines.append("=" * 50)
        info_lines.append("✓ extract_images_to_json: GPS coordinate extraction from images")
        info_lines.append("✓ json_to_ifc: IFC file generation from JSON data")
        info_lines.append("✓ config: Application configuration and settings")
        
        return "\n".join(info_lines)
    
    def get_contact_info(self):
        """Get contact and license information"""
        info = """DEVELOPMENT INFORMATION

Organization: AFRY
Project: Image GPS to IFC Converter
Purpose: Converting image GPS coordinates to IFC spatial markers for BIM workflows

FEATURES

• Two-step conversion process:
  1. Extract GPS coordinates from image EXIF data
  2. Generate IFC files with spatial positioning markers

• Coordinate system transformation using EPSG codes
• Support for Norwegian coordinate systems (e.g., EPSG:5110)
• EPSG code validation and information lookup
• JSON intermediate format for data review and editing
• Configurable project settings templates
• Threading for non-blocking operations
• Progress tracking and status updates

SUPPORTED FORMATS

• Input: JPEG, TIFF, and other images with GPS EXIF data
• Coordinate Systems: Any EPSG-defined coordinate reference system
• Output: IFC 2x3 or IFC 4 files with IfcSite spatial positioning
• Settings: JSON configuration files

COORDINATE SYSTEMS

This application supports coordinate transformation between:
• WGS84 Geographic (EPSG:4326) - GPS coordinates
• Norwegian coordinate systems (EPSG:5110, etc.)
• UTM zones and other projected coordinate systems
• Custom EPSG-defined coordinate reference systems

WORKFLOW

1. Select folder containing images with GPS coordinates
2. Choose target coordinate system (EPSG code)
3. Extract GPS data to JSON format
4. Configure project settings (site, building information)
5. Generate IFC file with positioned markers

LICENSE

This software is developed for internal use at AFRY.
All rights reserved.

CONTACT INFORMATION

For technical support or questions about this application,
please contact your local AFRY BIM coordinator or the
development team through official AFRY channels.

DISCLAIMER

This software is provided "as is" without warranty of any kind.
Users are responsible for validating coordinate transformations
and ensuring compliance with applicable standards and regulations."""
        
        return info

def main():
    """Main function to run the GUI"""
    root = tk.Tk()
    app = ImageToIFCGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()