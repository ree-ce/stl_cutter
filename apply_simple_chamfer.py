#!/usr/bin/env python3
import re

with open('core.py', 'r') as f:
    content = f.read()

# Simple, reliable 2-point chamfer function
new_function = '''        def get_tab_points(start_x, width, height, radius, direction=1):
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
            
            def chamfer_corner(corner, prev, next, r):
                """Simple 2-point chamfer"""
                c = np.array(corner)
                v1 = np.array(prev) - c
                v1 = v1 / np.linalg.norm(v1)
                v2 = np.array(next) - c
                v2 = v2 / np.linalg.norm(v2)
                pt1 = c + v1 * r
                pt2 = c + v2 * r
                return [tuple(pt1), tuple(pt2)]
            
            points = []
            points.append(p1)
            points.extend(chamfer_corner(p2, p1, p3, r))
            points.extend(chamfer_corner(p3, p2, p4, r))
            points.extend(chamfer_corner(p4, p3, p5, r))
            points.extend(chamfer_corner(p5, p4, p6, r))
            points.append(p6)
            
            return points
'''

# Replace
pattern = r'(        def get_tab_points\(start_x, width, height, radius, direction=1\):.*?return points)'
content = re.sub(pattern, new_function.rstrip(), content, count=1, flags=re.DOTALL)

with open('core.py', 'w') as f:
    f.write(content)

print("Applied simple chamfer solution")
