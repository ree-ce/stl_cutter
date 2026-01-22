#!/usr/bin/env python3
"""
Proper fillet arc generation using correct geometric approach:
1. Find the bisector of the angle
2. Calculate arc center along bisector
3. Generate arc points around that center
"""
import numpy as np
import matplotlib.pyplot as plt

def proper_arc_at_corner(corner, prev, next, r, segments=5):
    """Create a proper fillet arc using correct geometry"""
    c = np.array(corner)
    p_prev = np.array(prev)
    p_next = np.array(next)
    
    # Vectors FROM corner TO neighbors
    v1 = p_prev - c
    v1_len = np.linalg.norm(v1)
    v1_unit = v1 / v1_len
    
    v2 = p_next - c
    v2_len = np.linalg.norm(v2)
    v2_unit = v2 / v2_len
    
    # Calculate half angle between vectors
    dot = np.dot(v1_unit, v2_unit)
    angle = np.arccos(np.clip(dot, -1.0, 1.0))
    half_angle = angle / 2
    
    # Bisector direction (normalized)
    bisector = v1_unit + v2_unit
    bisector_len = np.linalg.norm(bisector)
    if bisector_len < 1e-6:
        # Vectors are opposite, no fillet possible
        return [corner]
    bisector = bisector / bisector_len
    
    # Distance from corner to arc center
    # d = r / sin(half_angle)
    sin_half = np.sin(half_angle)
    if sin_half < 1e-6:
        # Nearly straight line, no fillet needed
        return [corner]
    
    d = r / sin_half
    
    # Arc center
    arc_center = c + bisector * d
    
    # Arc start and end points
    arc_start = c + v1_unit * (r / np.tan(half_angle))
    arc_end = c + v2_unit * (r / np.tan(half_angle))
    
    # Angles from arc center to start/end
    start_vec = arc_start - arc_center
    end_vec = arc_end - arc_center
    
    start_angle = np.arctan2(start_vec[1], start_vec[0])
    end_angle = np.arctan2(end_vec[1], end_vec[0])
    
    # Determine the correct direction (shorter arc)
    # We want the arc on the "outside" of the corner
    cross = v1_unit[0] * v2_unit[1] - v1_unit[1] * v2_unit[0]
    
    # Adjust angles for correct arc direction
    if cross < 0:
        # Clockwise
        if end_angle > start_angle:
            end_angle -= 2 * np.pi
    else:
        # Counter-clockwise
        if end_angle < start_angle:
            end_angle += 2 * np.pi
    
    # Generate arc points
    arc_points = []
    for i in range(segments + 1):
        t = i / segments
        theta = start_angle + t * (end_angle - start_angle)
        point = arc_center + r * np.array([np.cos(theta), np.sin(theta)])
        arc_points.append(tuple(point))
    
    return arc_points


def test_arc():
    # Test with a simple tab corner
    # p1 = (0, 0), p2 = (4, 0), p3 = (3, 10)
    corner = (4.0, 0.0)
    prev = (0.0, 0.0)
    next = (3.0, 10.0)
    r = 2.0
    
    arc = proper_arc_at_corner(corner, prev, next, r, segments=10)
    
    print(f"Corner: {corner}")
    print(f"Arc points ({len(arc)} points):")
    for i, p in enumerate(arc):
        print(f"  {i}: ({p[0]:.2f}, {p[1]:.2f})")
    
    # Plot
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Original lines
    ax.plot([prev[0], corner[0], next[0]], [prev[1], corner[1], next[1]], 'r.-', label='Original', markersize=10)
    
    # Arc
    arc_x = [p[0] for p in arc]
    arc_y = [p[1] for p in arc]
    ax.plot(arc_x, arc_y, 'b.-', label='Arc', markersize=6)
    
    ax.set_aspect('equal')
    ax.grid(True)
    ax.legend()
    ax.set_title('Proper Fillet Arc Test')
    plt.savefig('proper_arc_test.png', dpi=150)
    print("\nSaved to proper_arc_test.png")

if __name__ == "__main__":
    test_arc()
