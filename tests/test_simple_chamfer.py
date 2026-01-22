#!/usr/bin/env python3
"""
SIMPLEST POSSIBLE approach - just cut corners with straight lines (chamfer)
No arc, no rotation, just two points per corner
This CANNOT go wrong!
"""
import numpy as np

def simple_chamfer_at_corner(corner, prev, next, r):
    """Create a simple 2-point chamfer - CANNOT FAIL"""
    c = np.array(corner)
    p = np.array(prev)
    n = np.array(next)
    
    # Vectors FROM corner TO neighbors (normalized)
    v1 = p - c
    v1 = v1 / np.linalg.norm(v1)
    
    v2 = n - c
    v2 = v2 / np.linalg.norm(v2)
    
    # Two points: one on the v1 direction, one on v2 direction
    pt1 = c + v1 * r
    pt2 = c + v2 * r
    
    return [tuple(pt1), tuple(pt2)]


def get_tab_points_simple(start_x, width, height, radius, direction=1):
    """Generate tab points with simple chamfer corners"""
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
    
    points = []
    points.append(p1)
    points.extend(simple_chamfer_at_corner(p2, p1, p3, r))
    points.extend(simple_chamfer_at_corner(p3, p2, p4, r))
    points.extend(simple_chamfer_at_corner(p4, p3, p5, r))
    points.extend(simple_chamfer_at_corner(p5, p4, p6, r))
    points.append(p6)
    
    return points

# Test
if __name__ == "__main__":
    pts = get_tab_points_simple(0, 20, 10, 2, 1)
    print(f"Generated {len(pts)} points")
    print("All points:")
    for i, p in enumerate(pts):
        print(f"  {i}: ({p[0]:.2f}, {p[1]:.2f})")
    
    # Check Y values
    y_vals = [p[1] for p in pts]
    print(f"\nY range: [{min(y_vals):.2f}, {max(y_vals):.2f}]")
    print(f"Expected: [0.00, 10.00]")
    
    # Test with direction=-1 (downward tab)
    pts_down = get_tab_points_simple(0, 20, 10, 2, -1)
    y_vals_down = [p[1] for p in pts_down]
    print(f"\nDownward tab Y range: [{min(y_vals_down):.2f}, {max(y_vals_down):.2f}]")
    print(f"Expected: [-10.00, 0.00]")
