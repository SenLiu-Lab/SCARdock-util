<div align="center">

# SCARdock-util (scardock-util)

**A Comprehensive Toolkit for SCARdock Covalent Docking, Bond Restoration, and Molecular Modeling**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux--64-green.svg)](https://github.com/SenLiu-Lab/SCARdock-util)
[![Conda Channel](https://img.shields.io/badge/Conda-pylyzeng-brightgreen.svg)](https://anaconda.org/pylyzeng/scardock-util)
[![GitHub stars](https://img.shields.io/github/stars/SenLiu-Lab/SCARdock-util?style=social)](https://github.com/SenLiu-Lab/SCARdock-util)

[English](./README.md) | [简体中文](./README_cn.md)

</div>

---

## 📖 Introduction

**SCARdock-util** (distributed in Conda as `scardock-util`, formerly `vinautil`) is an all-in-one computational chemistry utility package tailored for [AutoDock Vina](https://vina.scripps.edu/) and the [SCARdock](https://pubs.acs.org/doi/10.1021/acs.jcim.6b00334) covalent inhibitor screening protocol.

Molecular docking with standard Vina and PDBQT format often encounters two major challenges:
1. **Manual complexity in covalent docking**: Setting up SCARdock requires tedious pre-docking preparation, including cleaning PDB coordinates, in-silico mutation of the targeted catalytic residue into Glycine to accommodate the covalent warhead, preparing polar hydrogens, and positioning docking boxes.
2. **Loss of chemical bond information in PDBQT**: Standard PDBQT files only store partial charges and coordinates without explicit bond orders and connectivity. Direct format conversion usually results in broken bonds or incorrect aromaticity, causing severe bias in downstream analysis such as RMSD calculation.

**SCARdock-util** solves these problems with automated workflows, coordinate-topology mapping, and symmetry-aware post-processing.

All core algorithms were developed by **Lingyu Zeng** during graduate research under the supervision of **Prof. Sen Liu** ([Sen Liu Lab](https://life.hbut.edu.cn/info/1168/1745.htm)), [School of Life Sciences and Health Engineering](https://life.hbut.edu.cn/), Hubei University of Technology.

---

## 🌟 Core Functionalities & Highlights

### 1. ⚡ One-Click Automated SCARdock Covalent Docking
- **In-Silico Glycine Mutation**: Automatically executes site-directed mutation (`Target Residue -> GLY`) at the covalent attachment site (e.g. Cys, Ser, Lys) using built-in PyMOL mutagenesis utilities, removing steric clash from native sidechains while preserving backbone conformation.
- **Automated Receptor/Ligand Preparation**:
  - Receptor: Cleans standard `ATOM`/`TER` records, checks/adds hydrogens, and converts to PDBQT via MGLTools.
  - Ligand: Automatically adds polar hydrogens via OpenBabel and translates 3D coordinates into docking-ready PDBQT format using Meeko.
- **Smart Search Space Centering**: Automatically detects the alpha/beta carbon coordinates of the mutated residue and defines a 40 Å cubic search space around the reaction site.
- **Vina Engine Sampling & Energy Minimization**: Automatically invokes the AutoDock Vina engine for rigorous conformational search, scoring, and local energy optimization.

### 2. 🔄 PDBQT-to-MOL2 Bond Restoration & Symmetry-Aware RMSD
- **Lossless Bond Order Reconstruction (`PDBQTtoMol2`)**: Matches the docking output PDBQT atom coordinates back onto the original MOL2 connectivity graph. Accurately restores aromatic bonds, double/triple bonds, and formal charges without atom re-indexing errors.
- **Symmetry-Corrected RMSD Calculation**: Uses `spyrmsd` to compute topological symmetry-corrected RMSD between restored docked poses and the reference crystallographic ligand, avoiding false high-RMSD values caused by symmetric atom rotations (e.g. phenyl or carboxylate symmetry).

### 3. 🎯 Binding Pocket Detection & Vina Grid Box Generation
- **Fpocket & DeepPocket Integration**: Bridges classic geometric alpha-sphere pocket detection ([fpocket](https://github.com/Discngine/fpocket)) and deep learning site prediction ([DeepPocket](https://github.com/VincentBioSys/DeepPocket)).
- **Automated Grid Box Parameters**: Computes optimal grid centers (`center_x, center_y, center_z`) and boundaries (`size_x, size_y, size_z`) directly from predicted cavities for immediate use in AutoDock Vina configuration files.

### 4. 🧪 PyMOL Structure Biology Extension Toolkit
- Built-in utilities for structure cleaning, polar hydrogen calculation, residue mutagenesis, and coloring scripts for presentation-ready figures.

### 5. 📦 Zero-Pain Conda Distribution
- Avoids Python/C++ dependency conflicts by providing pre-built packages for Linux-64 containing `vina 1.2.3`, `pymol-open-source`, `openmm`, `pdbfixer`, `mgltools`, `openbabel`, `rdkit`, and `prody`.

---

## 🔄 Workflow Pipeline

```text
Target Receptor (PDB) + Ligand (MOL2/SDF)
   │
   ├─► Receptor Clean & Mutagenesis (cleanATOM -> TargetResidue to GLY -> PDBQT)
   │
   ├─► Ligand Preparation (Add Polar Hydrogens -> Meeko PDBQT)
   │
   ├─► Auto Search Box (Center at Target Cα/Cβ, 40Å Box)
   │
   ├─► AutoDock Vina Execution (Sampling + Energy Minimization)
   │
   ├─► Topology Restoration (PDBQT -> MOL2 with original bond orders restored)
   │
   └─► Rigorous Evaluation (spyrmsd Symmetry-Corrected RMSD)
```

---

## 🚀 Quick Start

### 1. Installation via Conda (Recommended)

```bash
# Create and activate environment
conda create -n scardock_env -c pylyzeng -c conda-forge -c bioconda scardock-util --yes
conda activate scardock_env
```

### 2. Installation from Source (Development)

```bash
# Clone the repository
git clone https://github.com/SenLiu-Lab/SCARdock-util.git
cd SCARdock-util

# Create environment from configuration
conda env create -f environment.yml -n scardock_dev
conda activate scardock_dev

# Install editable package
pip install -e . --no-deps
```

---

## 💻 Usage & Examples

### Method 1: Command Line Interface (CLI)

#### Run Built-in Verification Test

Verify your installation with the bundled crystal complex test dataset (PDB ID: `4I24`, covalent residue: Cys797):

```bash
scardocktest
```

#### Run Custom SCARdock Task

```bash
scardock \
  -r ./receptor.pdb \
  -l ./ligand.mol2 \
  -c A \
  -s 797 \
  -log ./logs
```

**CLI Argument Reference (`scardock -h`):**

| Flag | Long Argument | Type | Description |
|---|---|---|---|
| `-r` | `--receptor` | File | Input receptor structure file (`.pdb`) |
| `-l` | `--ligand` | File | Input ligand file (`.mol2` / `.sdf`) |
| `-c` | `--chain` | String | Covalent target protein chain ID (e.g., `A`) |
| `-s` | `--site` | Integer | Covalent target residue number (e.g., `797`) |
| `-log` | `--log_dir` | Directory | Directory for log outputs (Default: `./`) |
| `-h` | `--help` | - | Display help documentation |

---

### Method 2: Python API Usage

#### Example A: Restoring PDBQT to MOL2 & Computing Symmetry RMSD

```python
from pathlib import Path
from vinautil.vutils.obabel import PDBQTtoMol2, PDBQTparser
from vinautil.vutils.spyrmsd_load import symmrmsd_mol2_list

ref_mol2 = Path("ligand.mol2").read_text()
undocked_pdbqt = Path("ligand.pdbqt").read_text()
docked_pdbqt_file = Path("receptor--ligand.pdbqt")

# Parse multi-pose PDBQT output
parser = PDBQTparser(docked_pdbqt_file)
docked_poses = parser.get_modules()

# 1. Restore 3D coordinates into original MOL2 bond topologies
restorer = PDBQTtoMol2(
    original_mol2_file=ref_mol2,
    undock_pdbqt=undocked_pdbqt,
    docked_pdbqt=docked_poses
)
restored_mol2_list = restorer.to_string()

# Save restored poses
for idx, mol2_str in enumerate(restored_mol2_list):
    Path(f"pose_{idx+1}.mol2").write_text(mol2_str)

# 2. Compute symmetry-corrected RMSD against reference
rmsd_values = symmrmsd_mol2_list(
    mol2_docked=restored_mol2_list, 
    mol2_ref=ref_mol2
)
print("Symmetry RMSD (Å):", [f"{x:.2f}" for x in rmsd_values])
```

#### Example B: Cavity Detection & Vina Box Parameters via Fpocket

```python
from pathlib import Path
from vinautil.vutils.fpocket import FpocketBox

# Run pocket detection on target receptor
fp = FpocketBox(pdb_file=Path("receptor.pdb"))
fp.run_fpocket()

# Get predicted pocket centers and box dimensions
center, size = fp.get_box_by_pocket(pocket_id=1)
print(f"Vina Box Center: {center}")
print(f"Vina Box Size:   {size}")
```

---

## 📂 Repository Structure

```text
.
├── .condaignore               # Files excluded from conda packaging
├── bld.bat / build.sh         # Conda build scripts (Windows & Linux)
├── environment.yml            # Complete Conda environment specification
├── meta.yaml                  # Conda recipe manifest
├── setup.py                   # Setuptools packaging script
├── conda_pack.md              # Conda build & Anaconda upload guide
├── unittest.py                # Unit test runner
├── vinautil/                  # Core library source code
│   ├── vinautil/
│   │   ├── scardock.py        # Core SCARdock workflow & CLI commands
│   │   ├── vina.py            # AutoDock Vina wrapper & scoring routines
│   │   ├── restore_mol2.py    # PDBQT to MOL2 coordinate-bond mapper
│   │   ├── parserPDBQT.py     # PDBQT multi-pose text parser
│   │   ├── pymolutils/        # PyMOL scripts (mutation, color, hydrogen)
│   │   ├── vutils/            # Auxiliary tools (Fpocket, DeepPocket, RMSD)
│   │   └── test/              # Benchmark data (4I24 crystal structure)
└── README.md
```

---

## 🗺️ Roadmap & CI/CD Plans

- [x] Align `dev` branch with `master`.
- [x] Standardize open-source documentation with detailed functional guides.
- [ ] **GitHub Actions Automated CI/CD Pipeline** *(Under Development)*:
  - **Automated Testing**: Run lint checks and `pytest` test suites on PRs and commits.
  - **Automated Conda Build**: Run `conda-build` on Linux runners to ensure recipe integrity.
  - **Automated Release**: Automatically tag versions and publish build artifacts to Anaconda Cloud (`pylyzeng` channel) upon GitHub Releases.
- [ ] Support for non-covalent multi-ligand batch screening pipelines.
- [ ] Python 3.11 / 3.12 compatibility upgrades.

---

## 📚 References & Citation

If you utilize SCARdock-util or the SCARdock protocol in your academic work, please cite:

1. **SCARdock Method**:  
   Ai, Y. B., Yu, L. L., Tan, X., Chai, X. Y., Liu, S. (2016). *Discovery of Covalent Ligands via Noncovalent Docking by Dissecting Covalent Docking Based on a “Steric-Clashes Alleviating Receptor (SCAR)” Strategy.* **Journal of Chemical Information and Modeling**, 56(8), 1563–1575. [DOI: 10.1021/acs.jcim.6b00334](https://pubs.acs.org/doi/10.1021/acs.jcim.6b00334)
   Ai, Y. B., Xu, S. Y., Zhang Y., Liu, Z. X., Liu, S. (2025). *High-efficiency discovery and structure-activity-relationship analysis of non-substrate-based covalent inhibitors of S-adenosylmethionine decarboxylase.* **Journal of Medicinal Chemistry**, 65(18), 15483-15494. [DOI:10.1021/acs.jmedchem.4c03191](https://pubs.acs.org/jmcmar/article-abstract/68/15/15483/5234957/High-Efficiency-Discovery-and-Structure-Activity)
3. **SCARdock Screening Server**:  
   Zeng, L., Song, Q., & Liu, S. (2023). *SCARdock: A Web Server for Covalent Inhibitor Virtual Screening.* **ACS Omega**, 8(2), 2634–2641. [DOI: 10.1021/acsomega.2c08147](https://pubs.acs.org/doi/10.1021/acsomega.2c08147)

---

## 👥 Acknowledgements

- **Prof. Sen Liu** ([Personal Page](https://life.hbut.edu.cn/info/1168/1745.htm)) - Project Advisor
- **Prof. Qi Song** ([Personal Page](https://life.hbut.edu.cn/info/1229/1863.htm)) - Research Collaborator
- [School of Life Sciences and Health Engineering, Hubei University of Technology](https://life.hbut.edu.cn/)

---

## 📄 License

This project is licensed under the [MIT License](./LICENSE).
