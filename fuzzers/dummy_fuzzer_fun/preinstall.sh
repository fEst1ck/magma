#!/bin/bash
set -e

# Update the package list and install necessary dependencies
apt-get update && \
    apt-get install -y \
    build-essential \
    wget \
    cargo \
    git \
    curl \
    lsb-release software-properties-common gnupg

rm -rf /usr/local/bin/clang /usr/local/bin/clang++ /usr/local/bin/llvm*
rm -rf /usr/local/lib/clang
rm -rf /usr/local/include/clang
rm -rf /usr/local/share/clang

# Install LLVM 19
# Download the LLVM installation script
wget https://apt.llvm.org/llvm.sh && \
    chmod +x llvm.sh

# Install LLVM 19 using the script
./llvm.sh 19

# Clean up by removing the installation script
rm llvm.sh

# Set the default clang and clang++ to the installed version
update-alternatives --install /usr/bin/clang clang /usr/bin/clang-19 100 && \
    update-alternatives --install /usr/bin/clang++ clang++ /usr/bin/clang++-19 100

apt remove -y --purge rustc cargo
apt autoremove -y

# Uninstall old Rust
if which rustup; then rustup self uninstall -y; fi

# Install latest Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs > /rustup.sh && \
    sh /rustup.sh -y