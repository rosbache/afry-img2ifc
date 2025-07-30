"""
IFC exporter for creating 3D cube markers at image locations
"""

import os
import math
import ifcopenshell
import ifcopenshell.api
import numpy as np
from typing import List, Dict, Tuple
import config
import time


class IFCExporter:
    """Handles IFC file creation and 3D marker generation"""
    
    def __init__(self):
        """Initialize IFC exporter"""
        self.ifc_file = None
        self.project = None
        self.site = None
        self.building = None
        self.storey = None
        self.context = None
        self.project_settings = None
    
    def set_project_settings(self, project_settings: dict):
        """
        Set project settings from JSON configuration
        
        Args:
            project_settings: Dictionary containing project settings
        """
        self.project_settings = project_settings
        print(f"✅ Project settings configured")
    
    def _create_meter_units(self):
        """Create meter-based units for IFC2x3"""
        # Create length unit (meter)
        length_unit = self.ifc_file.createIfcSIUnit(
            UnitType="LENGTHUNIT",
            Name="METRE"
        )
        
        # Create area unit (square meter)
        area_unit = self.ifc_file.createIfcSIUnit(
            UnitType="AREAUNIT", 
            Name="SQUARE_METRE"
        )
        
        # Create volume unit (cubic meter)
        volume_unit = self.ifc_file.createIfcSIUnit(
            UnitType="VOLUMEUNIT",
            Name="CUBIC_METRE"
        )
        
        # Create unit assignment
        unit_assignment = self.ifc_file.createIfcUnitAssignment([
            length_unit,
            area_unit,
            volume_unit
        ])
        
        # Assign units to project
        self.project.UnitsInContext = unit_assignment
    
    def create_ifc_file(self):
        """Create a new IFC file with basic structure"""
        # Create new IFC file
        self.ifc_file = ifcopenshell.file()
        
        # Use project settings if available, otherwise use defaults
        if self.project_settings and 'project_settings' in self.project_settings:
            ps = self.project_settings['project_settings']
            project_name = ps.get('ifc_project_name', getattr(config, 'IFC_PROJECT_NAME', 'Default Project'))
            project_description = ps.get('ifc_project_description', getattr(config, 'IFC_PROJECT_DESCRIPTION', 'Default Description'))
            site_name = ps.get('ifc_site_name', getattr(config, 'IFC_SITE_NAME', 'Default Site'))
            site_description = ps.get('ifc_site_description', getattr(config, 'IFC_SITE_DESCRIPTION', 'Default Site Description'))
            building_name = ps.get('ifc_building', getattr(config, 'IFC_BUILDING', 'Default Building'))
            building_description = ps.get('ifc_building_description', getattr(config, 'IFC_BUILDING_DESCRIPTION', 'Default Building Description'))
            storey_name = ps.get('ifc_building_storey', getattr(config, 'IFC_BUILDING_STOREY', 'Default Storey'))
            storey_description = ps.get('ifc_building_storey_description', getattr(config, 'IFC_BUILDING_STOREY_DESCRIPTION', 'Default Storey Description'))
        else:
            project_name = getattr(config, 'IFC_PROJECT_NAME', 'Default Project')
            project_description = getattr(config, 'IFC_PROJECT_DESCRIPTION', 'Default Description')
            site_name = getattr(config, 'IFC_SITE_NAME', 'Default Site')
            site_description = getattr(config, 'IFC_SITE_DESCRIPTION', 'Default Site Description')
            building_name = getattr(config, 'IFC_BUILDING', 'Default Building')
            building_description = getattr(config, 'IFC_BUILDING_DESCRIPTION', 'Default Building Description')
            storey_name = getattr(config, 'IFC_BUILDING_STOREY', 'Default Storey')
            storey_description = getattr(config, 'IFC_BUILDING_STOREY_DESCRIPTION', 'Default Storey Description')
        
        # Use owner information if available
        if self.project_settings and 'owner_information' in self.project_settings:
            owner_info = self.project_settings['owner_information']
            person_given_name = owner_info.get('person_given_name', getattr(config, 'PERSON_GIVEN_NAME', 'Default'))
            person_family_name = owner_info.get('person_family_name', getattr(config, 'PERSON_FAMILY_NAME', 'User'))
            organization_name = owner_info.get('organization_name', getattr(config, 'ORGANIZATION_NAME', 'Default Organization'))
        else:
            person_given_name = getattr(config, 'PERSON_GIVEN_NAME', 'Default')
            person_family_name = getattr(config, 'PERSON_FAMILY_NAME', 'User')
            organization_name = getattr(config, 'ORGANIZATION_NAME', 'Default Organization')

        # Create application and owner history
        application = self.ifc_file.create_entity(
            "IfcApplication",
            ApplicationDeveloper=self.ifc_file.create_entity("IfcOrganization", Name=organization_name),
            Version="1.0",
            ApplicationFullName="Image GPS to IFC Converter",
            ApplicationIdentifier="IMG2IFC"
        )
        
        person = self.ifc_file.create_entity(
            "IfcPerson",
            GivenName=person_given_name,
            FamilyName=person_family_name
        )
        
        person_and_organization = self.ifc_file.create_entity(
            "IfcPersonAndOrganization",
            ThePerson=person,
            TheOrganization=application.ApplicationDeveloper
        )
        
        owner_history = self.ifc_file.create_entity(
            "IfcOwnerHistory",
            OwningUser=person_and_organization,
            OwningApplication=application,
            State="READWRITE",
            ChangeAction="ADDED",
            CreationDate=int(time.time())
        )

        # Create geometric representation context first (required for project)
        self.context = self.ifc_file.createIfcGeometricRepresentationContext(
            ContextType="Model",
            CoordinateSpaceDimension=3,
            Precision=0.00001,
            WorldCoordinateSystem=self.ifc_file.createIfcAxis2Placement3D(
                self.ifc_file.createIfcCartesianPoint([0.0, 0.0, 0.0])
            ),
            TrueNorth=None
        )
        
        # Create units first (required for project)
        length_unit = self.ifc_file.createIfcSIUnit(
            UnitType="LENGTHUNIT",
            Name="METRE"
        )
        area_unit = self.ifc_file.createIfcSIUnit(
            UnitType="AREAUNIT", 
            Name="SQUARE_METRE"
        )
        volume_unit = self.ifc_file.createIfcSIUnit(
            UnitType="VOLUMEUNIT",
            Name="CUBIC_METRE"
        )
        unit_assignment = self.ifc_file.createIfcUnitAssignment([
            length_unit,
            area_unit,
            volume_unit
        ])
        
        # Create project ONLY ONCE with required attributes
        self.project = self.ifc_file.createIfcProject(
            ifcopenshell.guid.new(),
            owner_history,
            project_name,
            project_description,
            None,
            None,
            None,
            [self.context],  # RepresentationContexts
            unit_assignment   # UnitsInContext
        )
        
        # Create 3D body context as subcontext
        self.body_context = self.ifc_file.createIfcGeometricRepresentationSubContext(
            ContextIdentifier="Body",
            ContextType="Model", 
            ParentContext=self.context,
            TargetView="MODEL_VIEW",
            TargetScale=None,
            UserDefinedTargetView=None,
            WorldCoordinateSystem=None,
            TrueNorth=None
        )
        
        # Create site
        self.site = self.ifc_file.createIfcSite(
            ifcopenshell.guid.new(),
            owner_history,
            site_name,
            site_description,
            None,
            self.ifc_file.createIfcLocalPlacement(
                None,
                self.ifc_file.createIfcAxis2Placement3D(
                    self.ifc_file.createIfcCartesianPoint([0.0, 0.0, 0.0])
                )
            ),
            None,
            None,
            "ELEMENT",
            None,
            None,
            None,
            None,
            None
        )
        
        # Assign site to project
        self.ifc_file.createIfcRelAggregates(
            ifcopenshell.guid.new(),
            owner_history,
            "Project-Site",
            None,
            self.project,
            [self.site]
        )
        
        # Create building
        self.building = self.ifc_file.createIfcBuilding(
            ifcopenshell.guid.new(),
            owner_history,
            building_name,
            building_description,
            None,
            self.ifc_file.createIfcLocalPlacement(
                self.site.ObjectPlacement,
                self.ifc_file.createIfcAxis2Placement3D(
                    self.ifc_file.createIfcCartesianPoint([0.0, 0.0, 0.0])
                )
            ),
            None,
            None,
            "ELEMENT",
            None,
            None,
            None
        )
        
        # Assign building to site
        self.ifc_file.createIfcRelAggregates(
            ifcopenshell.guid.new(),
            owner_history,
            "Site-Building",
            None,
            self.site,
            [self.building]
        )
        
        # Create building storey
        self.storey = self.ifc_file.createIfcBuildingStorey(
            ifcopenshell.guid.new(),
            owner_history,
            storey_name,
            storey_description,
            None,
            self.ifc_file.createIfcLocalPlacement(
                self.building.ObjectPlacement,
                self.ifc_file.createIfcAxis2Placement3D(
                    self.ifc_file.createIfcCartesianPoint([0.0, 0.0, 0.0])
                )
            ),
            None,
            None,
            "ELEMENT",
            None
        )
        
        # Assign storey to building
        self.ifc_file.createIfcRelAggregates(
            ifcopenshell.guid.new(),
            owner_history,
            "Building-Storey",
            None,
            self.building,
            [self.storey]
        )
        
        return self.ifc_file
    
    def create_red_style(self) -> ifcopenshell.entity_instance:
        """
        Create a red color style for the cube markers
        
        Returns:
            IfcStyledItem with red color
        """
        # Create red color (RGB 255,0,0 -> normalized to 1.0,0.0,0.0)
        red_color = ifcopenshell.api.run("style.add_style", 
                                       self.ifc_file,
                                       name="Red")
        
        # Add surface style with red color
        ifcopenshell.api.run("style.add_surface_style",
                           self.ifc_file,
                           style=red_color,
                           ifc_class="IfcSurfaceStyleShading",
                           attributes={
                               "SurfaceColour": {
                                   "Red": 1.0,    # 255/255 = 1.0
                                   "Green": 0.0,  # 0/255 = 0.0
                                   "Blue": 0.0    # 0/255 = 0.0
                               }
                           })
        
        return red_color
    
    def create_cube_geometry(self, radius: float = None) -> ifcopenshell.entity_instance:
        """
        Create a simple box geometry as a marker (more reliable than spheres)
        
        Args:
            radius: Size of the marker in meters (uses config default if None)
            
        Returns:
            IfcShapeRepresentation for the marker
        """
        if radius is None:
            # Convert config radius from mm to meters for IFC2x3
            radius = config.SPHERE_RADIUS / 1000.0
        
        # Create a simple box geometry for better compatibility
        size = radius * 2  # Make box size based on radius (4m for 2m radius)
        
        # Create a rectangular profile for the box
        rectangle = self.ifc_file.createIfcRectangleProfileDef(
            "AREA", 
            "MarkerProfile", 
            self.ifc_file.createIfcAxis2Placement2D(
                self.ifc_file.createIfcCartesianPoint([0.0, 0.0])
            ), 
            size, 
            size
        )
        
        # Create extruded area solid (box)
        position = self.ifc_file.createIfcAxis2Placement3D(
            self.ifc_file.createIfcCartesianPoint([0.0, 0.0, 0.0])
        )
        
        direction = self.ifc_file.createIfcDirection([0.0, 0.0, 1.0])
        
        extruded_solid = self.ifc_file.createIfcExtrudedAreaSolid(
            SweptArea=rectangle,
            Position=position,
            ExtrudedDirection=direction,
            Depth=size
        )
        
        # Create shape representation
        shape_representation = self.ifc_file.createIfcShapeRepresentation(
            ContextOfItems=self.body_context,
            RepresentationIdentifier="Body",
            RepresentationType="SweptSolid",
            Items=[extruded_solid]
        )
        
        # Create and apply red color style
        red_style = self.create_red_style()
        
        # Apply style to the extruded solid
        ifcopenshell.api.run("style.assign_representation_styles",
                           self.ifc_file,
                           shape_representation=shape_representation,
                           styles=[red_style])
        
        return shape_representation
    
    def create_cube_marker(self, image_data: Dict, geometry: ifcopenshell.entity_instance = None) -> ifcopenshell.entity_instance:
        """
        Create a marker element at the image location with optional embedded image
        
        Args:
            image_data: Dictionary containing image metadata and coordinates
            geometry: Optional pre-created geometry (if None, creates textured cube)
            
        Returns:
            Created IfcBuildingElementProxy (marker)
        """
        # Get owner history from project
        owner_history = self.project.OwnerHistory
        
        # Create geometry with embedded image if not provided
        if geometry is None:
            geometry = self.create_cube_geometry()
        
        # Ensure all required fields are present
        if not all(k in image_data for k in ("transformed_x", "transformed_y", "transformed_z")):
            raise ValueError(f"Missing transformed coordinates for {image_data.get('filename', 'unknown image')}")
        
        # Create marker as building element proxy manually
        cube = self.ifc_file.createIfcBuildingElementProxy(
            ifcopenshell.guid.new(),
            owner_history,
            f"Image Marker - {image_data.get('filename', 'Unknown')}",
            "360° panoramic image marker at GPS location",
            None,
            self.ifc_file.createIfcLocalPlacement(
                self.storey.ObjectPlacement,
                self.ifc_file.createIfcAxis2Placement3D(
                    self.ifc_file.createIfcCartesianPoint([
                        float(image_data['transformed_x']),
                        float(image_data['transformed_y']),
                        float(image_data['transformed_z'])
                    ])
                )
            ),
            self.ifc_file.createIfcProductDefinitionShape(None, None, [geometry]),
            None,
            "ELEMENT"
        )
        
        # Assign to building storey manually
        self.ifc_file.createIfcRelContainedInSpatialStructure(
            ifcopenshell.guid.new(),
            owner_history,
            "StoreyContains",
            None,
            [cube],
            self.storey
        )
        
        # Add custom properties for image data
        self._add_image_properties(cube, image_data)
        
        # Add document reference for clickable image access
        self.add_image_document_reference(cube, image_data)

        return cube
        
    def add_image_document_reference(self, element: ifcopenshell.entity_instance, image_data: Dict):
        """
        Add document reference to link the image to the marker element
        
        Args:
            element: The IFC element to link the document to
            image_data: Dictionary containing image metadata including URL
        """
        try:
            # Get owner history from project
            owner_history = self.project.OwnerHistory
            
            # Create document reference (different between IFC2x3 and IFC4)
            # In IFC4, ItemReference is not available
            try:
                # Try to create IFC4 version
                document = self.ifc_file.create_entity(
                    "IfcDocumentReference",
                    Description=f"360° panoramic image - {image_data.get('filename', 'Unknown')}",
                    Location=image_data.get('image_url', ''),
                    Identification=image_data.get('filename', 'Unknown')
                )
            except Exception as e1:
                print(f"Trying alternative document reference format: {e1}")
                try:
                    # Try to create IFC2x3 version
                    document = self.ifc_file.createIfcDocumentReference(
                        Location=image_data.get('image_url', ''),
                        ItemReference=image_data.get('filename', 'Unknown'),
                        Name="360° panoramic image"
                    )
                except Exception as e2:
                    print(f"Could not create document reference: {e2}")
                    # Skip document reference if it fails
                    return
            
            # Create document information relationship
            self.ifc_file.createIfcRelAssociatesDocument(
                GlobalId=ifcopenshell.guid.new(),
                OwnerHistory=owner_history,
                RelatedObjects=[element],
                RelatingDocument=document
            )
        except Exception as e:
            print(f"Error adding document reference: {e}")
            # Continue without the document reference

    def _add_image_properties(self, element: ifcopenshell.entity_instance, image_data: Dict):
        """Add custom properties to the marker element with image metadata"""
        
        # Get owner history from project
        owner_history = self.project.OwnerHistory
        
        # Create property values
        property_values = []
        
        # Add filename
        property_values.append(
            self.ifc_file.createIfcPropertySingleValue(
                Name="ImageFilename",
                NominalValue=self.ifc_file.createIfcText(image_data['filename'])
            )
        )
        
        # Add URL
        property_values.append(
            self.ifc_file.createIfcPropertySingleValue(
                Name="ImageURL",
                NominalValue=self.ifc_file.createIfcText(image_data['image_url'])
            )
        )
        
        # Add original GPS coordinates
        property_values.append(
            self.ifc_file.createIfcPropertySingleValue(
                Name="GPS_Latitude",
                NominalValue=self.ifc_file.createIfcReal(image_data['latitude'])
            )
        )
        
        property_values.append(
            self.ifc_file.createIfcPropertySingleValue(
                Name="GPS_Longitude",
                NominalValue=self.ifc_file.createIfcReal(image_data['longitude'])
            )
        )
        
        property_values.append(
            self.ifc_file.createIfcPropertySingleValue(
                Name="GPS_Elevation",
                NominalValue=self.ifc_file.createIfcReal(image_data['elevation'])
            )
        )

        # Add date taken if available
        if image_data.get('date_taken'):
            property_values.append(
                self.ifc_file.createIfcPropertySingleValue(
                    Name="DateTaken",
                    NominalValue=self.ifc_file.createIfcText(image_data['date_taken'])
                )
            )
        
        # Create property set
        property_set = self.ifc_file.createIfcPropertySet(
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=owner_history,
            Name="ImageMetadata",
            HasProperties=property_values
        )
        
        # Relate to element
        self.ifc_file.createIfcRelDefinesByProperties(
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=owner_history,
            RelatedObjects=[element],
            RelatingPropertyDefinition=property_set
        )
        
    def export_markers_from_json(self, json_file_path: str, output_path: str, project_settings_path: str = None):
        """
        Export markers directly from a JSON file
        
        Args:
            json_file_path: Path to JSON file with image data
            output_path: Path to output IFC file
            project_settings_path: Optional path to project settings JSON file
        """
        import json
        import os
        
        # Load processed images from JSON
        print(f"Loading image data from: {json_file_path}")
        with open(json_file_path, 'r', encoding='utf-8') as f:
            processed_images = json.load(f)
        
        print(f"Loaded {len(processed_images)} images")
        
        # Print first image data to verify structure
        if processed_images and len(processed_images) > 0:
            print(f"First image data keys: {list(processed_images[0].keys())}")
            print(f"First image filename: {processed_images[0].get('filename', 'unknown')}")
            print(f"First image transformed coordinates: {processed_images[0].get('transformed_x', 'N/A')}, "
                  f"{processed_images[0].get('transformed_y', 'N/A')}, {processed_images[0].get('transformed_z', 'N/A')}")
        
        # Load project settings if provided
        if project_settings_path and os.path.exists(project_settings_path):
            print(f"Loading project settings from: {project_settings_path}")
            with open(project_settings_path, 'r', encoding='utf-8') as f:
                project_settings = json.load(f)
            self.set_project_settings(project_settings)
            
        # Export the markers
        self.export_markers(processed_images, output_path)
    
    def export_markers(self, processed_images: List[Dict], output_path: str):
        """
        Export all image markers to IFC file
        
        Args:
            processed_images: List of processed image data
            output_path: Path to output IFC file
        """
        import os
        import json
        
        if not processed_images:
            print("No processed images to export.")
            return

        # Debug: Print first image data to verify structure
        if processed_images and len(processed_images) > 0:
            print(f"First image data keys: {list(processed_images[0].keys())}")
            
        print(f"Creating IFC file with {len(processed_images)} markers...")

        # Create IFC file structure
        try:
            print("Creating IFC file structure...")
            self.create_ifc_file()
            print("IFC structure created successfully")
        except Exception as e:
            print(f"Error creating IFC structure: {e}")
            import traceback
            traceback.print_exc()
            return

        # Create marker geometry (reuse for all markers)
        try:
            print("Creating marker geometry...")
            marker_radius = 1.0  # meters
            marker_geometry = self.create_cube_geometry(radius=marker_radius)
            print("Geometry created successfully")
        except Exception as e:
            print(f"Error creating geometry: {e}")
            import traceback
            traceback.print_exc()
            return

        # Create markers for each image
        markers_created = 0
        for image_data in processed_images:
            try:
                # Check if the required transformed coordinates exist
                if all(k in image_data for k in ("transformed_x", "transformed_y", "transformed_z")):
                    # Place marker at the transformed coordinates
                    image_data.setdefault('filename', 'Marker')
                    image_data.setdefault('image_url', '')
                    image_data.setdefault('latitude', 0.0)
                    image_data.setdefault('longitude', 0.0)
                    image_data.setdefault('elevation', 0.0)
                    image_data.setdefault('date_taken', '')
                    
                    # Debug: Print the transformed coordinates
                    print(f"Creating marker for {image_data['filename']} at ({image_data['transformed_x']}, {image_data['transformed_y']}, {image_data['transformed_z']})")
                    
                    # Create the marker
                    self.create_cube_marker(image_data, geometry=marker_geometry)
                    markers_created += 1
                    print(f"Created marker for {image_data['filename']}")
                else:
                    print(f"Skipping image (missing transformed coordinates): {image_data.get('filename')}")
                    # Debug: Print available keys
                    print(f"Available keys: {list(image_data.keys())}")
            except Exception as e:
                print(f"Error creating marker for {image_data.get('filename', 'unknown')}: {str(e)}")
                import traceback
                traceback.print_exc()

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Write IFC file
        try:
            self.ifc_file.write(output_path)
            print(f"Successfully exported {markers_created} markers to {output_path}")
        except Exception as e:
            print(f"Error writing IFC file: {str(e)}")
            import traceback
            traceback.print_exc()

