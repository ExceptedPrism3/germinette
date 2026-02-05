#!/bin/bash

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🌱 Installing Germinette...${NC}"

# Install the package
if [[ "$1" == "--home" ]]; then
    echo -e "${BLUE}🏠 Installing in isolated environment (--home)...${NC}"
    
    # Create venv if it doesn't exist
    if [ ! -d ".germinenv" ]; then
        python3 -m venv .germinenv
    fi
    
    # Activate and install
    source .germinenv/bin/activate
    pip install .
    
    # Ensure local bin exists
    mkdir -p "$HOME/.local/bin"
    
    # Symlink the binary to be accessible globally
    # We use the absolute path to the venv binary
    VENV_BIN="$PWD/.germinenv/bin/germinette"
    TARGET_LINK="$HOME/.local/bin/germinette"
    
    echo -e "${BLUE}🔗 Linking $VENV_BIN to $TARGET_LINK...${NC}"
    ln -sf "$VENV_BIN" "$TARGET_LINK"
    
else
    # Standard user install
    pip install --user .
fi

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Installation failed.${NC}"
    echo -e "${YELLOW}Please open an issue on GitHub: https://github.com/ExceptedPrism3/germinette/issues${NC}"
    exit 1
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
