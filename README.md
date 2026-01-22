# Auto-Dovetail Splitter ✂️

A Streamlit application for automatically splitting large 3D models into printable pieces with dovetail joints.

## 🚀 Quick Start

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### Deploy to Streamlit Cloud
1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io/)
3. Create new app with:
   - Repository: `your-username/stl_cutter`
   - Branch: `master`
   - Main file: `app.py`

## 📁 Project Structure

```
.
├── app.py                 # Main Streamlit application
├── core.py               # Core dovetail splitting logic
├── requirements.txt      # Python dependencies
├── docs/                 # Documentation
├── tests/                # Test files
├── scripts/              # Development scripts
│   └── debug/           # Debug and development helpers
└── assets/              # Static assets
    ├── images/          # Plots, verification images
    └── samples/         # Sample STL files
```

## 🔧 Features

- **Quadrant Distribution**: Correctly distributes tabs across each quadrant (not full mesh)
- **Proper Fillet Arcs**: Smooth, printable corner radius using geometric fillet algorithm
- **Auto-Scaling**: Automatically adjusts tab width if space is limited
- **Preview**: Real-time 2D preview of cutting paths
- **Customizable**: Control tab count, size, corner radius, and safe zone

## 📝 Parameters

- **Printer Bed Size**: Target size for split pieces
- **Joint Tolerance**: Gap between parts (default: 0.2mm)
- **Tab Width/Height**: Puzzle tab dimensions
- **Tabs per Arm**: Number of tabs on each side
- **Corner Radius**: Fillet radius for smooth corners
- **Center Safe Zone**: Minimum distance from center intersection

## 🧪 Testing

```bash
# Run tests
python tests/test_core.py
```

## 📄 License

MIT
