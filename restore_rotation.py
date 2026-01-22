#!/usr/bin/env python3
import re

with open('core.py', 'r') as f:
    content = f.read()

# Swap back to the ORIGINAL condition (which had correct geometry)
new_function = '''        def get_tab_points(start_x, width, height, radius, direction=1):
            """Generate tab points with correct arc direction"""
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
                """Create arc"""
                c = np.array(corner)
                p = np.array(prev)
                n = np.array(next)
                
                v1 = p - c
                v1 = v1 / np.linalg.norm(v1)
                
                v2 = n - c  
                v2 = v2 / np.linalg.norm(v2)
                
                dot = np.dot(v1, v2)
                angle = np.arccos(np.clip(dot, -1.0, 1.0))
                
                cross = v1[0] * v2[1] - v1[1] * v2[0]
                
                arc_points = []
                for i in range(segments + 1):
                    t = i / segments
                    theta = t * angle
                    
                    # BACK TO ORIGINAL: cross >= 0 for positive rotation
                    if cross >= 0:
                        cos_t = np.cos(theta)
                        sin_t = np.sin(theta)
                    else:
                        cos_t = np.cos(-theta)
                        sin_t = np.sin(-theta)
                    
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
'''

pattern = r'(        def get_tab_points\(start_x, width, height, radius, direction=1\):.*?return points)'
content = re.sub(pattern, new_function.rstrip(), content, count=1, flags=re.DOTALL)

with open('core.py', 'w') as f:
    f.write(content)

print("Restored original rotation direction (cross >= 0)")
