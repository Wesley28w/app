#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Updating system and installing dependencies..."
sudo apt-get update
sudo apt-get install -y iproute2 build-essential

# Verify GCC installation
gcc --version

# Set Compiler paths for the current script session: Done in onstart
# export CC=/usr/bin/gcc
# export CXX=/usr/bin/g++

# Create symlink for CUDA if it doesn't already exist
if [ ! -L /usr/lib/x86_64-linux-gnu/libcuda.so ]; then
    echo "Creating libcuda.so symlink..."
    sudo ln -s /usr/lib/x86_64-linux-gnu/libcuda.so.1 /usr/lib/x86_64-linux-gnu/libcuda.so
fi

# Add to LIBRARY_PATH for this session
export LIBRARY_PATH=$LIBRARY_PATH:/usr/lib/x86_64-linux-gnu

# Check GPU status
nvidia-smi

echo "Setup complete!"
