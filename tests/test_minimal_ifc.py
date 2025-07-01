#!/usr/bin/env python3
"""
Test script to create a minimal IFC file for debugging
"""

import ifcopenshell
import ifcopenshell.guid

def create_minimal_ifc():
    """Create a minimal IFC file for testing"""
    
    # Create IFC file
    ifc_file = ifcopenshell.file()
    
    # Create project
    project = ifc_file.createIfcProject(
        GlobalId=ifcopenshell.guid.new(),
        OwnerHistory=None,
        Name="Test Project",
        Description=None,
        ObjectType=None,
        LongName=None,
        Phase=None,
        RepresentationContexts=[],
        UnitsInContext=None
    )
    
    print("Minimal IFC file created successfully")
    
    # Write to file
    output_path = "C:\\Users\\HTO334\\OneDrive - AFRY\\Pictures\\e105-360 images\\test\\output\\test_minimal.ifc"
    ifc_file.write(output_path)
    print(f"Written to: {output_path}")
    
if __name__ == "__main__":
    create_minimal_ifc()
