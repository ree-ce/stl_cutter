#!/usr/bin/env python3
"""
Complete tab with proper fillet arcs
"""
import numpy as np

def fillet_at_corner(corner, prev, next, r, segments=5):
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
    
    pt1 = c + v1_unit * tan_dist
    pt2 = c + v2_unit * tan_dist
    
    bisector = v1_unit + v2_unit
    bisector = bisector / np.linalg.norm(bisector)
    
    center_dist = r_effective / np.sin(half_angle)
    arc_center = c + bisector * center_dist
    
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


def get_tab_points_with_fillet(start_x, width, height, radius, direction=1):
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
    
    points = []
    points.append(p1)
    points.extend(fillet_at_corner(p2, p1, p3, r, segments=5))
    points.extend(fillet_at_corner(p3, p2, p4, r, segments=5))
    points.extend(fillet_at_corner(p4, p3, p5, r, segments=5))
    points.extend(fillet_at_corner(p5, p4, p6, r, segments=5))
    points.append(p6)
    
    return points

# Test
if __name__ == "__main__":
    # Test upward tab
    pts_up = get_tab_points_with_fillet(0, 20, 10, 2, 1)
    y_up = [p[1] for p in pts_up]
    print(f"Upward tab: {len(pts_up)} points, Y range: [{min(y_up):.2f}, {max(y_up):.2f}]")
    print(f"Expected: [0.00, 10.00], Test: {'PASS' if min(y_up) >= -0.01 and max(y_up) <= 10.01 else 'FAIL'}")
    
    # Test downward tab
    pts_down = get_tab_points_with_fillet(0, 20, 10, 2, -1)
    y_down = [p[1] for p in pts_down]
    print(f"Downward tab: {len(pts_down)} points, Y range: [{min(y_down):.2f}, {max(y_down):.2f}]")
    print(f"Expected: [-10.00, 0.00], Test: {'PASS' if min(y_down) >= -10.01 and max(y_down) <= 0.01 else 'FAIL'}")
