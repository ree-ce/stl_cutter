# Project Specification: Auto-Dovetail Splitter for Streamlit

## 1. Project Overview
* **Objective:** Create a browser-based tool allowing users to upload large STL files (e.g., 300x300mm) and automatically split them into 4 printable quadrants using interlocking "Dovetail" (puzzle) joints.
* **Target Environment:** Streamlit Community Cloud (Linux environment, constrained RAM ~1GB).
* **Primary Use Case:** Users with small FDM printers (e.g., A1 Mini, Prusa Mini) need to print large objects without using glue for assembly.

## 2. Success Conditions (Definition of Done)
The project is considered complete ONLY when all the following criteria are met:

### 2.1 Functional Success
* [ ] **The "Fit" Test:** The output STL parts, when aligned in a CAD viewer, must have a visible, consistent gap of exactly `tolerance` (default 0.2mm) between the male and female joints. Zero-gap cuts are a FAILURE.
* [ ] **The "Lock" Test:** The generated joint must be a geometric Dovetail (trapezoidal), restricting movement to the Z-axis only. Simple sine waves or straight cuts are a FAILURE.
* [ ] **The Workflow:** A user can Upload -> Preview Path -> Download ZIP without the app crashing or timing out (under 60 seconds for a standard 20MB mesh).

### 2.2 Reliability Success
* [ ] **Memory Safety:** The app must not crash with "Out of Memory" errors on Streamlit Cloud. Large mesh objects must be explicitly deleted from memory after processing.
* [ ] **Error Handling:** Uploading a non-watertight or "garbage" STL file must trigger a polite UI error message, not a Python traceback/crash.

## 3. Functional Requirements

### 3.1 Input & Pre-processing
* **Input:** Single `.stl` file (Binary or ASCII).
* **Auto-Normalization (Critical):**
    * Before processing, translate the mesh Bounding Box Center (X,Y) to (0,0).
    * Translate the mesh Minimum Z to 0.
* **Validation:**
    * Check `mesh.is_watertight`. If False, run `mesh.repair()`. If still False, **STOP** and return `MeshError`.
    * **Complexity Guard:** Slice mesh at Z-midpoint. If the 2D cross-section contains > 10 disjoint polygons, **STOP** and return `ComplexityError` (to prevent boolean operations from hanging).

### 3.2 Core Logic: Dovetail Generation
* **Path Geometry:**
    * Generate a 2D Trapezoidal Wave along the X-axis and Y-axis.
    * **Constraint:** The "Neck" (narrowest part) of the dovetail must be > 3.0mm to prevent breakage during printing.
    * **Constraint:** The angle should be approx 75 degrees relative to the cutting line.
* **Tolerance Handling (The Kerf):**
    * The cut cannot be a single line. It must be a "Volume".
    * Create a "Cutter Mask" by extruding the 2D path.
    * **Offset Logic:** The Male part must be smaller than the Female slot by `tolerance` mm. (e.g., Apply a negative buffer to the male part or a positive buffer to the cutter).

### 3.3 Output Generation
* Perform Boolean operations to create 4 quadrants: Top-Left, Top-Right, Bottom-Left, Bottom-Right.
* **Sanitization:** Remove any disconnected debris (floating artifacts) smaller than 1% of the part volume.
* **File format:** Binary STL.
* **Packaging:** Compress all 4 STLs into a single ZIP file in memory.

## 4. UI/UX Specifications (Streamlit)

### 4.1 Sidebar Layout
* **Title:** "🔧 Settings"
* **Input:** `Printer Bed Size (mm)` (Default: 180).
* **Slider:** `Joint Tolerance` (0.05mm - 0.5mm, Default: 0.2mm, Step: 0.05).
* **Slider:** `Dovetail Scale` (10mm - 40mm, Default: 15mm). controls the size of the puzzle tabs.

### 4.2 Main Interface
* **Header:** Title and brief instructions.
* **Uploader:** `st.file_uploader` (Label: "Upload STL").
* **Pre-Computation Preview:**
    * IMMEDIATELY after upload, display the file stats (Dimensions).
    * Show a **2D Matplotlib Plot** of the *proposed* cutting path overlaid on the mesh bounding box. *Do not wait for the boolean operation to show this.*
* **Action:** Big "✂️ Slice & Generate" button.
* **Feedback:** Use `st.spinner` with text updating the user on the stage (e.g., "Repairing mesh...", "Calculating booleans...", "Zipping files...").
* **Result:** `st.download_button` for the final ZIP.

## 5. Technical Constraints
* **Statelessness:** Use `io.BytesIO` for ALL file operations. No `open('file.stl', 'w')`.
* **Dependencies:** `streamlit`, `trimesh`, `shapely`, `numpy`, `scipy`, `matplotlib`, `rtree`.
* **Performance:** Cache the expensive `generate_parts` function using `@st.cache_data`.