
import matplotlib.pyplot as plt
from core import DovetailSplitter
import trimesh

def verify_distribution():
    # Load the specific file
    try:
        with open("plate_mini.stl", "rb") as f:
            content = f.read()
        splitter = DovetailSplitter("plate_mini.stl", content)
    except Exception as e:
        print(f"Failed to load mesh: {e}")
        return

    
    mesh_width_x = splitter.mesh.extents[0]
    quadrant_x = mesh_width_x / 2  # THIS IS THE FIX!
    full_width = mesh_width_x * 1.5
    
    print(f"Full Mesh Width X: {mesh_width_x}")
    print(f"Quadrant Width (88mm): {quadrant_x}")
    print(f"Safe Radius: 15")
    print(f"Available Arm Length: {quadrant_x - 15}")
    
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    
    counts = [1, 2, 3]
    for i, n_tabs in enumerate(counts):
        ax = axes[i]
        path_x = splitter.generate_smart_path(
            mesh_length=quadrant_x,  # CORRECTED: Use quadrant size
            total_length=full_width,
            tab_width=20,
            tab_height=10,
            tab_radius=2,
            safe_radius=15,
            num_tabs_per_arm=n_tabs,
            tolerance=0.2,
            axis='x'
        )
        x, y = path_x.xy
        ax.plot(x, y, label=f'{n_tabs} Tabs', color='blue', linewidth=2)
        
        # Draw QUADRANT Bounds (not full mesh)
        ax.add_patch(plt.Rectangle((-quadrant_x, -50), quadrant_x*2, 100, 
                                   fill=False, edgecolor='green', linestyle='--', linewidth=2, label='Quadrant Bounds (88mm each side)'))
        
        # Draw Center Line (where we cut)
        ax.axvline(x=0, color='red', linestyle='-', linewidth=2, alpha=0.7, label='Cut Line (Center)')
        
        # Draw Safe Zone
        ax.axvline(x=-15, color='orange', linestyle=':', linewidth=1.5, alpha=0.7)
        ax.axvline(x=15, color='orange', linestyle=':', linewidth=1.5, alpha=0.7, label='Safe Zone')
        
        ax.set_aspect('equal')
        ax.legend(loc='upper right')
        ax.set_title(f"Configuration: {n_tabs} Tabs per arm (Width=20mm, Quadrant={quadrant_x:.0f}mm)")
        ax.grid(True, alpha=0.3)
        
        # Calculate Gap
        arm_len = quadrant_x - 15
        total_tab = n_tabs * 20
        gap = (arm_len - total_tab) / (n_tabs + 1)
        ax.text(-quadrant_x + 5, -40, f"Arm Length: {arm_len:.1f}mm | Gap: {gap:.2f}mm", fontsize=9)

    plt.suptitle(f"CORRECTED Distribution: Tabs on 88mm Quadrants (not 176mm full mesh)", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig("verification_corrected.png", dpi=150)
    print("Plot saved to verification_corrected.png")

if __name__ == "__main__":
    verify_distribution()
