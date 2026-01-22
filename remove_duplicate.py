#!/usr/bin/env python3
"""
Remove the duplicate old get_tab_points function starting at line 325
"""

with open('core.py', 'r') as f:
    lines = f.readlines()

# Find the second def get_tab_points (around line 325)
# and remove it until we find the start of the next section

in_duplicate = False
start_line = None
end_line = None

for i, line in enumerate(lines):
    if i > 200 and 'def get_tab_points(start_x' in line:
        # Found the duplicate
        start_line = i
        in_duplicate = True
        print(f"Found duplicate at line {i+1}")
    
    if in_duplicate and '# --- Generate Left Arm' in line:
        # Found the end of the duplicate function
        end_line = i
        print(f"Duplicate ends at line {i+1}")
        break

if start_line and end_line:
    # Remove lines from start_line to end_line-1
    new_lines = lines[:start_line] + lines[end_line:]
    
    with open('core.py', 'w') as f:
        f.writelines(new_lines)
    
    print(f"Removed {end_line - start_line} lines of duplicate code")
else:
    print("Could not find duplicate boundaries")
