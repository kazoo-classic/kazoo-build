#!/bin/bash
#
# Script to build Kazoo and its dependencies in the correct order
# using mock with a custom configuration
# Automatically detects the latest version of each SRPM

set -e  # Exit on any error

# Configuration
MOCK_CONFIG_PATH="/opt/rpmbuild/MOCK/kazoo-alma8.cfg"
SRPMS_DIR="/opt/rpmbuild/SRPMS"
RPMS_DIR="/opt/rpmbuild/RPMS"
RESULTS_DIR="/opt/mock_results"
LOG_DIR="/opt/mock_logs"

# Create directories if they don't exist
mkdir -p $RPMS_DIR $RESULTS_DIR $LOG_DIR

# Function to find the latest version of an SRPM
get_latest_srpm() {
    local package_prefix=$1
    local latest_srpm=$(find $SRPMS_DIR -name "${package_prefix}*.src.rpm" | sort -V | tail -n 1)
    
    if [ -z "$latest_srpm" ]; then
        echo "ERROR: No SRPM found for $package_prefix"
        exit 1
    fi
    
    echo $latest_srpm
}

# Function to build an SRPM and update the local repo
build_package() {
    local srpm=$1
    local package_name=$(basename $srpm .src.rpm)
    
    echo "=========================================================="
    echo "Building package: $package_name"
    echo "Using SRPM: $srpm"
    echo "=========================================================="
    
    # Build the package with mock using the custom config file
    mock -r $MOCK_CONFIG_PATH --resultdir=$RESULTS_DIR/$package_name $srpm
    
    # Check if build was successful
    if [ $? -ne 0 ]; then
        echo "ERROR: Build failed for $package_name"
        exit 1
    fi
    
    # Copy resulting RPMs to our local repo
    cp $RESULTS_DIR/$package_name/*.rpm $RPMS_DIR/
    
    # Update the repo metadata
    createrepo_c --update $RPMS_DIR/
    
    echo "Successfully built $package_name"
    echo ""
}

# Initialize the repository if it doesn't have metadata yet
if [ ! -d "$RPMS_DIR/repodata" ]; then
    echo "Initializing local repository metadata..."
    createrepo_c $RPMS_DIR/
fi

# Find the latest SRPM for each package
ERLANG_SRPM=$(get_latest_srpm "erlang-")
REBAR_SRPM=$(get_latest_srpm "rebar-")
ELIXIR_SRPM=$(get_latest_srpm "elixir-")
KAZOO_SRPM=$(get_latest_srpm "kazoo-classic-")

echo "Found the following SRPMs to build:"
echo "Erlang: $(basename $ERLANG_SRPM)"
echo "Rebar: $(basename $REBAR_SRPM)"
echo "Elixir: $(basename $ELIXIR_SRPM)"
echo "Kazoo: $(basename $KAZOO_SRPM)"
echo ""

# Build packages in order (dependencies first)
# 1. Build erlang
build_package "$ERLANG_SRPM"

# 2. Build rebar
build_package "$REBAR_SRPM"

# 3. Build elixir
build_package "$ELIXIR_SRPM"

# 4. Finally build kazoo
build_package "$KAZOO_SRPM"

echo "=========================================================="
echo "All packages built successfully!"
echo "=========================================================="
echo "RPMs are available in: $RPMS_DIR"
echo "Build logs are available in: $RESULTS_DIR"

# Optional: List all built packages
echo ""
echo "Built packages:"
find $RPMS_DIR -name "*.rpm" | sort

exit 0