"""
Simple script to verify the generated IFC file properties
"""

import ifcopenshell
import config


def verify_ifc_file():
    """Verify the generated IFC file"""
    ifc_path = config.OUTPUT_IFC_FILE
    
    try:
        # Open the IFC file
        ifc_file = ifcopenshell.open(ifc_path)
        print(f"Successfully opened IFC file: {ifc_path}")
        
        # Get basic info
        print(f"IFC Schema: {ifc_file.schema}")
        
        # Get project info
        projects = ifc_file.by_type("IfcProject")
        if projects:
            project = projects[0]
            print(f"Project Name: {project.Name}")
        
        # Get units
        units = ifc_file.by_type("IfcUnitAssignment")
        if units:
            unit_assignment = units[0]
            print(f"Units assigned: {len(unit_assignment.Units)} units")
            for unit in unit_assignment.Units:
                if hasattr(unit, 'UnitType') and hasattr(unit, 'Name'):
                    print(f"  - {unit.UnitType}: {unit.Name}")
        
        # Get markers
        markers = ifc_file.by_type("IfcBuildingElementProxy")
        print(f"Found {len(markers)} markers")
        
        if markers:
            marker = markers[0]
            print(f"First marker name: {marker.Name}")
            
            # Check placement
            if marker.ObjectPlacement and marker.ObjectPlacement.RelativePlacement:
                location = marker.ObjectPlacement.RelativePlacement.Location
                if location and hasattr(location, 'Coordinates'):
                    coords = location.Coordinates
                    print(f"First marker coordinates: X={coords[0]:.2f}, Y={coords[1]:.2f}, Z={coords[2]:.2f} mm")
                    print(f"In meters: X={coords[0]/1000:.3f}, Y={coords[1]/1000:.3f}, Z={coords[2]/1000:.3f} m")
            
            # Check geometry
            if marker.Representation:
                representations = marker.Representation.Representations
                for rep in representations:
                    if rep.Items:
                        for item in rep.Items:
                            if hasattr(item, 'SweptArea') and hasattr(item.SweptArea, 'XDim'):
                                x_dim = item.SweptArea.XDim
                                y_dim = item.SweptArea.YDim
                                depth = item.Depth
                                print(f"Marker dimensions: {x_dim}mm x {y_dim}mm x {depth}mm")
                                print(f"In meters: {x_dim/1000}m x {y_dim/1000}m x {depth/1000}m")
        
        # Get properties
        property_sets = ifc_file.by_type("IfcPropertySet")
        print(f"Found {len(property_sets)} property sets")
        
        print("\nIFC file verification completed successfully!")
        
    except Exception as e:
        print(f"Error verifying IFC file: {str(e)}")


if __name__ == "__main__":
    verify_ifc_file()
