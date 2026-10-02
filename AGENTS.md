# AGENTS.md - SCARdock-util 代码库维护指南与 Agent 行为守则

本文档为后续接手维护、开发、构建和审查本仓库的 AI 代理（Agent）与开发者提供权威指导。请在执行任何代码变更前完整阅读本指南，并严格遵守各项规范。

---

## 🎯 一、项目核心概述与定位

- **项目全称**：SCARdock-util
- **Conda 包名**：`scardock-util`（Conda 频道：`pylyzeng`）
  - *历史兼容说明*：2023 年之前的旧包名曾为 `vinautil`，在 Anaconda.org 上保留归档；当前所有新版本一律以 `scardock-util` 发布。
- **Python 核心模块**：`scardock_util`（扁平化单层命名空间）
- **核心定位与功能**：
  1. **自动化共价对接（SCARdock Protocol）**：受体蛋白定点甘氨酸突变（`Target Residue -> GLY`）、受体清洗与加氢、受体/配体 PDBQT 准备、共价位点空间盒子自动计算、AutoDock Vina 局部能量最小化与构象搜索。
  2. **成键信息无损还原（Bond Restoration）**：将对接输出的 PDBQT 坐标利用参考 MOL2 的拓扑关系进行一对一欧氏距离映射还原（`PDBQTtoMol2`），准确恢复芳香键、双键与键级。
  3. **真实对称性校正 RMSD（Symmetry RMSD）**：集成 `spyrmsd` 消除由于对称原子翻转带来的虚假高 RMSD。
  4. **结合口袋预测（Pocket Detection）**：集成 `Fpocket`（几何特征）与 `DeepPocket`（深度学习）自动输出 Vina 对接网格。
- **学术与机构信息**：
  - 研发机构：[湖北工业大学生命科学与健康工程学院](https://life.hbut.edu.cn/)
  - 指导导师：[刘森 教授](https://life.hbut.edu.cn/info/1168/1745.htm)
  - 合作学者：[宋奇 老师](https://life.hbut.edu.cn/info/1229/1863.htm)

---

## 📁 二、代码库标准目录结构

```text
SCARdock-util/
├── .github/
│   └── workflows/
│       ├── ci.yml                 # 提交/PR 基础自动化测试 (Python 3.10)
│       ├── release.yml            # 打 Tag (v*) 或手动触发的 Conda 打包与发布
│       └── cleanup.yml            # 每月 1 日自动清理旧运行记录与缓存
├── scardock_util/                 # Python 核心业务模块（禁止恢复原两层嵌套结构）
│   ├── scardock.py                # SCARdock 对接全流程与 CLI 入口
│   ├── vina.py                    # AutoDock Vina Python 封装
│   ├── restore_mol2.py            # PDBQT 转 MOL2 成键信息恢复
│   ├── parserPDBQT.py             # PDBQT 多模型文本解析
│   ├── vinaconfig.py              # 对接盒子三维坐标数据结构
│   ├── getbox_pymol.py            # PyMOL 结合腔盒子计算
│   ├── pymolutils/                # PyMOL 插件（定点突变、色彩、加氢）
│   ├── vutils/                    # 辅助工具（Fpocket, DeepPocket, RMSD, OpenBabel）
│   └── test/                      # 核心基准测试数据（4I24 晶体复合物）
├── tests/                         # 标准单元测试目录
│   └── test_core.py               # 核心解析、CLI 参数、ATOM 清洗单元测试
├── examples/                      # 用户教程与 Notebook 示范
│   └── scardock_pipeline_demo.ipynb
├── .condaignore                   # Conda 打包排除项
├── .gitignore                     # Git 忽略配置
├── bld.bat / build.sh             # Conda 构建安装脚本
├── environment.yml                # 跨平台开发运行环境声明
├── meta.yaml                      # Conda Recipe 配方元数据
├── setup.py                       # Setuptools 安装与 Console Scripts 配置
├── conda_pack.md                  # Conda 打包操作说明文档
├── README.md                      # 官方英文文档
├── README_cn.md                   # 官方中文文档
└── AGENTS.md                      # 本文档（Agent 维护规则）
```

---

## 🛑 三、科学逻辑与工程质量铁律（Agent 绝不可违反）

### 1. 【重大科学性铁律】受体突变文件必须正确传递
- **规则**：在 `scardock_util/scardock.py` 的 `SCARdockbase` 中，通过 PyMOL 进行定点甘氨酸突变后生成了突变文件 `muta_receptor`。
- **强制约束**：调用 MGLTools `prepare_receptor4` 生成受体 PDBQT 时，**必须使用 `muta_receptor` 作为输入（`-r` 参数）**，绝对不能退化传入原始未突变的野生型 `receptor`！否则原生侧链位阻会导致共价对接完全失效。

### 2. 【子进程安全性铁律】严禁裸写 `subprocess.Popen` 无超时轮询
- **规则**：调用外部二进制（如 MGLTools 的 `prepare_receptor4`、Meeko 的 `mk_prepare_ligand`）时，必须统一通过内部封装的 `_run_cmd()` 执行。
- **强制约束**：必须传入参数列表（禁止 `shell=True`）、显式配置 `timeout`（默认 300s）、捕获 stdout/stderr，并在命令结束后校验输出 PDBQT 文件存在且大小大于 0。

### 3. 【依赖隔离铁律】计算化学重依赖按需导入（Lazy Import）
- **规则**：`scardock.py` 和通用工具函数（如 `cleanATOM`、`PDBQTparser`）严禁在文件顶层无保护地强制导入重度 C++ 扩展包（如 `pymol`, `vina`, `openbabel`）。
- **原因**：必须保证 `scardock -h`、CLI 参数解析以及纯文本处理测试在未安装上述重库的轻量级 Python 环境中也能秒级运行。

### 4. 【CLI 健壮性铁律】必填参数严禁设为 `default=sys.stdin`
- **规则**：CLI 必填文件或位点参数（`-r, -l, -s, -c`）必须声明为 `required=True`，并赋予明确类型（`Path`, `int`, `str`）。缺失参数时必须直接抛出标准错误提示并安全退出，严禁阻塞等待标准输入。

### 5. 【测试命名铁律】禁止在根目录创建 `unittest.py`
- **规则**：所有单元测试必须存放在 `tests/` 目录下，并以 `test_*.py` 命名。根目录下绝对禁止新建名为 `unittest.py` 的文件，否则会导致 Python 标准库 `unittest` 发生循环自我遮蔽崩溃。

---

## 🌿 四、分支管理与同步规则

当前仓库的分支体系如下：
- **`main`**：主要工作分支，所有新特性、文档优化与 Bug 修复均应合并至此。
- **`dev`**：日常开发分支，每次向 `main` 提交后，**必须将 `dev` 快进同步（Fast-Forward）至最新**，保持对齐。
- **`master`**：由于历史原因在 GitHub 远程保留作为过渡分支。在组织管理员完成默认分支切换前，**必须保持 `master` 与 `main` 完全同步推送**。

```bash
# 典型的三分支对齐提交流程：
git checkout main
# ... 完成修改并 commit ...
git push origin main

# 同步 dev 分支
git checkout dev
git merge --ff-only main
git push origin dev

# 同步 master 分支并切回 main
git checkout -b master origin/master 2>/dev/null || git checkout master
git merge --ff-only main
git push origin master
git checkout main
```

---

## 🚀 五、Conda 包构建与版本发布标准流程

### 1. 自动化流水线说明
本仓库配有全自动 GitHub Actions 工作流：
- **`ci.yml`**：Push / PR 触发轻量级 Python 3.10 单元测试。
- **`release.yml`**：推送版本 Tag（`v*`）时自动在 Ubuntu Runner 上启动 `Miniforge`，通过 `conda run -n build conda-build` 编译 `linux-64` 的 `.conda` 包，并使用凭据推送到 Anaconda Cloud（`pylyzeng` 频道）。
- **`cleanup.yml`**：每月 1 日 00:00 UTC 自动清理过期的 Actions 运行记录与缓存。

### 2. 发布新版本（例如 `0.2.0`）标准操作步骤

```bash
# 步骤 1：更新版本号
# 编辑 meta.yaml: package.version -> 0.2.0, build.number -> 0
# 编辑 setup.py (其自动从 meta.yaml 读取 version)

# 步骤 2：本地运行回归测试
python -m unittest discover -s tests -v

# 步骤 3：提交修改并推送
git add meta.yaml setup.py ...
git commit -m "chore(release): bump version to 0.2.0"
git push origin main
# (同时同步 dev 和 master 分支)

# 步骤 4：打 Tag 并触发自动构建与发布
git tag v0.2.0
git push origin v0.2.0

# 步骤 5：在 GitHub Actions 中观察发布结果
gh run list --workflow "Build & Release Conda Package"
```

### 3. Repository Secrets 凭据规范
- 键名：**`ANACONDA_API_TOKEN`**（已在仓库 Secrets 中配置，有效期至 2027 年）。
- **安全约束**：严禁在任何脚本、日志或提交信息中明文打印此 Token；若重新生成，需通过 `gh secret set ANACONDA_API_TOKEN` 写入。

---

## 📚 六、学术引用与外部链接准则

- **核心文献**：
  1. *Ai, Y. B., et al. (2016). JCIM. DOI: 10.1021/acs.jcim.6b00334*（SCARdock 原始方法）
  2. *Ai, Y. B., et al. (2025). J. Med. Chem. DOI: 10.1021/acs.jmedchem.4c03191*（SAR 应用拓展）
  3. *Zeng, L., et al. (2023). ACS Omega. DOI: 10.1021/acsomega.2c08147*（SCARdock 在线平台）
- 严禁擅自删除或替换上述三篇课题组正统成果论文。
- 导师与学院主页一律使用官方新链接：`https://life.hbut.edu.cn/info/1168/1745.htm` 及 `https://life.hbut.edu.cn/`。
