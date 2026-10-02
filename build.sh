#!/usr/bin/env bash
set -euo pipefail

# Install current scardock-util package into conda build prefix
"$PYTHON" -m pip install . --no-deps --no-build-isolation -vv

# Resilient clone of Meeko with official repo fallback
echo "Cloning Meeko..."
if ! git clone --depth 1 https://github.com/forlilab/Meeko.git; then
    echo "Direct clone failed, retrying via mirror..."
    git clone --depth 1 https://mirror.ghproxy.com/https://github.com/forlilab/Meeko.git
fi

cd Meeko
"$PYTHON" -m pip install . --no-deps --no-build-isolation -vv
