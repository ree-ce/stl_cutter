#!/usr/bin/env python3
"""
The arc is going INWARD instead of OUTWARD
We need to reverse the arc direction
"""
import numpy as np

def get_tab_points_correct_direction(start_x, width, height, radius, direction=1):
    """Generate tab points with arc going OUTWARD from the tab"""
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
        """Create arc - but we want it to bulge OUTWARD, not inward"""
        c = np.array(corner)
        p = np.array(prev)
        n = np.array(next)
        
        # Vectors FROM corner TO neighbors
        v1 = p - c
        v1 = v1 / np.linalg.norm(v1)
        
        v2 = n - c  
        v2 = v2 / np.linalg.norm(v2)
        
        # The arc should bulge AWAY from the interior angle
        # We need to rotate in the OPPOSITE direction
        
        dot = np.dot(v1, v2)
        angle = np.arccos(np.clip(dot, -1.0, 1.0))
        
        # Cross product to determine which way is "outward"
        cross = v1[0] * v2[1] - v1[1] * v2[0]
        
        arc_points = []
        for i in range(segments + 1):
            t = i / segments
            theta = t * angle
            
            # REVERSE the rotation direction!
            if cross >= 0:
                # Was CCW, now CW
                cos_t = np.cos(-theta)
                sin_t = np.sin(-theta)
            else:
                # Was CW, now CCW
                cos_t = np.cos(theta)
                sin_t = np.sin(theta)
            
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
    pts = get_tab_points_correct_direction(0, 20, 10, 2, 1)
    print(f"Generated {len(pts)} points")
    
    # Check a few key points
    print("\nKey points:")
    print(f"  p1 (start): {pts[0]}")
    print(f"  First arc point: {pts[1]}")
    print(f"  Last point: {pts[-1]}")
    
    # The arc at p2 should bulge OUTWARD (negative Y for upward tab)
    print(f"\nArc at p2 (should bulge out):")
    for i in range(1, 7):
        print(f"    {pts[i]}")
