#!/bin/bash

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🗑️  Uninstalling Germinette...${NC}"

# Uninstall package
pip uninstall -y germinette

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Package removed.${NC}"
else
    echo -e "${RED}⚠️  Failed to uninstall package (maybe it wasn't installed?).${NC}"
fi

# Cleanup build artifacts just in case
rm -rf build/ dist/ *.egg-info "$HOME/.germinette_repo_path"

# Remove venv if exists
if [ -d ".germinenv" ]; then
    echo -e "${BLUE}🗑️  Removing virtual environment...${NC}"
    rm -rf .germinenv
fi

# Remove symlink if it exists
if [ -L "$HOME/.local/bin/germinette" ]; then
    echo -e "${BLUE}🗑️  Removing symlink...${NC}"
    rm "$HOME/.local/bin/germinette"
fi

# Shell Config Cleanup
SHELL_CONFIG=""
if [[ "$SHELL" == */zsh ]]; then
    SHELL_CONFIG="$HOME/.zshrc"
elif [[ "$SHELL" == */bash ]]; then
    SHELL_CONFIG="$HOME/.bashrc"
else
    SHELL_CONFIG="$HOME/.profile"
fi

if [ -f "$SHELL_CONFIG" ]; then
    echo -e "${BLUE}🧹 Cleaning up configuration in $SHELL_CONFIG...${NC}"
    # Remove the comment line only. Leaving the export line is safer.
    # We use temporary file to be portable across sed versions (Mac vs Linux)
    grep -v "# Germinette PATH" "$SHELL_CONFIG" > "${SHELL_CONFIG}.tmp" && mv "${SHELL_CONFIG}.tmp" "$SHELL_CONFIG"
    echo -e "${GREEN}✨ Configuration cleaned.${NC}"
    echo -e "${YELLOW}Note: We kept '$HOME/.local/bin' in your PATH as other tools might use it.${NC}"
fi

echo -e "\n${GREEN}👋 Germinette has been removed.${NC}"

# Reload offer
read -p "🔄 Do you want to reload your shell now? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}Reloading shell...${NC}"
    exec "$SHELL"
fi
