#!/bin/bash
# Fix the get_tab_points function in core.py

# Create backup
cp core.py core.py.backup

# Find and replace the get_tab_points function (lines 97-168)
# We'll use Python to do this more reliably

python3 << 'EOF'
import re

with open('core.py', 'r') as f:
    content = f.read()

# Find the first get_tab_points function and replace it
new_function = '''        def get_tab_points(start_x, width, height, radius, direction=1):
            """Generate tab points with optional smooth rounding using Shapely"""
            from shapely.geometry import Polygon
            
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
            
            # Use Shapely buffer for smooth rounding
            poly = Polygon([p1, p2, p3, p4, p5, p6])
            
            # Limit radius to avoid over-rounding
            eff_radius = min(radius, width/8.0, abs(height)/4.0)
            
            # Buffer out then in to round corners
            rounded = poly.buffer(eff_radius, join_style=1, resolution=16).buffer(-eff_radius, join_style=1, resolution=16)
            
            # Extract coordinates
            coords = list(rounded.exterior.coords)
            if coords[0] == coords[-1]:
                coords = coords[:-1]
            
            return coords
'''

# Pattern to match the first get_tab_points function (from line 97 to the return statement around line 168)
pattern = r'(        def get_tab_points\(start_x, width, height, radius, direction=1\):.*?return new_path)'

# Replace first occurrence only
content = re.sub(pattern, new_function.rstrip(), content, count=1, flags=re.DOTALL)

with open('core.py', 'w') as f:
    f.write(content)

print("Fixed get_tab_points function")
EOF
