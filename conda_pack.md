# Conda Packaging & Distribution Guide

## 1. Installation

Install the pre-built package directly into a fresh environment:

```shell
conda create -n scardock_env -c pylyzeng -c conda-forge -c bioconda scardock-util -y
conda activate scardock_env
```

## 2. Automated Build & Release via GitHub Actions

This repository includes automated CI/CD workflows:
- When a new version tag (e.g. `v0.1.0`) is pushed to GitHub, `.github/workflows/release.yml` will automatically build the `linux-64` package and upload it to the `pylyzeng` Anaconda channel.
- You can also trigger the release workflow manually from the **Actions** tab via `workflow_dispatch`.

## 3. Manual Local Build

To build and publish the Conda package manually:

```shell
# Create dedicated build environment
conda create -n condabuild python=3.10 conda-build anaconda-client -c conda-forge -y
conda activate condabuild

# Navigate to repository root
cd SCARdock-util

# Build conda package
conda build . --output-folder ./conda-dist

# Login and upload
anaconda login
anaconda upload ./conda-dist/linux-64/scardock-util-*.tar.bz2
```
