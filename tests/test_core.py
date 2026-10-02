import unittest
import tempfile
import sys
import os
from pathlib import Path

# Add package directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'vinautil'))

from vinautil.scardock import cleanATOM, SCARdock
from vinautil.vutils.obabel import PDBQTparser


class TestPDBQTParser(unittest.TestCase):
    def setUp(self):
        self.sample_pdbqt = """MODEL 1
REMARK VINA RESULT:    -7.500      0.000      0.000
ATOM      1  C1  UNL     1       0.000   1.000   2.000  0.00  0.00    +0.050 C 
ATOM      2  C2  UNL     1       1.000   1.000   2.000  0.00  0.00    +0.050 C 
ENDMDL
MODEL 2
REMARK VINA RESULT:    -6.800      1.500      2.100
ATOM      1  C1  UNL     1       0.500   1.200   2.300  0.00  0.00    +0.050 C 
ATOM      2  C2  UNL     1       1.500   1.200   2.300  0.00  0.00    +0.050 C 
ENDMDL
"""
        self.tmp = tempfile.NamedTemporaryFile('w', delete=False, suffix='.pdbqt')
        self.tmp.write(self.sample_pdbqt)
        self.tmp.close()

    def tearDown(self):
        if os.path.exists(self.tmp.name):
            os.remove(self.tmp.name)

    def test_module_count_and_content(self):
        parser = PDBQTparser(Path(self.tmp.name))
        self.assertEqual(parser.module_num, 2)
        modules = parser.get_modules()
        self.assertEqual(len(modules), 2)
        self.assertIn("MODEL 1", modules[0])
        self.assertIn("MODEL 2", modules[1])
        single_pose = parser.get_modules(0)
        self.assertIn("MODEL 1", single_pose)


class TestCleanATOM(unittest.TestCase):
    def setUp(self):
        self.sample_pdb = """HEADER    TEST PDB
TITLE     MOCK PDB FILE
COMPND    MOL_ID: 1
ATOM      1  N   ALA A   1      11.104  13.207   9.000  1.00 20.00           N
ATOM      2  CA  ALA A   1      12.000  14.000  10.000  1.00 20.00           C
HETATM    3  O   HOH A 101      20.000  25.000  30.000  1.00 30.00           O
TER       4      ALA A   1
END
"""
        self.tmp_in = tempfile.NamedTemporaryFile('w', delete=False, suffix='.pdb')
        self.tmp_in.write(self.sample_pdb)
        self.tmp_in.close()

    def tearDown(self):
        if os.path.exists(self.tmp_in.name):
            os.remove(self.tmp_in.name)

    def test_clean_atom_filters_hetatm(self):
        cleaned_path = cleanATOM(self.tmp_in.name)
        self.assertTrue(cleaned_path.exists())
        content = cleaned_path.read_text().splitlines()
        self.assertEqual(len(content), 3)  # Only 2 ATOM + 1 TER lines
        self.assertTrue(all(line.startswith(('ATOM', 'TER')) for line in content))
        if cleaned_path.exists():
            cleaned_path.unlink()


class TestCLIValidation(unittest.TestCase):
    def test_missing_required_arguments_exits_gracefully(self):
        # Verify that running SCARdock with no arguments exits with code 2 rather than hanging on stdin
        old_argv = sys.argv
        sys.argv = ['scardock']
        try:
            with self.assertRaises(SystemExit) as cm:
                SCARdock()
            self.assertEqual(cm.exception.code, 2)
        finally:
            sys.argv = old_argv


if __name__ == '__main__':
    unittest.main()
