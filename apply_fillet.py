#!/usr/bin/env python3
import re

with open('core.py', 'r') as f:
    content = f.read()

# The WORKING fillet implementation
new_function = '''        def get_tab_points(start_x, width, height, radius, direction=1):
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
            
            def fillet_corner(corner, prev, next, r, segments=5):
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
                
                bisector = v1_unit + v2_unit
                bisector = bisector / np.linalg.norm(bisector)
                
                center_dist = r_effective / np.sin(half_angle)
                arc_center = c + bisector * center_dist
                
                pt1 = c + v1_unit * tan_dist
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
            
            points = []
            points.append(p1)
            points.extend(fillet_corner(p2, p1, p3, r, segments=5))
            points.extend(fillet_corner(p3, p2, p4, r, segments=5))
            points.extend(fillet_corner(p4, p3, p5, r, segments=5))
            points.extend(fillet_corner(p5, p4, p6, r, segments=5))
            points.append(p6)
            
            return points
'''

# Replace
pattern = r'(        def get_tab_points\(start_x, width, height, radius, direction=1\):.*?return points)'
content = re.sub(pattern, new_function.rstrip(), content, count=1, flags=re.DOTALL)

with open('core.py', 'w') as f:
    f.write(content)

print("Applied proper fillet implementation to core.py")
