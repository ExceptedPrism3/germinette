#!/bin/bash

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Credit to @GayaOliveira (GitHub Issue #9) for reporting install.sh failing after a successful
# pip install when pyenv cannot rehash (e.g. /opt/pyenv/shims not writable — pip shim exits non-zero).
verify_germinette_installed() {
    local py="${1:-python3}"
    "$py" -m pip show germinette >/dev/null 2>&1 \
        || "$py" -c "import importlib.metadata as m; m.version('germinette')" >/dev/null 2>&1
}

# uv-managed Pythons often break `python3 -m venv` (ensurepip fails). Prefer `uv venv` when available.
germinenv_python_exe() {
    if [[ -x "$PWD/.germinenv/bin/python3" ]]; then
        echo "$PWD/.germinenv/bin/python3"
    elif [[ -x "$PWD/.germinenv/bin/python" ]]; then
        echo "$PWD/.germinenv/bin/python"
    else
        echo ""
    fi
}

germinenv_is_valid() {
    [[ -f "$PWD/.germinenv/bin/activate" ]] && [[ -n "$(germinenv_python_exe)" ]]
}

create_germinenv() {
    if germinenv_is_valid; then
        return 0
    fi
    if [[ -d .germinenv ]]; then
        echo -e "${YELLOW}Removing incomplete .germinenv (e.g. failed ensurepip)...${NC}"
        rm -rf .germinenv
    fi
    if command -v uv >/dev/null 2>&1; then
        echo -e "${BLUE}Creating .germinenv with uv (works with uv-managed Python)...${NC}"
        if uv venv .germinenv --python python3 2>/dev/null || uv venv .germinenv; then
            :
        else
            echo -e "${RED}uv venv failed.${NC}"
            return 1
        fi
    else
        echo -e "${BLUE}Creating .germinenv with python3 -m venv...${NC}"
        if ! python3 -m venv .germinenv; then
            echo -e "${RED}python3 -m venv failed.${NC}"
            echo -e "${YELLOW}Tip: install uv (https://docs.astral.sh/uv/) and re-run; uv venv avoids broken ensurepip on some Pythons.${NC}"
            return 1
        fi
    fi
    germinenv_is_valid
}

# PEP 668: distro / uv / Homebrew Pythons ship EXTERNALLY-MANAGED and reject pip install --user.
is_externally_managed_python() {
    python3 -c "
import os, sysconfig
stdlib = sysconfig.get_path('stdlib')
if os.path.isfile(os.path.join(stdlib, 'EXTERNALLY-MANAGED')):
    raise SystemExit(0)
raise SystemExit(1)
" 2>/dev/null
}

INSTALL_SCRIPT="${BASH_SOURCE[0]}"

# Common install location when uv was installed but shell PATH not reloaded
if ! command -v uv >/dev/null 2>&1 && [[ -x "$HOME/.local/bin/uv" ]]; then
    PATH="$HOME/.local/bin:$PATH"
    export PATH
fi

echo -e "${BLUE}🌱 Installing Germinette...${NC}"

PIP_EXIT=0
VENV_PY=""

# Install the package
# Credit to @mauricelorenz (GitHub Issue #4) for suggesting the --home isolated installation feature!
if [[ "$1" == "--home" ]]; then
    echo -e "${BLUE}🏠 Installing in isolated environment (--home)...${NC}"

    if ! create_germinenv; then
        echo -e "${RED}❌ Could not create a valid virtual environment in .germinenv${NC}"
        exit 1
    fi

    VENV_PY="$(germinenv_python_exe)"
    echo -e "${BLUE}📦 Installing into .germinenv using ${VENV_PY}${NC}"
    if command -v uv >/dev/null 2>&1; then
        if uv pip install --python "$VENV_PY" .; then
            PIP_EXIT=0
        else
            "$VENV_PY" -m pip install .
            PIP_EXIT=$?
        fi
    else
        "$VENV_PY" -m pip install .
        PIP_EXIT=$?
    fi
    
    # Ensure local bin exists
    mkdir -p "$HOME/.local/bin"
    
    # Symlink the binary to be accessible globally
    # We use the absolute path to the venv binary
    VENV_BIN="$PWD/.germinenv/bin/germinette"
    TARGET_LINK="$HOME/.local/bin/germinette"
    
    echo -e "${BLUE}🔗 Linking $VENV_BIN to $TARGET_LINK...${NC}"
    ln -sf "$VENV_BIN" "$TARGET_LINK"
    
else
    # Standard install logic
    # Credit to @DayraN19 (GitHub Issue #6) for reporting the pip --user virtualenv crash!
    # Prefer `python3 -m pip` so behavior matches the interpreter you run (fewer shim surprises).
    if [[ -z "$VIRTUAL_ENV" ]] && is_externally_managed_python; then
        echo -e "${YELLOW}This Python is externally managed (PEP 668), e.g. uv, Homebrew, or distro packages.${NC}"
        echo -e "${YELLOW}User installs are blocked. Switching to isolated install (same as ${BLUE}./install.sh --home${YELLOW})...${NC}"
        exec bash "$INSTALL_SCRIPT" --home
    fi
    if [[ -n "$VIRTUAL_ENV" ]]; then
        echo -e "${BLUE}🐍 Virtual environment detected ($VIRTUAL_ENV). Installing without --user...${NC}"
        python3 -m pip install .
        PIP_EXIT=$?
    else
        echo -e "${BLUE}👤 Installing to user site-packages...${NC}"
        PIP_LOG="$(mktemp)"
        python3 -m pip install --user . 2>&1 | tee "$PIP_LOG"
        PIP_EXIT=${PIPESTATUS[0]}
        if [[ "$PIP_EXIT" -ne 0 ]] && grep -qiE 'externally-managed-environment|externally managed' "$PIP_LOG" 2>/dev/null; then
            rm -f "$PIP_LOG"
            echo -e "${YELLOW}pip reported an externally-managed-environment error. Retrying with isolated --home install...${NC}"
            exec bash "$INSTALL_SCRIPT" --home
        fi
        rm -f "$PIP_LOG"
    fi
fi

if [ "$PIP_EXIT" -ne 0 ]; then
    if [[ "$1" == "--home" ]] && [[ -n "${VENV_PY:-}" ]] && verify_germinette_installed "$VENV_PY"; then
        echo -e "${YELLOW}⚠️  pip exited with code $PIP_EXIT, but germinette appears installed in .germinenv.${NC}"
    elif verify_germinette_installed; then
        echo -e "${YELLOW}⚠️  pip exited with code $PIP_EXIT, but germinette appears to be installed.${NC}"
        echo -e "${YELLOW}   This often happens with pyenv when rehash fails (e.g. shims directory not writable).${NC}"
        echo -e "${YELLOW}   See: https://github.com/ExceptedPrism3/germinette/issues/9${NC}"
        echo -e "${YELLOW}   Try: hash -r  (or fix permissions on your pyenv shims directory).${NC}"
    else
        echo -e "${RED}❌ Installation failed.${NC}"
        echo -e "${YELLOW}Please open an issue on GitHub: https://github.com/ExceptedPrism3/germinette/issues${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✅ Installation successful!${NC}"

# Save repository location for the updater
REPO_PATH_FILE="$HOME/.germinette_repo_path"
echo "$PWD" > "$REPO_PATH_FILE"
echo -e "${BLUE}📍 Registered repository path: $PWD${NC}"

# Path configuration logic
USER_BIN_DIR="$HOME/.local/bin"
SHELL_CONFIG=""

# Detect Shell
if [[ "$SHELL" == */zsh ]]; then
    SHELL_CONFIG="$HOME/.zshrc"
elif [[ "$SHELL" == */bash ]]; then
    SHELL_CONFIG="$HOME/.bashrc"
else
    SHELL_CONFIG="$HOME/.profile"
fi

echo -e "${BLUE}🔍 Checking PATH configuration for $SHELL...${NC}"

# Check if the export line already exists in the config file
# We check the file content, not just the current PATH env var, 
# because the user might just need to source the file.
if grep -Fxq 'export PATH="$HOME/.local/bin:$PATH"' "$SHELL_CONFIG"; then
    echo -e "${GREEN}👍 PATH is already configured in $SHELL_CONFIG.${NC}"
else
    echo -e "${YELLOW}🔧 Adding $USER_BIN_DIR to PATH in $SHELL_CONFIG...${NC}"
    echo "" >> "$SHELL_CONFIG"
    echo "# Germinette PATH" >> "$SHELL_CONFIG"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_CONFIG"
    echo -e "${GREEN}✅ Added!${NC}"
    echo -e "${YELLOW}⚠️  IMPORTANT: Please run the following command now:${NC}"
    echo -e "   source $SHELL_CONFIG"
fi

# Cleanup
echo -e "${BLUE}🧹 Cleaning up build artifacts...${NC}"
rm -rf build/ dist/ *.egg-info
echo -e "${GREEN}✨ Cleaned!${NC}"

echo -e "\n${GREEN}🎉 Done! You are ready to plant some code!${NC}"

# Offer to reload shell
read -p "🔄 Do you want to reload your shell now to apply changes? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}Reloading shell...${NC}"
    exec "$SHELL"
else
    echo -e "${YELLOW}Please run 'source $SHELL_CONFIG' manually or restart your terminal.${NC}"
fi
