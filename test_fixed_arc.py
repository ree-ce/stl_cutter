#!/usr/bin/env python3
"""
Fixed arc rotation with proper direction detection
"""
import numpy as np

def get_tab_points_fixed(start_x, width, height, radius, direction=1):
    """Generate tab points with CORRECT arc rotation"""
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
    
    def arc_at_corner(corner, prev, next, r, segments=5):
        """Create arc with CORRECT rotation direction"""
        c = np.array(corner)
        p = np.array(prev)
        n = np.array(next)
        
        # Vectors FROM corner TO neighbors
        v1 = p - c
        v1_len = np.linalg.norm(v1)
        v1 = v1 / v1_len
        
        v2 = n - c  
        v2_len = np.linalg.norm(v2)
        v2 = v2 / v2_len
        
        # Calculate angle between vectors
        dot = np.dot(v1, v2)
        angle = np.arccos(np.clip(dot, -1.0, 1.0))
        
        # CRITICAL: Determine rotation direction using cross product
        # In 2D: cross(v1, v2) = v1.x * v2.y - v1.y * v2.x
        cross = v1[0] * v2[1] - v1[1] * v2[0]
        
        # If cross > 0: counter-clockwise (CCW)
        # If cross < 0: clockwise (CW)
        # We want to rotate FROM v1 TO v2
        
        arc_points = []
        for i in range(segments + 1):
            t = i / segments
            theta = t * angle
            
            # Apply rotation in the CORRECT direction
            if cross >= 0:
                # Counter-clockwise rotation
                cos_t = np.cos(theta)
                sin_t = np.sin(theta)
            else:
                # Clockwise rotation (negative angle)
                cos_t = np.cos(-theta)
                sin_t = np.sin(-theta)
            
            # Rotation matrix applied to v1
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

# Test
if __name__ == "__main__":
    pts = get_tab_points_fixed(0, 20, 10, 2, 1)
    print(f"Generated {len(pts)} points")
    print("First 10 points:")
    for i, p in enumerate(pts[:10]):
        print(f"  {i}: ({p[0]:.2f}, {p[1]:.2f})")
    
    # Check that all Y values are reasonable
    y_vals = [p[1] for p in pts]
    print(f"\nY range: [{min(y_vals):.2f}, {max(y_vals):.2f}]")
    print(f"Expected: [0.00, 10.00]")
