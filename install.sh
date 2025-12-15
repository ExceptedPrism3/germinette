#!/bin/bash

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🌱 Installing Germinette...${NC}"

# Install the package
pip install --user .

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Installation failed.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Installation successful!${NC}"

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
