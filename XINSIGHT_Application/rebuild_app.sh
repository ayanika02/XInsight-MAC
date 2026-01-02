#!/bin/bash

echo "=================================="
echo "XInsight App Rebuild Script"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the app name from dist folder
APP_NAME="XInsight.app"
DIST_PATH="dist/$APP_NAME"

echo "Step 1: Checking icon file..."
if [ ! -f "IDEAS-TIH.icns" ]; then
    echo -e "${RED}ERROR: IDEAS-TIH.icns not found in current directory${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Icon file found${NC}"
echo ""

echo "Step 2: Killing any running Streamlit processes..."
# Kill any streamlit processes
pkill -f streamlit
# Kill any processes on port 8502
lsof -ti:8502 | xargs kill -9 2>/dev/null
sleep 2
echo -e "${GREEN}✓ Processes cleared${NC}"
echo ""

echo "Step 3: Removing old app from Applications..."
if [ -d "/Applications/$APP_NAME" ]; then
    rm -rf "/Applications/$APP_NAME"
    echo -e "${GREEN}✓ Old app removed from Applications${NC}"
else
    echo "  No existing app in Applications"
fi
echo ""

echo "Step 4: Cleaning build directories..."
rm -rf build dist
echo -e "${GREEN}✓ Build directories cleaned${NC}"
echo ""

echo "Step 5: Building new app..."
python setup.py py2app
if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Build failed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ App built successfully${NC}"
echo ""

echo "Step 6: Verifying icon in app bundle..."
if [ -f "$DIST_PATH/Contents/Resources/IDEAS-TIH.icns" ]; then
    echo -e "${GREEN}✓ Icon file found in app bundle${NC}"
else
    echo -e "${YELLOW}⚠ Warning: Icon file not found in app bundle${NC}"
fi
echo ""

echo "Step 7: Copying app to Applications..."
cp -R "$DIST_PATH" /Applications/
if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Failed to copy app to Applications${NC}"
    exit 1
fi
echo -e "${GREEN}✓ App copied to Applications${NC}"
echo ""

echo "Step 8: Clearing macOS icon cache..."
# Clear icon cache - this is crucial for icon to show up
sudo rm -rf /Library/Caches/com.apple.iconservices.store
rm -rf ~/Library/Caches/com.apple.iconservices.store
killall Dock
killall Finder
echo -e "${GREEN}✓ Icon cache cleared (Dock will restart)${NC}"
echo ""

echo "Step 9: Updating launch services database..."
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f "/Applications/$APP_NAME"
echo -e "${GREEN}✓ Launch services updated${NC}"
echo ""

echo "=================================="
echo -e "${GREEN}Build Complete!${NC}"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Wait 10-15 seconds for the Dock to fully restart"
echo "2. Open Applications folder"
echo "3. Drag XInsight.app to your Dock"
echo "4. If icon still doesn't show, restart your Mac"
echo ""
echo "To run the app:"
echo "  - Double-click from Applications"
echo "  - Or click the Dock icon"
echo ""
echo "To quit properly:"
echo "  - Right-click Dock icon → Quit"
echo "  - Or press Cmd+Q when app is active"
echo ""

^X

X

