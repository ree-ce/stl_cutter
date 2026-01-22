
import trimesh
import numpy as np
import io
import unittest
import os
from core import DovetailSplitter

class TestDovetailSplitter(unittest.TestCase):
    def setUp(self):
        # Create a simple 100x100x20mm box
        self.mesh = trimesh.creation.box(extents=[100, 100, 20])
        # Move it so it's not perfectly centered, to test auto-centering
        self.mesh.apply_translation([10, 10, 0])
        
        # Save to bytes
        self.stl_bytes = trimesh.exchange.stl.export_stl(self.mesh)
        self.splitter = DovetailSplitter("test_cube.stl", self.stl_bytes)

    def test_normalization(self):
        print("\nTesting Normalization...")
        self.splitter.validate_and_heal()
        
        center = self.splitter.mesh.bounds.mean(axis=0)
        min_z = self.splitter.mesh.bounds[0][2]
        
        # Check X,Y centered (allow small float error)
        self.assertTrue(np.abs(center[0]) < 1e-5)
        self.assertTrue(np.abs(center[1]) < 1e-5)
        # Check Z min is 0
        self.assertTrue(np.abs(min_z) < 1e-5)
        print("Normalization PASSED")

    def test_path_generation(self):
        print("\nTesting Smart Path Generation...")
        # New API: ... tab_radius, safe_radius, num_tabs ...
        path = self.splitter.generate_smart_path(100, 150, 20, 10, 2.0, 15, 1, 0.2, 'x')
        self.assertTrue(path.is_valid)
        print("Smart Path Generation PASSED")

    def test_splitting(self):
        print("\nTesting Splitting (This may take a moment)...")
        self.splitter.validate_and_heal()
        # Use new parameters
        parts = self.splitter.split_mesh(tab_width=20, tab_height=10, tab_radius=2, safe_radius=15, num_tabs=1, tolerance=0.2)
        
        print(f"Generated {len(parts)} parts.")
        self.assertEqual(len(parts), 4)
        
        for name, mesh in parts.items():
            self.assertTrue(mesh.is_watertight)
            print(f"  - {name}: Vol={mesh.volume:.2f}, Watertight={mesh.is_watertight}")
            
        print("Splitting PASSED")

    def test_zip_packaging(self):
        print("\nTesting ZIP Packaging...")
        # Create dummy parts
        parts = {"p1.stl": self.mesh}
        zip_io = self.splitter.pack_zip(parts)
        self.assertIsInstance(zip_io, io.BytesIO)
        self.assertGreater(zip_io.getbuffer().nbytes, 0)
        print("ZIP Packaging PASSED")

if __name__ == '__main__':
    unittest.main()
