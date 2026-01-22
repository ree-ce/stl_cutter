#!/usr/bin/env python3
"""
Debug the arc rotation algorithm
Test each corner individually to see where the distortion occurs
"""
import numpy as np
import matplotlib.pyplot as plt

def test_arc_rotation():
    """Test the arc generation for a single corner"""
    
    # Test case: corner at p2 (neck start)
    # Coming from p1 (left base) going to p3 (head top left)
    
    # Simple test geometry
    p1 = np.array([0.0, 0.0])
    p2 = np.array([4.0, 0.0])  # Corner
    p3 = np.array([3.0, 8.0])
    
    r = 2.0
    
    # Vectors FROM corner TO neighbors
    v1 = p1 - p2  # Should point LEFT
    v2 = p3 - p2  # Should point UP-LEFT
    
    print(f"p1 (prev): {p1}")
    print(f"p2 (corner): {p2}")
    print(f"p3 (next): {p3}")
    print(f"v1 (to prev): {v1}")
    print(f"v2 (to next): {v2}")
    
    # Normalize
    v1 = v1 / np.linalg.norm(v1)
    v2 = v2 / np.linalg.norm(v2)
    
    print(f"v1 normalized: {v1}")
    print(f"v2 normalized: {v2}")
    
    # Calculate angle
    dot = np.dot(v1, v2)
    angle = np.arccos(np.clip(dot, -1.0, 1.0))
    
    print(f"Dot product: {dot}")
    print(f"Angle (radians): {angle}")
    print(f"Angle (degrees): {np.degrees(angle)}")
    
    # Generate arc points
    arc_points = []
    segments = 5
    
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
        
        point = p2 + rotated * r
        arc_points.append(point)
        print(f"  t={t:.2f}, theta={np.degrees(theta):.1f}°, point={point}")
    
    # Plot
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Original points
    ax.plot([p1[0], p2[0], p3[0]], [p1[1], p2[1], p3[1]], 'ro-', label='Original', markersize=10)
    
    # Arc points
    arc_x = [p[0] for p in arc_points]
    arc_y = [p[1] for p in arc_points]
    ax.plot(arc_x, arc_y, 'b*-', label='Arc', markersize=8)
    
    # Vectors
    ax.arrow(p2[0], p2[1], v1[0]*r, v1[1]*r, head_width=0.3, color='green', alpha=0.5, label='v1')
    ax.arrow(p2[0], p2[1], v2[0]*r, v2[1]*r, head_width=0.3, color='orange', alpha=0.5, label='v2')
    
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.set_title('Arc Rotation Test')
    plt.savefig('arc_debug.png', dpi=150)
    print("\nSaved plot to arc_debug.png")

if __name__ == "__main__":
    test_arc_rotation()
