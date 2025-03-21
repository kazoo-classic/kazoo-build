#!/bin/bash
# build-all.sh - Script to build all components in the correct order

set -e  # Exit on error

# Requirements:
# dnf install epel-release -y
# dnf install mock wget rpm-build -y
# Helper function to check if a package is installed

is_installed() {
    rpm -q "$1" >/dev/null 2>&1
}

# Create a local repo meta
createrepo_c /opt/rpmbuild/RPMS/

# Helper function to download with overwrite prompt
download_source() {
    local url="$1"
    local output="$2"

    if [ -f "$output" ]; then
        read -p "File $output exists. Overwrite? (y/n): " answer
        case $answer in
            [Yy]* ) wget -O "$output" "$url";;
            * ) echo "Skipping $output";;
        esac
    else
        wget -O "$output" "$url"
    fi
}

# empty build dir
rm -rf /opt/rpmbuild/{SRPMS}

# Set up RPM build environment
mkdir -p /opt/rpmbuild/{SOURCES,SPECS,SRPMS}

# Download source files
cd /opt/rpmbuild/SOURCES
echo "Downloading sources..."

download_source "https://github.com/erlang/otp/archive/OTP-19.3.tar.gz" "otp_src_19.3.tar.gz"
download_source "https://www.openssl.org/source/old/1.0.2/openssl-1.0.2r.tar.gz" "openssl-1.0.2r.tar.gz"
download_source "https://archive.apache.org/dist/xmlgraphics/fop/binaries/fop-2.10-bin.tar.gz" "fop-2.10-bin.tar.gz"
download_source "https://github.com/rebar/rebar/archive/2.6.4.tar.gz" "rebar-2.6.4.tar.gz"
download_source "https://github.com/elixir-lang/elixir/archive/v1.5.3.tar.gz" "elixir-1.5.3.tar.gz"
download_source "https://github.com/okeuday/pqueue/archive/v1.7.0.tar.gz" "pqueue-1.7.0.tar.gz"
download_source "https://www.kamailio.org/pub/kamailio/5.5.7/src/kamailio-5.5.7_src.tar.gz" "kamailio-5.5.7_src.tar.gz"
download_source "https://github.com/google/libphonenumber/archive/refs/tags/v9.0.1.tar.gz" "libphonenumber-9.0.1.tar.gz"

# First, let's clean up existing packages if they exist
echo "Removing existing packages..."
sudo rpm -e erlang-19 rebar elixir --nodeps 2>/dev/null || true

# Build order
echo "Preparing Erlang OTP 19..."
rpmbuild --define "_topdir /opt/rpmbuild" --define "_buildhost generic-builder" -bs /opt/rpmbuild/SPECS/erlang.spec

echo "Preparing Rebar..."
rpmbuild --define "_topdir /opt/rpmbuild" --define "_buildhost generic-builder" -bs /opt/rpmbuild/SPECS/rebar.spec

echo "Preparing Elixir..."
rpmbuild --define "_topdir /opt/rpmbuild" --define "_buildhost generic-builder" -bs /opt/rpmbuild/SPECS/elixir.spec

echo "Downloading kazoo-configs-core from 4.3-classic branch..."
if [ ! -d /tmp/kazoo-configs-core ]; then
    rm -rf /tmp/kazoo-configs-core
    git clone https://github.com/kazoo-classic/kazoo-configs-core.git /tmp/kazoo-configs-core
    cd /tmp/kazoo-configs-core
    git checkout 4.3-classic
    cd ..
    tar -czf /opt/rpmbuild/SOURCES/kazoo-configs-core-4.3.tar.gz -C /tmp kazoo-configs-core
else
    echo "Update kazoo-configs-core..."
    cd /tmp/kazoo-configs-core
    git reset --hard HEAD
    git pull
    tar -czf /opt/rpmbuild/SOURCES/kazoo-configs-core-4.3.tar.gz -C /tmp kazoo-configs-core
fi



echo "Downloading kazoo-core from kazoo-classic..."
if [ ! -d /tmp/kazoo ]; then
    rm -rf /tmp/kazoo
    git clone https://github.com/kazoo-classic/kazoo.git /tmp/kazoo
    tar -czf /opt/rpmbuild/SOURCES/kazoo-classic-4.3.tar.gz -C /tmp kazoo
else
    echo "Update kazoo-core..."
    cd /tmp/kazoo
    git reset --hard HEAD
    git pull
    tar -czf /opt/rpmbuild/SOURCES/kazoo-classic-4.3.tar.gz -C /tmp kazoo
fi


echo "Preparing Kazoo..."
rpmbuild --define "_topdir /opt/rpmbuild" --define "_buildhost generic-builder" -bs /opt/rpmbuild/SPECS/kazoo.spec

## Kamailio

echo "Preparing Kamailio..."
rpmbuild --define "_topdir /opt/rpmbuild" --define "_buildhost generic-builder" -bs /opt/rpmbuild/SPECS/libphonenumber.spec
rpmbuild --define "_topdir /opt/rpmbuild" --define "_buildhost generic-builder" -bs /opt/rpmbuild/SPECS/kamailio.spec

echo "DONE"