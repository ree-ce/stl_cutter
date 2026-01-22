#!/usr/bin/env python3
# Simple chamfer-based rounding for tabs

def get_tab_points_chamfer(start_x, width, height, radius, direction=1):
    """Generate tab points with simple chamfer at corners"""
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
    
    # Simple chamfer: just cut the corners
    # For each sharp corner, replace it with 2 points (a small chamfer)
    r = min(radius, width/10.0, abs(height)/5.0)
    
    def chamfer_point(corner, prev, next, r):
        """Create a simple 2-point chamfer"""
        import numpy as np
        c = np.array(corner)
        p = np.array(prev)
        n = np.array(next)
        
        v1 = p - c
        v1 = v1 / np.linalg.norm(v1)
        v2 = n - c  
        v2 = v2 / np.linalg.norm(v2)
        
        pt1 = c + v1 * r
        pt2 = c + v2 * r
        return [tuple(pt1), tuple(pt2)]
    
    points = []
    points.append(p1)
    points.extend(chamfer_point(p2, p1, p3, r))
    points.extend(chamfer_point(p3, p2, p4, r))
    points.extend(chamfer_point(p4, p3, p5, r))
    points.extend(chamfer_point(p5, p4, p6, r))
    points.append(p6)
    
    return points

# Test
if __name__ == "__main__":
    pts = get_tab_points_chamfer(0, 20, 10, 2, 1)
    print(f"Generated {len(pts)} points:")
    for i, p in enumerate(pts):
        print(f"  {i}: ({p[0]:.2f}, {p[1]:.2f})")
