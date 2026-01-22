# Temporary fix for get_tab_points
from shapely.geometry import Polygon

def get_tab_points_fixed(start_x, width, height, radius, direction=1):
    """Generate tab points with optional smooth rounding using Shapely"""
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

# Test
if __name__ == "__main__":
    points = get_tab_points_fixed(0, 20, 10, 2, 1)
    print(f"Generated {len(points)} points")
    for i, p in enumerate(points[:5]):
        print(f"  Point {i}: {p}")
