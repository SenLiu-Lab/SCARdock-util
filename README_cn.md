<div align="center">

# SCARdock-util (scardock-util)

**SCARdock 共价分子对接、分子成键信息还原与计算生物学综合工具包**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux--64-green.svg)](https://github.com/SenLiu-Lab/SCARdock-util)
[![Conda Channel](https://img.shields.io/badge/Conda-pylyzeng-brightgreen.svg)](https://anaconda.org/pylyzeng/scardock-util)
[![GitHub stars](https://img.shields.io/github/stars/SenLiu-Lab/SCARdock-util?style=social)](https://github.com/SenLiu-Lab/SCARdock-util)

[English](./README.md) | [简体中文](./README_cn.md)

</div>

---

## 📖 项目简介

**SCARdock-util**（在 Conda 生态中以包名 `scardock-util` 发布，原包名 `vinautil`）是一个面向 [AutoDock Vina](https://vina.scripps.edu/) 与 [SCARdock](https://pubs.acs.org/doi/10.1021/acs.jcim.6b00334) 共价抑制剂筛选协议的自动化分子建模与对接实用工具包。

在传统分子对接中，常面临以下痛点：
1. **共价对接繁琐的手工预处理**：SCARdock 协议要求先对受体做 PDB 结构清洗，将发生共价反应的催化位点残基通过计算突变为甘氨酸（Glycine）以腾出空间容纳配体反应弹头，同时需加极性氢、计算盒子中心与尺寸；
2. **PDBQT 格式丢失真实化学键信息**：AutoDock 系列的 PDBQT 格式仅记录原子坐标、原子类型与部分电荷，**完全丢弃了键级与成键拓扑信息**。使用常规工具将 PDBQT 转回 MOL2 或 SDF 往往会出现键序错乱或断键，导致后续分析（如 RMSD 评价）严重失真。

**SCARdock-util** 彻底解决了上述问题，提供了一键全自动突变与共价对接、PDBQT 无损成键拓扑恢复、对称性校正 RMSD 计算以及结合口袋预测等一系列开箱即用的功能。

本项目所有核心算法均由**曾令宇**在[湖北工业大学生命科学与健康工程学院](https://life.hbut.edu.cn/)攻读硕士研究生期间，在**刘森教授**（[导师主页](https://life.hbut.edu.cn/info/1168/1745.htm)）指导下开发完成。

---

## 🌟 核心功能与亮点

### 1. ⚡ 一键自动化 SCARdock 共价对接
- **计算机定点甘氨酸突变（In-silico Mutagenesis）**：
  自动对受体目标共价位点残基（如 Cys、Ser、Lys 等）执行定点突变为 `GLY`（保留骨架，消除侧链空间位阻），以便配体共价弹头充分伸入结合口袋。
- **全自动受体与配体预处理**：
  - **受体**：自动清洗 PDB 文件中的标准 `ATOM`/`TER` 记录，自动检测并补齐极性氢，由 MGLTools 转化为受体 PDBQT；
  - **配体**：自动利用 OpenBabel 补全极性氢，并调用 Meeko 将 MOL2/SDF 转换为规范配体 PDBQT。
- **智能结合腔网格盒子定位**：
  自动抓取突变位点残基的 Cα/Cβ 空间三维坐标，以其为中心自动生成 40 Å 立方体对接搜索空间。
- **对接采样与能量局部优化**：
  自动调用 AutoDock Vina 核心引擎进行全局多构象采样、能量打分与局部梯度优化。

### 2. 🔄 还原 PDBQT 丢失的化学键信息 & 计算对称性 RMSD
- **无损成键拓扑映射恢复（`PDBQTtoMol2`）**：
  将对接输出的多构象 PDBQT 原子三维坐标无缝映射回初始参考 MOL2 的分子拓扑图谱中，**精准复原芳香键、双键/单键及形式电荷**，避免原子重编号混乱或断键。
- **真实对称性校正 RMSD 计算（Symmetry-Corrected RMSD）**：
  集成 `spyrmsd` 算法，在恢复完整成键信息的基础上，自动进行分子对称性校正（如苯环、羧基翻转等拓扑对称），彻底避免因原子编号对称翻转导致的虚假高 RMSD，输出可信重原子重合度。

### 3. 🎯 结合口袋智能预测与 Vina 对接盒子构建
- **集成 Fpocket 与 DeepPocket**：
  原生封装经典几何 Alpha 球探测算法（[fpocket](https://github.com/Discngine/fpocket)）与基于深度学习的口袋预测模型（[DeepPocket](https://github.com/VincentBioSys/DeepPocket)）。
- **自动化生成 Vina 盒子参数**：
  直接根据预测口袋计算对接网格中心坐标（`center_x, center_y, center_z`）和包围盒尺寸（`size_x, size_y, size_z`）。

### 4. 🧪 PyMOL 结构生物学扩展插件
- 内置针对 PyMOL 的系列脚本与插件：支持结构清洗、极性加氢、残基定点突变以及高质量论文配图自动着色。

### 5. 📦 解决依赖地狱的 Conda 统一分发
- 预先编译打包并解决了计算化学领域异构依赖的冲突问题（包含 `vina 1.2.3`、`pymol-open-source`、`openmm`、`pdbfixer`、`mgltools`、`openbabel`、`rdkit`、`prody` 等）。

---

## 🔄 核心对接工作流示意

```text
受体蛋白 (PDB) + 配体小分子 (MOL2/SDF)
   │
   ├─► 受体自动化清洗与定点突变 (cleanATOM -> 目标位点突变为甘氨酸 GLY -> 受体 PDBQT)
   │
   ├─► 配体自动化准备 (OpenBabel 补齐极性氢 -> Meeko 转换为配体 PDBQT)
   │
   ├─► 智能对接盒子计算 (以突变位点 Cα/Cβ 为中心，构建 40Å 对接网格)
   │
   ├─► AutoDock Vina 对接与构象能量最小化优化
   │
   ├─► 构象成键拓扑还原 (将 PDBQT 坐标写回原始 MOL2，完整复原化学键与键级)
   │
   └─► 构象评价 (调用 spyrmsd 计算消除对称翻转误差的真实验证 RMSD)
```

---

## 🚀 快速上手与安装

### 1. 通过 Conda 直接安装（推荐）

通过预编译的 Conda 包，一行命令完成全套复杂依赖的安装（支持 `linux-64` 平台）：

```bash
# 创建并激活环境
conda create -n scardock_env -c pylyzeng -c conda-forge -c bioconda scardock-util --yes
conda activate scardock_env
```

### 2. 源码本地安装（开发者模式）

如需二次开发或修改源码：

```bash
# 克隆代码仓库
git clone https://github.com/SenLiu-Lab/SCARdock-util.git
cd SCARdock-util

# 从 environment.yml 创建依赖环境
conda env create -f environment.yml -n scardock_dev
conda activate scardock_dev

# 可编辑模式安装
pip install -e . --no-deps
```

---

## 💻 使用方法与示例

### 方式一：命令行终端（CLI）

安装成功后系统将自动注册 `scardock` 与 `scardocktest` 两个命令行入口。

#### 1. 运行内置验证测试

使用仓库内置的靶点晶体复合物验证数据（PDB ID: `4I24`，共价结合残基为 Cys797）进行一键测试：

```bash
scardocktest
```

#### 2. 执行自定义共价对接任务

```bash
scardock \
  -r ./receptor.pdb \
  -l ./ligand.mol2 \
  -c A \
  -s 797 \
  -log ./logs
```

**命令行参数详述（`scardock -h`）：**

| 参数项 | 完整参数 | 类型 | 说明 | 默认值 |
|---|---|---|---|---|
| `-r` | `--receptor` | 文件路径 | 输入的受体蛋白结构文件（`.pdb`） | 必填 |
| `-l` | `--ligand` | 文件路径 | 输入的配体小分子文件（`.mol2` / `.sdf`） | 必填 |
| `-c` | `--chain` | 字符串 | 发生共价反应的受体链标识（例如 `A`） | 必填 |
| `-s` | `--site` | 整数 | 发生共价结合的目标残基编号（例如 `797`） | 必填 |
| `-log` | `--log_dir` | 目录路径 | 运行日志输出目录 | `./` |
| `-h` | `--help` | - | 查看参数帮助说明 | - |

---

### 方式二：Python API 模块调用

#### 示例 A：还原 PDBQT 丢失的化学键信息并计算对称性校正 RMSD

```python
from pathlib import Path
from vinautil.vutils.obabel import PDBQTtoMol2, PDBQTparser
from vinautil.vutils.spyrmsd_load import symmrmsd_mol2_list

ref_mol2 = Path("ligand.mol2").read_text()
undocked_pdbqt = Path("ligand.pdbqt").read_text()
docked_pdbqt_file = Path("receptor--ligand.pdbqt")

# 解析对接输出的多构象 PDBQT
parser = PDBQTparser(docked_pdbqt_file)
docked_poses = parser.get_modules()

# 1. 将 PDBQT 坐标还原为具有完整键级和化学键的 MOL2
restorer = PDBQTtoMol2(
    original_mol2_file=ref_mol2,
    undock_pdbqt=undocked_pdbqt,
    docked_pdbqt=docked_poses
)
restored_mol2_list = restorer.to_string()

# 导出还原后的构象文件
for idx, mol2_str in enumerate(restored_mol2_list):
    Path(f"pose_{idx+1}.mol2").write_text(mol2_str)

# 2. 与参考晶体配体计算对称性校正 RMSD
rmsd_values = symmrmsd_mol2_list(
    mol2_docked=restored_mol2_list, 
    mol2_ref=ref_mol2
)
print("对称性校正 RMSD (Å):", [f"{x:.2f}" for x in rmsd_values])
```

#### 示例 B：使用 Fpocket 预测蛋白活性口袋并生成 Vina 盒子坐标

```python
from pathlib import Path
from vinautil.vutils.fpocket import FpocketBox

# 对目标受体运行口袋探测
fp = FpocketBox(pdb_file=Path("receptor.pdb"))
fp.run_fpocket()

# 获取预测口袋的中心与盒子尺寸
center, size = fp.get_box_by_pocket(pocket_id=1)
print(f"Vina 盒子中心坐标: {center}")
print(f"Vina 盒子尺寸大小: {size}")
```

---

## 📂 仓库代码结构

```text
.
├── .condaignore               # Conda 打包忽略文件配置
├── bld.bat / build.sh         # Conda 打包构建脚本（Windows 与 Linux）
├── environment.yml            # 完整开发运行 Conda 环境声明
├── meta.yaml                  # Conda 包配方（Recipe）元数据定义
├── setup.py                   # Python 包分发与 CLI 注册脚本
├── conda_pack.md              # Conda 打包与上传操作指引
├── unittest.py                # 单元测试文件
├── vinautil/                  # 核心 Python 源码目录
│   ├── vinautil/
│   │   ├── scardock.py        # SCARdock 主流程实现与 CLI 接口
│   │   ├── vina.py            # AutoDock Vina Python 封装
│   │   ├── restore_mol2.py    # PDBQT 转 MOL2 成键信息恢复模块
│   │   ├── parserPDBQT.py     # PDBQT 多构象文本解析器
│   │   ├── pymolutils/        # PyMOL 插件（定点突变、色彩、加氢）
│   │   ├── vutils/            # 口袋探测（Fpocket/DeepPocket）、RMSD 与格式转换
│   │   └── test/              # 测试基准数据（4I24 晶体复合物结构）
└── README_cn.md
```

---

## 🗺️ 后续路线与 CI/CD 规划（待开发）

- [x] 完成 `dev` 与 `master` 分支快进对齐与合并。
- [x] 更新并标准化中英文开源文档。
- [ ] **GitHub Actions 自动化 CI/CD 流水线** *(待开发 / 规划中)*：
  - **自动代码测试**：每次提交与 PR 自动运行代码风格检查与 `pytest` 测试套件。
  - **自动构建 Conda 包**：在 Linux Runner 上通过 `conda-build` 自动化验证并构建包。
  - **自动发布与分发**：发布 GitHub Release 时自动触发打 tag，并将包构建物推送到 Anaconda Cloud（`pylyzeng` channel）及 Release 附件中。
- [ ] 支持非共价多分子高通量虚拟筛选流程集成。
- [ ] Python 3.11 / 3.12 兼容性拓展。

---

## 📚 学术论文与引用

如果您在学术研究中使用了 SCARdock-util 或 SCARdock 相关技术，请引用以下论文：

1. **SCARdock 原始方法**:  
   Zhu, T., Cao, S., Su, P. C., Patel, R., Shah, H., Chokshi, H. K., Szep, S., & Hevener, K. E. (2017). *Hit Identification and Optimization in Virtual Screening: Practical Applications of SCARdock.* **Journal of Chemical Information and Modeling**, 57(4), 844–853. [DOI: 10.1021/acs.jcim.6b00334](https://pubs.acs.org/doi/10.1021/acs.jcim.6b00334)
2. **SCARdock 在线筛选平台**:  
   Zeng, L., Song, Q., & Liu, S. (2023). *SCARdock: A Web Server for Covalent Inhibitor Virtual Screening.* **ACS Omega**, 8(2), 2634–2641. [DOI: 10.1021/acsomega.2c08147](https://pubs.acs.org/doi/10.1021/acsomega.2c08147)

---

## 👥 致谢与交流

- **刘森 教授**（[导师主页](https://life.hbut.edu.cn/info/1168/1745.htm)）
- **宋奇 老师**（[个人主页](https://life.hbut.edu.cn/info/1229/1863.htm)）
- [湖北工业大学生命科学与健康工程学院](https://life.hbut.edu.cn/)

---

## 📄 开源许可证

本项目基于 [MIT License](./LICENSE) 协议开源。
