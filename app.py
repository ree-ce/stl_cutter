import streamlit as st
import time
import matplotlib.pyplot as plt
import numpy as np
import io

# Import Core Logic
try:
    from core import DovetailSplitter, MeshError, ComplexityError
except ImportError:
    st.error("Failed to import core module. Please ensure core.py is in the same directory.")
    st.stop()

# 1. Page Config
st.set_page_config(
    page_title="Auto-Dovetail Splitter",
    page_icon="✂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Sidebar
with st.sidebar:
    st.title("🔧 Settings")
    
    st.markdown("### Printer Constraints")
    bed_size = st.number_input(
        "Printer Bed Size (mm)",
        min_value=100,
        max_value=1000,
        value=120,
        step=10,
        help="The maximum build volume size (X/Y) of your printer."
    )
    
    st.markdown("### Joint Configuration")
    tolerance = st.slider(
        "Joint Tolerance (mm)",
        min_value=0.05,
        max_value=0.5,
        value=0.2,
        step=0.05,
        help="Gap between male and female parts. Higher = looser fit."
    )
    
    col_sett_1, col_sett_2 = st.columns(2)
    with col_sett_1:
        tab_width = st.slider(
            "Tab Width (mm)",
            min_value=10,
            max_value=50,
            value=20,
            step=1,
            help="Total width of the puzzle tab at the base."
        )
        tab_height = st.slider(
            "Tab Height (mm)",
            min_value=5,
            max_value=30,
            value=10,
            step=1,
            help="Height of the puzzle tab."
        )
    with col_sett_2:
        num_tabs = st.slider(
            "Tabs per Arm",
            min_value=1,
            max_value=5,
            value=1,
            step=1,
            help="Number of tabs on each side."
        )
        tab_radius = st.slider(
            "Corner Radius (mm)",
            min_value=0.0,
            max_value=5.0,
            value=2.0,
            step=0.5,
            help="Fillet radius for tab corners."
        )
        safe_radius = st.slider(
            "Center Safe Zone (mm)",
            min_value=5.0,
            max_value=50.0,
            value=15.0,
            step=1.0,
            help="Radius of the flat center area. Reduction allows tabs closer to center."
        )
    
    st.info(f"Targeting: {bed_size}x{bed_size}mm Bed\nTolerance: {tolerance}mm")

# 3. Main Area
st.title("Auto-Dovetail Splitter ✂️")
st.markdown("""
    Upload a large STL file to automatically split it into 4 dovetail-jointed quadrants 
    compatible with smaller printers.
""")

uploaded_file = st.file_uploader("Upload STL File", type=['stl'])

@st.cache_data(show_spinner=False)
def load_and_preview(file_content, filename):
    try:
        splitter = DovetailSplitter(filename, file_content)
        splitter.validate_and_heal()
        return splitter
    except Exception as e:
        return str(e)

@st.cache_data(show_spinner=False)
def process_mesh(_splitter, t_width, t_height, t_radius, s_radius, n_tabs, tol):
    return _splitter.split_mesh(tab_width=t_width, tab_height=t_height, tab_radius=t_radius, safe_radius=s_radius, num_tabs=n_tabs, tolerance=tol)

if uploaded_file:
    # 3.1 Pre-computation / Preview
    
    # Initialize Splitter (Cached)
    # We read bytes once
    file_bytes = uploaded_file.getvalue()
    
    with st.spinner("Analyzing mesh..."):
        result = load_and_preview(file_bytes, uploaded_file.name)
        
    if isinstance(result, str):
        st.error(f"Error loading mesh: {result}")
    else:
        splitter = result
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📁 File Stats")
            st.write(f"**Filename:** `{uploaded_file.name}`")
            st.write(f"**Size:** `{uploaded_file.size / 1024 / 1024:.2f} MB`")
            
            bounds = splitter.mesh.bounds
            dims = bounds[1] - bounds[0]
            st.metric("Dimensions", f"{dims[0]:.1f} x {dims[1]:.1f} x {dims[2]:.1f} mm")
            st.metric("Volume", f"{splitter.mesh.volume / 1000:.2f} cm³")
            
            if dims[0] > (bed_size * 2) or dims[1] > (bed_size * 2):
                st.warning("⚠️ Object might be too large even after splitting!")

        with col2:
            st.subheader("📐 Cut Preview")
            
            # Generate Real Path for Preview
            try:
                # Use a slightly larger bbox for the plot to show the full cut
                # Check for potential scaling to warn user
                # Each quadrant is half the mesh dimension
                quadrant_x = dims[0] / 2
                quadrant_y = dims[1] / 2
                mesh_arm_len = (min(quadrant_x, quadrant_y)) - safe_radius
                req_width = num_tabs * tab_width
                if req_width > mesh_arm_len and mesh_arm_len > 0:
                    st.warning(f"⚠️ **Space Constraint**: Tabs are too wide for the available arm space ({mesh_arm_len:.1f}mm). They have been automatically scaled down to fit.")
                
                max_dim = max(dims[0], dims[1])
                full_len = max_dim * 1.5
                
                # Generate paths for QUADRANT size, not full mesh size
                path_x = splitter.generate_smart_path(quadrant_x, full_len, tab_width, tab_height, tab_radius, safe_radius, num_tabs, tolerance, 'x')
                path_y = splitter.generate_smart_path(quadrant_y, full_len, tab_width, tab_height, tab_radius, safe_radius, num_tabs, tolerance, 'y')
                
                fig, ax = plt.subplots(figsize=(4, 4))
                
                # Plot Bounding Box of Mesh
                # The paths are generated relative to the mesh's origin, so the bounding box should also be relative.
                # The original code used bounds[0][0], bounds[0][1] as the bottom-left corner.
                # The instruction's suggested coordinates (-dims[0]/2, -dims[1]/2) would center the box at (0,0).
                # To maintain alignment with the generated paths, we keep the original bottom-left corner.
                # ax.add_patch(plt.Rectangle((bounds[0][0], bounds[0][1]), dims[0], dims[1], 
                #                      fill=False, edgecolor='gray', linestyle='--', linewidth=1, label='Mesh Bounds'))
                
                # Plot Cuts
                # Shapely to plotting
                x_coords, y_coords = path_x.xy
                ax.plot(x_coords, y_coords, color='red', alpha=0.8, label='Cut X')
                
                x_coords, y_coords = path_y.xy
                ax.plot(x_coords, y_coords, color='blue', alpha=0.8, label='Cut Y')
                
                
                ax.set_aspect('equal')
                ax.set_xlim(-max_dim*0.6, max_dim*0.6)
                ax.set_ylim(-max_dim*0.6, max_dim*0.6)
                ax.grid(True, alpha=0.3)
                ax.axhline(y=0, color='k', linewidth=0.5, alpha=0.3)
                ax.axvline(x=0, color='k', linewidth=0.5, alpha=0.3)
                ax.legend()
                st.pyplot(fig)
                
            except Exception as e:
                st.error(f"Preview Error: {e}")

        # 4. Action Area
        st.divider()
        
        if st.button("✂️ Slice & Generate", type="primary", use_container_width=True):
            status_container = st.status("Processing...", expanded=True)
            
            try:
                with status_container:
                    st.write("⚙️ Performing boolean cuts (This may take a minute)...")
                    start_time = time.time()
                    
                    # Heavy Lifting
                    parts = process_mesh(splitter, tab_width, tab_height, tab_radius, safe_radius, num_tabs, tolerance)
                    
                    st.write(f"✅ Boolean operations complete ({time.time() - start_time:.1f}s)")
                    st.write(f"🧩 Generated {len(parts)} parts.")
                    
                    st.write("📦 Zipping files...")
                    zip_data = splitter.pack_zip(parts)
                    
                    status_container.update(label="Processing Complete!", state="complete", expanded=False)
                
                st.success("Slicing complete! Download your parts below.")
                
                st.download_button(
                    label="⬇️ Download ZIP",
                    data=zip_data,
                    file_name=f"split_{uploaded_file.name}.zip",
                    mime="application/zip"
                )
                
            except Exception as e:
                status_container.update(label="Failed", state="error")
                st.error(f"Processing Failed: {str(e)}")

else:
    st.info("👆 Upload an STL file to get started.")
