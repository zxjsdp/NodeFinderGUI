#!/usr/bin/env bash

# This script is used to generate .pyw file automatically
# This script must be called as:
#  scripts/generate_zip.sh

NODEFINDERGUI_ZIP_REPO_PATH='../NodeFinderGUI-Downloads'
UNAMES="$(uname -s)"

# Check if run this script in the right directory
if [ ! -e setup.py ]
then
    echo "Run this script in the same folder with setup.py"
    echo "  Usage: scripts/generate_zip.sh"
    exit
fi

# Import fdi_generator.py to get .pyc bytecode file
echo "Generating .pyc file..."
python -c "import nodefinder_gui.nodefinder_gui"

# Rename .pyc file to .pyw file
echo "Generating .pyw file..."
mv nodefinder_gui/nodefinder_gui.pyc nodefinder_gui/NodeFinderGUI.pyw

mkdir -p NodeFinderGUI

echo "Copying necessary files to NodeFinderGUI..."
cp -rf nodefinder_gui/nodefinder_gui.py nodefinder_gui/NodeFinderGUI.pyw README.md LICENSE CONTRIBUTING.rst CHANGES.rst data NodeFinderGUI

if [[ $UNAMES == 'Linux' ]] || [[ $UNAMES == 'Darwin'  ]]
then
    # Use zip on Linux & Mac OSX
    echo "Zip files on Windows..."
    zip -r NodeFinderGUI.zip NodeFinderGUI
elif [[ $UNAMES == CYGWIN* ]] || [[ $UNAMES == MINGW* ]]
then
    # Use zip on Windows
    echo "Zip files..."
    scripts/zip -r NodeFinderGUI.zip NodeFinderGUI
else
    echo "Unknown Platform! Zip failed!!"
fi

# Move zip file to NodeFinderGUI-Downloads repository
# https://github.com/zxjsdp/NodeFinderGUI-Downloads
if [ -e "$NODEFINDERGUI_ZIP_REPO_PATH/NodeFinderGUI.zip" ]
then
    rm "$NODEFINDERGUI_ZIP_REPO_PATH/NodeFinderGUI.zip"
fi

# Move NodeFinderGUI.zip & NodeFinderGUi.pyw to "../NodeFinderGUI-Downloads"
mv NodeFinderGUI.zip "$NODEFINDERGUI_ZIP_REPO_PATH/"
mv nodefinder_gui/NodeFinderGUI.pyw "$NODEFINDERGUI_ZIP_REPO_PATH/"

# Cleaning job
echo "Cleaning ..."
rm -rf NodeFinderGUI
if [ -e NodeFinderGUI.zip ]
then
    rm NodeFinderGUI.zip
fi
