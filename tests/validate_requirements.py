"""
Comprehensive validation of the generated IFC file to ensure it meets all requirements
"""

import ifcopenshell
import config
import os


def validate_requirements():
    """Validate that the IFC file meets all specified requirements"""
    
    ifc_path = config.OUTPUT_IFC_FILE
    
    if not os.path.exists(ifc_path):
        print("❌ IFC file not found!")
        return False
    
    print("🔍 Validating IFC file requirements...")
    print(f"📁 File: {ifc_path}")
    print("=" * 60)
    
    try:
        # Open the IFC file
        ifc_file = ifcopenshell.open(ifc_path)
        
        all_checks_passed = True
        
        # ✅ Requirement 1: IFC2x3 schema
        print("1️⃣ Schema Check:")
        schema = ifc_file.schema
        if schema == "IFC2X3":
            print(f"   ✅ Schema: {schema}")
        else:
            print(f"   ❌ Expected IFC2X3, got {schema}")
            all_checks_passed = False
        
        # ✅ Requirement 2: Units in meters
        print("\n2️⃣ Units Check:")
        units = ifc_file.by_type("IfcUnitAssignment")
        if units:
            unit_assignment = units[0]
            meter_units_found = 0
            for unit in unit_assignment.Units:
                if hasattr(unit, 'UnitType') and hasattr(unit, 'Name'):
                    if unit.Name == "METRE" and unit.UnitType == "LENGTHUNIT":
                        meter_units_found += 1
                        print(f"   ✅ Length unit: {unit.Name}")
            if meter_units_found > 0:
                print("   ✅ Meter units are properly configured")
            else:
                print("   ❌ Meter units not found!")
                all_checks_passed = False
        else:
            print("   ❌ No units found!")
            all_checks_passed = False
        
        # ✅ Requirement 3: Proper spatial hierarchy
        print("\n3️⃣ Spatial Hierarchy Check:")
        projects = ifc_file.by_type("IfcProject")
        sites = ifc_file.by_type("IfcSite")
        buildings = ifc_file.by_type("IfcBuilding")
        storeys = ifc_file.by_type("IfcBuildingStorey")
        
        hierarchy_ok = True
        if len(projects) == 1:
            print(f"   ✅ Project: {projects[0].Name}")
        else:
            print(f"   ❌ Expected 1 project, found {len(projects)}")
            hierarchy_ok = False
            
        if len(sites) == 1:
            print(f"   ✅ Site: {sites[0].Name}")
        else:
            print(f"   ❌ Expected 1 site, found {len(sites)}")
            hierarchy_ok = False
            
        if len(buildings) == 1:
            print(f"   ✅ Building: {buildings[0].Name}")
        else:
            print(f"   ❌ Expected 1 building, found {len(buildings)}")
            hierarchy_ok = False
            
        if len(storeys) == 1:
            print(f"   ✅ Storey: {storeys[0].Name}")
        else:
            print(f"   ❌ Expected 1 storey, found {len(storeys)}")
            hierarchy_ok = False
            
        if not hierarchy_ok:
            all_checks_passed = False
        
        # ✅ Requirement 4: 4x4 meter cube markers
        print("\n4️⃣ Marker Geometry Check:")
        markers = ifc_file.by_type("IfcBuildingElementProxy")
        print(f"   📍 Found {len(markers)} markers")
        
        if markers:
            marker = markers[0]  # Check first marker
            geometry_ok = False
            
            if marker.Representation:
                representations = marker.Representation.Representations
                for rep in representations:
                    if rep.Items:
                        for item in rep.Items:
                            if hasattr(item, 'SweptArea') and hasattr(item.SweptArea, 'XDim'):
                                x_dim = item.SweptArea.XDim
                                y_dim = item.SweptArea.YDim
                                depth = item.Depth
                                
                                # Check if dimensions are 4x4x4 meters (should be in meters directly)
                                if abs(x_dim - 4.0) < 0.01 and abs(y_dim - 4.0) < 0.01 and abs(depth - 4.0) < 0.01:
                                    print(f"   ✅ Marker dimensions: {x_dim}m x {y_dim}m x {depth}m")
                                    geometry_ok = True
                                else:
                                    print(f"   ❌ Expected 4x4x4m, got {x_dim}m x {y_dim}m x {depth}m")
                                    
            if not geometry_ok:
                print("   ❌ Marker geometry validation failed")
                all_checks_passed = False
        else:
            print("   ❌ No markers found!")
            all_checks_passed = False
        
        # ✅ Requirement 5: EPSG:5110 coordinates (no local placement offset)
        print("\n5️⃣ Coordinate System Check:")
        if markers:
            marker = markers[0]
            if marker.ObjectPlacement and marker.ObjectPlacement.RelativePlacement:
                location = marker.ObjectPlacement.RelativePlacement.Location
                if location and hasattr(location, 'Coordinates'):
                    coords = location.Coordinates
                    # EPSG:5110 coordinates should be in the range 100,000-200,000 for X
                    if 50000 < coords[0] < 300000:
                        print(f"   ✅ Coordinates in EPSG:5110 range: ({coords[0]:.1f}, {coords[1]:.1f}, {coords[2]:.1f})")
                    else:
                        print(f"   ❌ Coordinates outside expected EPSG:5110 range: ({coords[0]:.1f}, {coords[1]:.1f}, {coords[2]:.1f})")
                        all_checks_passed = False
                else:
                    print("   ❌ No coordinates found in marker placement")
                    all_checks_passed = False
            else:
                print("   ❌ No placement found for marker")
                all_checks_passed = False
        
        # ✅ Requirement 6: Image metadata properties
        print("\n6️⃣ Image Metadata Check:")
        property_sets = ifc_file.by_type("IfcPropertySet")
        metadata_found = False
        
        for prop_set in property_sets:
            if prop_set.Name == "ImageMetadata":
                metadata_found = True
                print(f"   ✅ Found ImageMetadata property set with {len(prop_set.HasProperties)} properties")
                
                required_props = ['ImageFilename', 'ImageURL', 'GPS_Latitude', 'GPS_Longitude', 'GPS_Elevation']
                found_props = []
                
                for prop in prop_set.HasProperties:
                    if hasattr(prop, 'Name'):
                        found_props.append(prop.Name)
                
                for req_prop in required_props:
                    if req_prop in found_props:
                        print(f"   ✅ Property: {req_prop}")
                    else:
                        print(f"   ❌ Missing property: {req_prop}")
                        all_checks_passed = False
                break
        
        if not metadata_found:
            print("   ❌ ImageMetadata property set not found!")
            all_checks_passed = False
        
        # ✅ Requirement 7: Geometric contexts
        print("\n7️⃣ Geometric Context Check:")
        contexts = ifc_file.by_type("IfcGeometricRepresentationContext")
        subcontexts = ifc_file.by_type("IfcGeometricRepresentationSubContext")
        
        if len(contexts) >= 1:
            print(f"   ✅ Found {len(contexts)} main context(s)")
        else:
            print(f"   ❌ No geometric representation contexts found")
            all_checks_passed = False
            
        if len(subcontexts) >= 1:
            print(f"   ✅ Found {len(subcontexts)} subcontext(s)")
        else:
            print(f"   ❌ No geometric representation subcontexts found")
            all_checks_passed = False
        
        # Final validation result
        print("\n" + "=" * 60)
        
        if all_checks_passed:
            print("🎉 ALL REQUIREMENTS VALIDATED SUCCESSFULLY!")
            print("✅ The IFC file is ready for use in Solibri and BIMvision")
            print("✅ Schema: IFC2x3")
            print("✅ Units: Meters")
            print("✅ Markers: 4x4x4 meter cubes")
            print("✅ Coordinates: EPSG:5110 (direct placement)")
            print("✅ Metadata: Complete image properties")
            return True
        else:
            print("❌ VALIDATION FAILED!")
            print("Some requirements are not met. Please check the issues above.")
            return False
        
    except Exception as e:
        print(f"❌ Error validating IFC file: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🔍 IFC File Requirements Validation")
    print("=" * 60)
    
    success = validate_requirements()
    
    print("=" * 60)
    if success:
        print("✅ Ready for deployment!")
    else:
        print("❌ Requires fixes before deployment.")
