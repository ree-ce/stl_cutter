#!/usr/bin/env python3
"""
CORRECT fillet arc implementation using proper geometry:
- Arc center is along the angle bisector
- Arc is tangent to both edges
- Arc radius equals the fillet radius parameter
"""
import numpy as np
import matplotlib.pyplot as plt

def fillet_at_corner(corner, prev, next, r, segments=5):
    """
    Create a proper fillet arc that is tangent to both edges.
    
    The fillet arc:
    - Starts at a point on the edge toward prev
    - Ends at a point on the edge toward next
    - Is tangent to both edges
    - Has the specified radius r
    """
    c = np.array(corner)
    p_prev = np.array(prev)
    p_next = np.array(next)
    
    # Vectors FROM corner TO neighbors (normalized)
    v1 = p_prev - c
    v1_len = np.linalg.norm(v1)
    v1_unit = v1 / v1_len
    
    v2 = p_next - c
    v2_len = np.linalg.norm(v2)
    v2_unit = v2 / v2_len
    
    # Calculate the angle between the edges
    dot = np.dot(v1_unit, v2_unit)
    angle = np.arccos(np.clip(dot, -1.0, 1.0))
    half_angle = angle / 2
    
    # Safety check: if angle is too small or too large
    if half_angle < 0.1 or half_angle > np.pi - 0.1:
        # Just return the corner point
        return [corner]
    
    # Distance from corner to tangent point on each edge
    tan_dist = r / np.tan(half_angle)
    
    # Limit the distance to avoid going past the edge midpoint
    tan_dist = min(tan_dist, v1_len * 0.4, v2_len * 0.4)
    
    # Recalculate r based on limited tan_dist
    r_effective = tan_dist * np.tan(half_angle)
    
    # Tangent points (where arc touches the edges)
    pt1 = c + v1_unit * tan_dist
    pt2 = c + v2_unit * tan_dist
    
    # Bisector direction (points INTO the corner angle)
    bisector = v1_unit + v2_unit
    bisector = bisector / np.linalg.norm(bisector)
    
    # Distance from corner to arc center
    center_dist = r_effective / np.sin(half_angle)
    
    # Arc center
    arc_center = c + bisector * center_dist
    
    # Generate arc points from pt1 to pt2 around the arc center
    # Calculate start and end angles
    start_vec = pt1 - arc_center
    end_vec = pt2 - arc_center
    
    start_angle = np.arctan2(start_vec[1], start_vec[0])
    end_angle = np.arctan2(end_vec[1], end_vec[0])
    
    # Determine arc direction: we want the shorter arc
    # The arc should go AWAY from the corner (on the outside)
    
    # Cross product of bisector with v1 tells us the orientation
    cross_b_v1 = bisector[0] * v1_unit[1] - bisector[1] * v1_unit[0]
    
    # Normalize angle difference
    angle_diff = end_angle - start_angle
    
    # We want to go the "short way" which is π - angle (the exterior angle of the fillet)
    # The arc sweep should be π - angle (exterior angle)
    arc_sweep = np.pi - angle
    
    if cross_b_v1 > 0:
        # CCW direction
        angles = [start_angle + t * arc_sweep for t in np.linspace(0, 1, segments + 1)]
    else:
        # CW direction
        angles = [start_angle - t * arc_sweep for t in np.linspace(0, 1, segments + 1)]
    
    # Generate points
    arc_points = []
    for theta in angles:
        point = arc_center + r_effective * np.array([np.cos(theta), np.sin(theta)])
        arc_points.append(tuple(point))
    
    return arc_points


def test_fillet():
    """Test the fillet on a simple corner"""
    # Test corner: p1=(0,0), corner=(4,0), p3=(3,10)
    corner = (4.0, 0.0)
    prev = (0.0, 0.0)
    next = (3.0, 10.0)
    r = 1.5
    
    arc = fillet_at_corner(corner, prev, next, r, segments=8)
    
    print(f"Fillet at corner {corner}:")
    print(f"Arc has {len(arc)} points")
    for i, p in enumerate(arc):
        print(f"  {i}: ({p[0]:.3f}, {p[1]:.3f})")
    
    # Check: all points should have Y >= 0 for this geometry
    y_vals = [p[1] for p in arc]
    print(f"\nY range: [{min(y_vals):.3f}, {max(y_vals):.3f}]")
    print(f"All Y >= 0? {all(y >= -0.001 for y in y_vals)}")
    
    # Plot
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Original lines
    ax.plot([prev[0], corner[0], next[0]], [prev[1], corner[1], next[1]], 'r.-', 
            label='Original edges', markersize=12, linewidth=2)
    
    # Arc
    arc_x = [p[0] for p in arc]
    arc_y = [p[1] for p in arc]
    ax.plot(arc_x, arc_y, 'b.-', label='Fillet arc', markersize=8, linewidth=2)
    
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.set_title('Proper Fillet Arc Test')
    plt.savefig('fillet_test.png', dpi=150)
    print("\nSaved to fillet_test.png")
    
    return all(y >= -0.001 for y in y_vals)

if __name__ == "__main__":
    success = test_fillet()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
