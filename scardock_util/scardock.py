import argparse
from pathlib import Path
import os, sys, shutil
import subprocess
import datetime
from typing import List, Optional

# 获取当前 Python 解释器及工具路径
python_exec_prefix = Path(sys.exec_prefix)
here = Path(__file__).parent.resolve()
python2_interpreter = python_exec_prefix.joinpath('bin/python2')
python3_interpreter = Path(sys.executable)
prepare_ligand4 = python_exec_prefix.joinpath('MGLToolsPckgs/AutoDockTools/Utilities24/prepare_ligand4.py')
prepare_receptor4 = python_exec_prefix.joinpath('MGLToolsPckgs/AutoDockTools/Utilities24/prepare_receptor4.py')
mk_prepare_ligand = python_exec_prefix.joinpath('bin/mk_prepare_ligand.py')

def _resolve_tool(tool_path: Path, tool_name: str) -> str:
    """Resolve executable or script path from prefix or system PATH."""
    if tool_path.exists():
        return tool_path.as_posix()
    which_res = shutil.which(tool_name)
    if which_res:
        return which_res
    return tool_path.as_posix()

def _log(level: str, message: str) -> None:
    try:
        from loguru import logger
        getattr(logger, level.lower(), logger.info)(message)
    except ImportError:
        print(f"[{level.upper()}] {message}")

def _run_cmd(argv: List[str], output_file: Path, desc: str, timeout: int = 300) -> None:
    """Execute external CLI tools robustly with error handling and output checks."""
    _log("info", f"Running {desc}: {' '.join(argv)}")
    try:
        res = subprocess.run(
            argv,
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if res.stdout:
            _log("info", f"{desc} output:\n{res.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        err_msg = f"{desc} failed with exit code {e.returncode}.\nStderr: {e.stderr}\nStdout: {e.stdout}"
        _log("error", err_msg)
        raise RuntimeError(f"{desc} failed (exit code {e.returncode}): {e.stderr or e.stdout}") from e
    except subprocess.TimeoutExpired as e:
        _log("error", f"{desc} timed out after {timeout}s.")
        raise RuntimeError(f"{desc} timed out after {timeout} seconds.") from e

    if not output_file.exists() or output_file.stat().st_size == 0:
        raise RuntimeError(f"{desc} succeeded but expected output file was not found or is empty: {output_file}")

def dockvina(receptor:Path, ligand:Path, center:List[float], box_size:List[float], 
             exhaustiveness:int =32, n_poses:int =20, out_n_poses:int = 20):
    from scardock_util.vina import Vina
    out_stem = f'{receptor.stem}--{ligand.stem}'
    out_dir = receptor.parent
    v = Vina(sf_name='vina')
    v.set_receptor(receptor.as_posix())
    v.set_ligand_from_file(ligand.as_posix())
    v.compute_vina_maps(center=center, box_size=box_size)
    # Score the current pose
    energy = v.score()
    print('Score before minimization: %.3f (kcal/mol)' % energy[0])
    # Minimized locally the current pose
    energy_minimized = v.optimize()
    print('Score after minimization : %.3f (kcal/mol)' % energy_minimized[0])
    v.write_pose(out_dir.joinpath(f'{out_stem}_minimized.pdbqt').as_posix(), overwrite=True)
    # Dock the ligand
    v.dock(exhaustiveness=exhaustiveness, n_poses=n_poses)
    docked_file = out_dir.joinpath(f'{out_stem}.pdbqt')
    v.write_poses(docked_file.as_posix(), n_poses=out_n_poses, overwrite=True)
    return docked_file

def SCARdockbase(receptor: Path, ligand: Path, chain: str, site: str):
    from pymol import cmd
    from openbabel import pybel
    from scardock_util.vutils.obabel import PDBQTtoMol2, PDBQTparser
    from scardock_util.vutils.spyrmsd_load import symmrmsd_mol2_list
    from scardock_util.pymolutils.mutagenesis import Mutagenesis_site

    # clean pdb file
    receptor = cleanATOM(receptor.as_posix()) # same pyrosetta.toolbox cleanATOM
    if not receptor.exists():
        raise FileNotFoundError(f'{receptor.as_posix()} not found')
    # protein Mutagenesis (GLY)
    print('Mutagenesis site: ', site)
    muta_receptor = receptor.parent.joinpath(f'{receptor.stem}_{site}G.pdb')
    Mutagenesis_site(filename=receptor, mutation_type='GLY', site=int(site), outfile=muta_receptor)
    # prepare receptor dock file
    print('Prepare PDBQT receptor file: ', muta_receptor.name)
    receptor_pdbqt = receptor.parent.joinpath(f"{muta_receptor.stem}.pdbqt")
    py2_bin = _resolve_tool(python2_interpreter, 'python2')
    prep_rec = _resolve_tool(prepare_receptor4, 'prepare_receptor4.py')
    _run_cmd(
        [py2_bin, prep_rec, '-r', muta_receptor.as_posix(), '-o', receptor_pdbqt.as_posix(), '-A', 'checkhydrogens'],
        receptor_pdbqt,
        "Receptor PDBQT preparation"
    )
    # prepare ligand dock file(file)
    ligand = Path(ligand)
    ligand_pdbqt = ligand.parent.joinpath(f"{ligand.stem}.pdbqt")
    file_polarHydrogens = ligand.parent.joinpath(f'{ligand.stem}_add_polarHydrogens.mol2')
    if not ligand.exists():
        raise FileNotFoundError(f'{ligand} not found')
    # use openbabel add polar hydrogens
    print('Add polar hydrogens(Openbabel): ', ligand.name)
    lfmt = ligand.suffix[1:]
    molH = pybel.readfile(lfmt, ligand.as_posix())
    molH = next(molH)
    molH.OBMol.DeleteHydrogens()
    molH.OBMol.AddPolarHydrogens()
    molH.write('mol2', file_polarHydrogens.as_posix(), overwrite=True)
    # use meeko backend prepare ligand, optional MGLtools prepare_ligand4.py
    print('Prepare PDBQT ligand file: ', ligand.name)
    py3_bin = _resolve_tool(python3_interpreter, 'python3')
    prep_lig = _resolve_tool(mk_prepare_ligand, 'mk_prepare_ligand.py')
    _run_cmd(
        [py3_bin, prep_lig, '-i', file_polarHydrogens.as_posix(), '-o', ligand_pdbqt.as_posix()],
        ligand_pdbqt,
        "Ligand PDBQT preparation"
    )
    # box center, covalent beta carbon coordinate
    cmd.reinitialize('everything')
    cmd.load(receptor.as_posix())
    coordinates = []
    cmd.select('res_covalent_atoms', f'chain {chain} and resi {site} and name CA') # select residue covalent site apha carbon, be careful GLY have no side chain with beta carbon
    cmd.iterate_state('0', 'res_covalent_atoms', 'coordinates.append([x,y,z])', space=locals())
    if len(coordinates) == 1:
        center = coordinates[0]
        print('Covalent residue beta carbon coordinate(center): ', center)
    else:
        raise ValueError(f'covalent beta carbon site {site} not found!')
    # SCARdock docking
    # ! be careful, orginal molecule coordinate should in docking box
    print("The molecular coordinates of the input mol2 file should be within a range of 40 angstroms, with the covalent residue's beta carbon atom as the center of the extended box.")
    docked_file = dockvina(receptor=receptor_pdbqt, ligand=ligand_pdbqt, center=center, box_size=[40, 40, 40], exhaustiveness=32, n_poses=20, out_n_poses=20)
    # restore mol2 (update coordinate)
    print('Restore mol2 file: ', ligand.name)
    ins = PDBQTtoMol2(file_polarHydrogens.read_text(), ligand_pdbqt.read_text(), PDBQTparser(docked_file).get_modules())
    res_mol2 = ins.to_string() # mol2 string list
    # write mol2
    for n,m in enumerate(res_mol2):
        mol2_file = ligand.parent.joinpath(f'{ligand.stem}+{str(n+1).zfill(3)}.mol2')
        mol2_file.write_text(m)
    # cal RMSD(spyrmsd)
    print('Calculate RMSD(spyrmsd): ')
    res = symmrmsd_mol2_list(mol2_docked=res_mol2, mol2_ref=ligand.read_text())
    res_list = ['{:.2f}'.format(i) for i in res]
    print(f'''
SCARdock docking result: {docked_file}
RMSD: {res_list}''')

def SCARdock():
    # cmd lineparser
    parser = argparse.ArgumentParser(description='SCARdock Covalent Docking Workflow')
    parser.add_argument('-r', '--receptor', type=Path, required=True, help='Receptor PDB structure file')
    parser.add_argument('-l', '--ligand', type=Path, required=True, help='Ligand molecule file (MOL2, SDF, ...)')
    parser.add_argument('-s', '--site', type=int, required=True, help='Residue covalent attachment site index (e.g. 797)')
    parser.add_argument('-c', '--chain', type=str, required=True, help='Target receptor chain ID (e.g. A)')
    parser.add_argument('-log', '--log_dir', type=Path, default=Path('./'), help='Output log directory (default: current directory)')
    args = parser.parse_args()
    
    # 确保日志输出目录存在
    args.log_dir.mkdir(parents=True, exist_ok=True)
    try:
        from loguru import logger
        log_file = args.log_dir / 'scardock.log'
        logger.add(log_file.as_posix(), encoding='utf-8')
        logger.info('SCARdock covalent docking initialized...')
    except ImportError:
        pass
    
    print('''SCARdock method DOI: 10.1021/acs.jcim.6b00334
SCARdock screening server(https://scardock.com) DOI: 10.1021/acsomega.2c08147
lab site: https://life.hbut.edu.cn/info/1168/1745.htm
author: Lingyu Zeng mail: pylyzeng@gmail.com
''')
    SCARdockbase(receptor=args.receptor, ligand=args.ligand, chain=args.chain, site=str(args.site))
    
def SCARdocktest():
    # Run SCARdock with predefined test parameters
    test_dir = here / 'test'
    receptor = test_dir.joinpath('4i24.pdb').as_posix()
    ligand = test_dir.joinpath('4i24_C_1C9_babel_addh.mol2').as_posix()
    site = 797
    chain = 'A'
    SCARdockbase(receptor=Path(receptor), ligand=Path(ligand), chain=chain, site=str(site))
    
def cleanATOM(pdb_file, out_file=None, ext="_clean.pdb") -> Path:
    """Extract all ATOM and TER records in a PDB file and write them to a new file.

    Args:
        pdb_file (str): Path of the PDB file from which ATOM and TER records
            will be extracted
        out_file (str): Optional argument to specify a particular output filename.
            Defaults to <pdb_file>.clean.pdb.
        ext (str): File extension to use for output file. Defaults to ".clean.pdb"
    """
    # find all ATOM and TER lines
    with open(pdb_file, "r") as fid:
        good = [l for l in fid if l.startswith(("ATOM", "TER"))]

    # default output file to <pdb_file>_clean.pdb
    if out_file is None:
        out_file = os.path.splitext(pdb_file)[0] + ext

    # write the selected records to a new file
    with open(out_file, "w") as fid:
        fid.writelines(good)
    return Path(out_file)
