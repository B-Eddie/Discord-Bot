#!/bin/bash

# Specify the Python version you want to install
PYTHON_VERSION="3.9.2"

# Download and extract the specified Python version
curl -O https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz
tar -xzf Python-$PYTHON_VERSION.tgz

# Build and install the specified Python version
cd Python-$PYTHON_VERSION
./configure --prefix=$HOME/python
make
make install

# Go back to the project root directory
cd ..

# Add the newly installed Python version to the PATH
export PATH=$HOME/python/bin:$PATH

# Install project dependencies
pip install -r requirements.txt
