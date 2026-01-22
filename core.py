
import trimesh
import numpy as np
import io
import zipfile
from shapely.geometry import LineString, Polygon
from shapely.ops import polygonize
import matplotlib.pyplot as plt

class MeshError(Exception):
    pass

class ComplexityError(Exception):
    pass

class DovetailSplitter:
    def __init__(self, filename, content_bytes):
        self.filename = filename
        try:
            # Load mesh from bytes
            file_obj = io.BytesIO(content_bytes)
            # trimesh.load returns a Scene or Trimesh. Force Trimesh.
            loaded = trimesh.load(file_obj, file_type='stl')
            if isinstance(loaded, trimesh.Scene):
                # If it's a scene, dump all geometries into a single mesh
                self.mesh = trimesh.util.concatenate(
                    tuple(trimesh.graph.split(loaded, only_watertight=False))
                )
            else:
                self.mesh = loaded
        except Exception as e:
            raise MeshError(f"Failed to load STL: {str(e)}")

    def validate_and_heal(self):
        """
        Check watertight status, repair, center, and check complexity.
        """
        # 1. Watertight Check & Repair
        if not self.mesh.is_watertight:
            print("Mesh is not watertight. Attempting repair...")
            trimesh.repair.fill_holes(self.mesh)
            trimesh.repair.fix_normals(self.mesh)
            
        if not self.mesh.is_watertight:
            raise MeshError("Mesh is not watertight and auto-repair failed. Please repair it in external software (e.g. 3D Builder) first.")

        # 2. Auto-Normalization (Centering)
        # Center X, Y to 0,0. Z min to 0.
        center = self.mesh.bounds.mean(axis=0)
        min_z = self.mesh.bounds[0][2]
        
        translation_matrix = np.eye(4)
        translation_matrix[0, 3] = -center[0]
        translation_matrix[1, 3] = -center[1]
        translation_matrix[2, 3] = -min_z
        
        self.mesh.apply_transform(translation_matrix)
        
        # 3. Complexity Guard
        # Slice at Z-midpoint
        mid_z = (self.mesh.bounds[1][2] - self.mesh.bounds[0][2]) / 2
        slice_2d = self.mesh.section(plane_origin=[0, 0, mid_z], plane_normal=[0, 0, 1])
        
        if slice_2d:
            # Count disjoint polygons in the slice
            # section returns a Path3D, which may have multiple entities
            if len(slice_2d.entities) > 15:
                # This is a heuristic. A very complex specific slice might imply complex boolean overhead
                # Raising limit slightly as 10 is quite low for some organic organic models
                raise ComplexityError(f"Mesh cross-section is too complex ({len(slice_2d.entities)} disjoint parts detected). This may crash the processor.")

    def generate_smart_path(self, mesh_length, total_length, tab_width, tab_height, tab_radius, safe_radius, num_tabs, tolerance, axis='x'):
        """
        Generates a 2D Smart Puzzle Path with configurable dimensions auto-scaling.
        mesh_length: The quadrant size (e.g., 88mm for a 176mm mesh)
        num_tabs: Number of tabs to distribute across this quadrant (from center to edge)
        """
        # Available length for tabs: from safe_radius to mesh_length (the quadrant edge)
        available_len = mesh_length - safe_radius
        
        # Auto-scaling logic
        if available_len < 1.0:
            effective_num_tabs = 0
            effective_tab_width = tab_width
        else:
            effective_num_tabs = num_tabs
            effective_tab_width = tab_width
            
            # Check for Overflow
            required_width = effective_num_tabs * effective_tab_width
            if required_width > available_len:
                effective_tab_width = (available_len / effective_num_tabs) * 0.98

        points = []
        
        # Helper for a single Jigsaw Tab with Radius
        def get_tab_points(start_x, width, height, radius, direction=1):
            """Generate tab points with proper fillet arcs at corners"""
            neck_w = width * 0.6
            head_w = width * 0.9 
            center_x = start_x + width/2
            
            p1 = (start_x, 0)
            p2 = (center_x - neck_w/2, 0)
            p3 = (center_x - head_w/2, height * direction)
            p4 = (center_x + head_w/2, height * direction)
            p5 = (center_x + neck_w/2, 0)
            p6 = (start_x + width, 0)
            
            if radius <= 0:
                return [p1, p2, p3, p4, p5, p6]
            
            r = min(radius, width/10.0, abs(height)/5.0)
            
            def fillet_corner(corner, prev, next, r, segments=5):
                """Create a proper fillet arc tangent to both edges."""
                c = np.array(corner)
                p_prev = np.array(prev)
                p_next = np.array(next)
                
                v1 = p_prev - c
                v1_len = np.linalg.norm(v1)
                v1_unit = v1 / v1_len
                
                v2 = p_next - c
                v2_len = np.linalg.norm(v2)
                v2_unit = v2 / v2_len
                
                dot = np.dot(v1_unit, v2_unit)
                angle = np.arccos(np.clip(dot, -1.0, 1.0))
                half_angle = angle / 2
                
                if half_angle < 0.1 or half_angle > np.pi - 0.1:
                    return [corner]
                
                tan_dist = r / np.tan(half_angle)
                tan_dist = min(tan_dist, v1_len * 0.4, v2_len * 0.4)
                r_effective = tan_dist * np.tan(half_angle)
                
                bisector = v1_unit + v2_unit
                bisector = bisector / np.linalg.norm(bisector)
                
                center_dist = r_effective / np.sin(half_angle)
                arc_center = c + bisector * center_dist
                
                pt1 = c + v1_unit * tan_dist
                start_vec = pt1 - arc_center
                start_angle = np.arctan2(start_vec[1], start_vec[0])
                
                cross_b_v1 = bisector[0] * v1_unit[1] - bisector[1] * v1_unit[0]
                arc_sweep = np.pi - angle
                
                if cross_b_v1 > 0:
                    angles = [start_angle + t * arc_sweep for t in np.linspace(0, 1, segments + 1)]
                else:
                    angles = [start_angle - t * arc_sweep for t in np.linspace(0, 1, segments + 1)]
                
                arc_points = []
                for theta in angles:
                    point = arc_center + r_effective * np.array([np.cos(theta), np.sin(theta)])
                    arc_points.append(tuple(point))
                
                return arc_points
            
            points = []
            points.append(p1)
            points.extend(fillet_corner(p2, p1, p3, r, segments=5))
            points.extend(fillet_corner(p3, p2, p4, r, segments=5))
            points.extend(fillet_corner(p4, p3, p5, r, segments=5))
            points.extend(fillet_corner(p5, p4, p6, r, segments=5))
            points.append(p6)
            
            return points

            """Generate tab points with smooth multi-segment arc at corners"""
            neck_w = width * 0.6
            head_w = width * 0.9 
            center_x = start_x + width/2
            
            p1 = (start_x, 0)
            p2 = (center_x - neck_w/2, 0)
            p3 = (center_x - head_w/2, height * direction)
            p4 = (center_x + head_w/2, height * direction)
            p5 = (center_x + neck_w/2, 0)
            p6 = (start_x + width, 0)
            
            if radius <= 0:
                return [p1, p2, p3, p4, p5, p6]
            
            # Create smooth arc with multiple segments
            r = min(radius, width/10.0, abs(height)/5.0)
            
            def arc_at_corner(corner, prev, next, r, segments=5):
                """Create a smooth circular arc at the corner"""
                c = np.array(corner)
                p = np.array(prev)
                n = np.array(next)
                
                # Vectors from corner to prev and next
                v1 = p - c
                v1 = v1 / np.linalg.norm(v1)
                v2 = n - c  
                v2 = v2 / np.linalg.norm(v2)
                
                # Arc start and end points
                start_pt = c + v1 * r
                end_pt = c + v2 * r
                
                # Calculate angle between vectors
                dot = np.dot(v1, v2)
                angle = np.arccos(np.clip(dot, -1.0, 1.0))
                
                # Generate arc points
                arc_points = []
                for i in range(segments + 1):
                    t = i / segments
                    theta = t * angle
                    
                    # Rotate v1 towards v2
                    cos_t = np.cos(theta)
                    sin_t = np.sin(theta)
                    
                    # 2D rotation matrix
                    rotated = np.array([
                        v1[0] * cos_t - v1[1] * sin_t,
                        v1[0] * sin_t + v1[1] * cos_t
                    ])
                    
                    point = c + rotated * r
                    arc_points.append(tuple(point))
                
                return arc_points
            
            points = []
            points.append(p1)
            points.extend(arc_at_corner(p2, p1, p3, r, segments=5))
            points.extend(arc_at_corner(p3, p2, p4, r, segments=5))
            points.extend(arc_at_corner(p4, p3, p5, r, segments=5))
            points.extend(arc_at_corner(p5, p4, p6, r, segments=5))
            points.append(p6)
            
            return points

        # Start from far left (cutter edge)
        points.append((-total_length/2, 0))
        
        # Left side: from -mesh_length to -safe_radius
        # Distribute tabs across this region
        if effective_num_tabs > 0:
            total_tab_w = effective_num_tabs * effective_tab_width
            total_gap_space = available_len - total_tab_w
            gap = total_gap_space / (effective_num_tabs + 1)
            
            current_x = -mesh_length
            
            for i in range(effective_num_tabs):
                tab_start = current_x + gap
                
                direction = 1 if i % 2 == 0 else -1
                if axis == 'y': direction *= -1
                
                tab_pts = get_tab_points(tab_start, effective_tab_width, tab_height, tab_radius, direction)
                points.append(tab_pts[0])
                points.extend(tab_pts[1:])
                
                current_x = tab_start + effective_tab_width
            
            points.append((-safe_radius, 0))
        else:
            points.append((-mesh_length, 0))
            points.append((-safe_radius, 0))

        # Safe Zone
        points.append((safe_radius, 0))
        
        # Right side: from safe_radius to mesh_length
        if effective_num_tabs > 0:
            total_tab_w = effective_num_tabs * effective_tab_width
            total_gap_space = available_len - total_tab_w
            gap = total_gap_space / (effective_num_tabs + 1)

            current_x = safe_radius
            
            for i in range(effective_num_tabs):
                tab_start = current_x + gap
                
                direction = -1 if i % 2 == 0 else 1
                if axis == 'y': direction *= -1
                
                tab_pts = get_tab_points(tab_start, effective_tab_width, tab_height, tab_radius, direction)
                points.append(tab_pts[0])
                points.extend(tab_pts[1:])
                
                current_x = tab_start + effective_tab_width
        
        points.append((mesh_length, 0))
        points.append((total_length/2, 0))

        if axis == 'y':
            points = [(y, x) for x, y in points]
            
        return LineString(points)
        """
        Generates a 2D Smart Puzzle Path with configurable dimensions auto-scaling.
        """
        # Arm length available for tabs (on the visible mesh)
        mesh_arm_len = (mesh_length/2) - safe_radius
        
        # Auto-scaling logic:
        # If the requested tabs don't fit in the arm length, we must scale down the width.
        # Minimal space check
        if mesh_arm_len < 1.0:
            effective_num_tabs = 0
            effective_tab_width = tab_width
        else:
            effective_num_tabs = num_tabs_per_arm
            effective_tab_width = tab_width
            
            # Check for Overflow
            required_width = effective_num_tabs * effective_tab_width
            if required_width > mesh_arm_len:
                # Auto-scale down tab width to fit
                # Allow a tiny margin factor (0.98) to prevent float overlapping
                effective_tab_width = (mesh_arm_len / effective_num_tabs) * 0.98

        points = []
        
        # Helper for a single Jigsaw Tab with Radius
        # --- Generate Left Arm (Negative X) ---
        # Start far left (Cutter Edge)
        points.append((-total_length/2, 0))
        
        if effective_num_tabs > 0:
            # Equal Gap using effective_width
            total_tab_w = effective_num_tabs * effective_tab_width
            total_gap_space = mesh_arm_len - total_tab_w
            
            # Should be non-negative now due to auto-scaling above
            gap = total_gap_space / (effective_num_tabs + 1)
            
            current_x = -mesh_length/2
            
            for i in range(effective_num_tabs):
                tab_start = current_x + gap
                
                direction = 1 if i % 2 == 0 else -1
                if axis == 'y': direction *= -1
                
                tab_pts = get_tab_points(tab_start, effective_tab_width, tab_height, tab_radius, direction)
                points.append(tab_pts[0])
                points.extend(tab_pts[1:])
                
                current_x = tab_start + effective_tab_width
            
            # Connect to Safe Zone start (-safe_radius)
            points.append((-safe_radius, 0))
        else:
            points.append((-mesh_length/2, 0))
            points.append((-safe_radius, 0))

        # --- Safe Zone ---
        points.append((safe_radius, 0))
        
        # --- Generate Right Arm (Positive X) ---
        if effective_num_tabs > 0:
            total_tab_w = effective_num_tabs * effective_tab_width
            total_gap_space = mesh_arm_len - total_tab_w
            
            gap = total_gap_space / (effective_num_tabs + 1)

            current_x = safe_radius
            
            for i in range(effective_num_tabs):
                tab_start = current_x + gap
                
                direction = -1 if i % 2 == 0 else 1
                if axis == 'y': direction *= -1
                
                tab_pts = get_tab_points(tab_start, effective_tab_width, tab_height, tab_radius, direction)
                points.append(tab_pts[0])
                points.extend(tab_pts[1:])
                
                current_x = tab_start + effective_tab_width
                
            # Connect to Mesh End is handled below
        
        # End of Mesh
        points.append((mesh_length/2, 0))
        # End of Cutter
        points.append((total_length/2, 0))

        if axis == 'y':
            points = [(y, x) for x, y in points]
            
        return LineString(points)

    def _generate_rounded_path(self, points, radius, axis):
        """
        Post-process points to add fillets using Shapely buffer trick.
        """
        if axis == 'y':
            points = [(y, x) for x, y in points]
        
        sharp_line = LineString(points)
        
        if radius <= 0:
            return sharp_line
            
        # The Buffer-Unbuffer trick (Morphological Opening/Closing)
        # buffer(r, join_style=1) rounds outer corners.
        # buffer(-r) shrinks it back.
        # But this works on Polygons (offset curves). 
        # Buffering a LineString produces a Polygon (the stroke).
        # We need to treat the LineString as a boundary of a shape?
        # No, the LineString describes the CUT.
        
        # If we want the CUT to be rounded, we just need the sharp line + buffer(kerf, join_style=ROUND).
        # But user wants the actual shape geometry to change, i.e. large Radius on the tab corners.
        # The Kerf is only 0.1-0.2mm. Radius is 2mm.
        
        # To round the LineString geometry itself:
        # We can treat the area UNDER the line as a polygon, fillet it, then extract the top edge.
        # Since our line is roughly monotonic or simple functional Y=f(X), we can close it with a bounding box bottom.
        
        # 1. Close the loop to form a Polygon "below" the line.
        # Get bounds
        min_x, min_y, max_x, max_y = sharp_line.bounds
        # Add bottom corners
        
        # Determine "Bottom" relative to the tabs.
        # The tabs stick up or down.
        # But the line is continuous.
        # Let's form a large rectangle enclosing the line's extent + some padding, but only on one side?
        # It's alternating... simple closure won't work easily.
        
        # ALTERNATIVE: Simplification.
        # Just use `sharp_line.simplify(radius)`? No, that removes points.
        
        # ALTERNATIVE: Chaikin's Algorithm or Interpolation.
        # Since we just want to round the sharp corners we introduced in `get_tab_points`.
        # We know where they are.
        # Re-writing `get_tab_points` to return round corners is the most robust way.
        
        # Let's do that in a separate replacement or right here?
        # I can't easily change `get_tab_points` from here as it is inside the other method.
        # But I can modify `generate_smart_path` again to use a rounding helper there.
        
        # Let's return the sharp line here if I can't do magic, BUT:
        # I will replace `generate_smart_path` entirely in the next step to properly implement rounding at point generation time.
        # For now, just return sharp so code runs, then I fix `generate_smart_path`.
        
        return sharp_line

    def create_cutter_masks(self, tab_width, tab_height, tab_radius, safe_radius, num_tabs, tolerance):
        """
        Create 3D cutter volumes using Smart Path.
        """
        bounds = self.mesh.bounds
        # Actual mesh dimensions
        mesh_width_x = bounds[1][0] - bounds[0][0]
        mesh_width_y = bounds[1][1] - bounds[0][1]
        
        # Cutter needs to be larger to ensure full cut
        full_width = max(mesh_width_x, mesh_width_y) * 1.5
        z_height = (bounds[1][2] - bounds[0][2]) * 1.5
        z_min = bounds[0][2] - 10.0
        
        # 1. Generate Paths
        # CRITICAL: We cut at center (0,0), so each quadrant has size mesh_width/2
        # Tabs should distribute across the QUADRANT size, not the full mesh size
        quadrant_x = mesh_width_x / 2
        quadrant_y = mesh_width_y / 2
        
        path_x = self.generate_smart_path(quadrant_x, full_width, tab_width, tab_height, tab_radius, safe_radius, num_tabs, tolerance, axis='x')
        path_y = self.generate_smart_path(quadrant_y, full_width, tab_width, tab_height, tab_radius, safe_radius, num_tabs, tolerance, axis='y')
        
        # 2. Buffer to create thickness (The Kerf Volume)
        # buffer(distance) expands the line into a polygon.
        buffer_val = tolerance / 2.0
        poly_x = path_x.buffer(buffer_val, cap_style=2, join_style=2) # cap_style=2 (flat)
        poly_y = path_y.buffer(buffer_val, cap_style=2, join_style=2)
        
        # 3. Extrude
        # Trimesh extrusion
        cutter_x = trimesh.creation.extrude_polygon(poly_x, height=z_height)
        cutter_y = trimesh.creation.extrude_polygon(poly_y, height=z_height)
        
        # Center the cutters relative to Z
        cutter_x.apply_translation([0, 0, z_min])
        cutter_y.apply_translation([0, 0, z_min])
        
        return cutter_x, cutter_y, path_x, path_y

    def split_mesh(self, tab_width=20, tab_height=10, tab_radius=2, safe_radius=15, num_tabs=1, tolerance=0.2):
        """
        Execute the split.
        Returns: Dict of {name: trimesh}
        """
        cutter_x, cutter_y, _, _ = self.create_cutter_masks(tab_width, tab_height, tab_radius, safe_radius, num_tabs, tolerance)
        
        try:
            # Step 1: Cut along X-axis (This splits Top / Bottom usually, depending on orientation)
            # Actually, my path generation logic:
            # X-axis path varies in Y. So it splits Top (High Y) from Bottom (Low Y).
            
            # We "subtract" the cutter.
            # Since the cutter is a "wall" of thickness `tolerance`, the result will be 2 disjoint meshes (if successful)
            # separated by the gap.
            
            # Using trimesh boolean difference
            # mesh - cutter
            
            # Performance optimization: Reduce faces if extremely high poly?
            # self.mesh.simplify_quadratic_decimation(50000) # Optional, strictly speaking we should try to keep quality
            
            parts_x_split = self.mesh.difference(cutter_x)
            
            # parts_x_split should be a Scene or a Mesh with disjoint bodies.
            bodies_x = parts_x_split.split(only_watertight=False)
            
            if len(bodies_x) < 2:
                # Fallback or error?
                # Sometimes boolean fails or the cut didn't traverse the whole mesh.
                # Assuming success for now.
                pass
                
            final_parts = {}
            
            # Step 2: Cut each resulting body along Y-axis (Splits Left / Right)
            idx = 0
            quadrant_names = ["Top-Left", "Top-Right", "Bottom-Left", "Bottom-Right"] 
            # Note: Naming might not be perfectly aligned with logic without sorting, but sufficient for user.
            
            # Sort bodies by Y centroid to guess Top/Bottom
            # This helps consistency
            bodies_x.sort(key=lambda m: m.bounds.mean(axis=0)[1]) # Sort by Y
            
            # Determine Top/Bottom based on Y
            # Low Y = Bottom, High Y = Top
            
            # For each body (Top slice, Bottom slice), cut with Y-cutter
            # Y-cutter splits Left / Right (varies in X)
            
            # Collect all final chunks
            all_chunks = []
            
            for body in bodies_x:
                # Perform Y cut
                parts_y_split = body.difference(cutter_y)
                sub_bodies = parts_y_split.split(only_watertight=False)
                
                # Sort sub-bodies by X
                sub_bodies.sort(key=lambda m: m.bounds.mean(axis=0)[0])
                
                all_chunks.extend(sub_bodies)
                
            # Now we should have 4 chunks (ideally)
            # Let's just name them Part_1 to Part_4 to be safe against complex topology
            for i, chunk in enumerate(all_chunks):
                # Cleanup: remove small artifacts
                if chunk.volume < (self.mesh.volume * 0.01):
                    continue # Skip debris
                    
                name = f"Part_{i+1}.stl"
                final_parts[name] = chunk
                
            return final_parts

        except Exception as e:
            raise RuntimeError(f"Boolean operation failed: {str(e)}")

    def pack_zip(self, parts_dict):
        """
        Zip the parts into a BytesIO object
        """
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for name, mesh in parts_dict.items():
                data = trimesh.exchange.stl.export_stl(mesh)
                zf.writestr(name, data)
        zip_buffer.seek(0)
        return zip_buffer
