#!/usr/bin/env python3
import re

with open('core.py', 'r') as f:
    content = f.read()

# The new smooth arc function
new_function = '''        def get_tab_points(start_x, width, height, radius, direction=1):
            """Generate tab points with smooth multi-segment arc at corners"""
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
            
            # Create smooth arc with multiple segments
            r = min(radius, width/10.0, abs(height)/5.0)
            
            def arc_at_corner(corner, prev, next, r, segments=5):
                """Create a smooth circular arc at the corner"""
                c = np.array(corner)
                p = np.array(prev)
                n = np.array(next)
                
                # Vectors from corner to prev and next
                v1 = p - c
                v1 = v1 / np.linalg.norm(v1)
                v2 = n - c  
                v2 = v2 / np.linalg.norm(v2)
                
                # Arc start and end points
                start_pt = c + v1 * r
                end_pt = c + v2 * r
                
                # Calculate angle between vectors
                dot = np.dot(v1, v2)
                angle = np.arccos(np.clip(dot, -1.0, 1.0))
                
                # Generate arc points
                arc_points = []
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

# Find and replace the FIRST get_tab_points function
pattern = r'(        def get_tab_points\(start_x, width, height, radius, direction=1\):.*?return points)'

content = re.sub(pattern, new_function.rstrip(), content, count=1, flags=re.DOTALL)

with open('core.py', 'w') as f:
    f.write(content)

print("Applied smooth 5-segment arc")
