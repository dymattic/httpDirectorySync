# HTTP Directory Sync
___

This tool is a simple GUI application written in python, which enables an easy way of downloading and synchronizing \
remote HTTP Directories with a local copy.

## Features

+ Recursion
+ HTTP Basic Authentication
+ check for local changes
+ save settings
+ remote browser for changing remote directory
+ selectable list of file types

## How to run

### Unix/Linux
1. `git clone https://github.com/dymattic/httpDirectorySync.git`
2. `cd ./httpDirectorySync`
3. Install requirements listed in requirements.txt
4. `python ./main.py`

### Windows
#### Precompiled binary
1. Download the executable https://github.com/dymattic/httpDirectorySync/releases/tag/v0.1-alpha
2. Execute it

#### Compiling binary

For Compiling the binary make sure all Dependencies requirements.txt are satisfied.\
In addition the **pyinstaller** package is required for compiling a binary:\

`pip install pyinstaller`

## Contribute!

You are welcome to
+ **Open Issues**
+ **Open Pull Requests**
+ **Contribute in any other way you might see fit**