#!/bin/bash
#
# Script to build Kazoo and its dependencies in the correct order
# using mock with a custom configuration
# Automatically detects the latest version of each SRPM
# Can take arguments to select which packages to build

set -e  # Exit on any error

createrepo_c /opt/rpmbuild/RPMS/
createrepo_c --update /opt/rpmbuild/RPMS/


# empty build dir
rm -rf /opt/rpmbuild/{BUILD,BUILDROOT}

# Set up RPM build environment
mkdir -p /opt/rpmbuild/{BUILD,BUILDROOT}

# Configuration
MOCK_CONFIG_PATH="/opt/rpmbuild/MOCK/kazoo-alma8.cfg"
SRPMS_DIR="/opt/rpmbuild/SRPMS"
RPMS_DIR="/opt/rpmbuild/RPMS"
RESULTS_DIR="/opt/mock_results"
LOG_DIR="/opt/mock_logs"

# Package flags (default to false)
BUILD_ERLANG=false
BUILD_REBAR=false
BUILD_ELIXIR=false
BUILD_KAZOO=false
BUILD_KAMAILIO=false

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

# Function to ask yes/no question
ask_yes_no() {
    local question=$1
    local response
    
    while true; do
        read -p "$question (y/n): " response
        case $response in
            [Yy]* ) return 0;;
            [Nn]* ) return 1;;
            * ) echo "Please answer yes or y or no or n.";;
        esac
    done
}

# Parse command line arguments
parse_arguments() {
    for arg in "$@"; do
        case $arg in
            erlang)
                BUILD_ERLANG=true
                ;;
            rebar)
                BUILD_REBAR=true
                ;;
            elixir)
                BUILD_ELIXIR=true
                ;;
            kazoo)
                BUILD_KAZOO=true
                ;;
            kamailio)
                BUILD_KAMAILIO=true
                ;;
            *)
                echo "Warning: Unknown argument '$arg' ignored"
                ;;
        esac
    done
}

# If no arguments provided, ask interactively
ask_interactively() {
    if ask_yes_no "Build Erlang?"; then
        BUILD_ERLANG=true
    fi
    
    if ask_yes_no "Build Rebar?"; then
        BUILD_REBAR=true
    fi
    
    if ask_yes_no "Build Elixir?"; then
        BUILD_ELIXIR=true
    fi
    
    if ask_yes_no "Build Kazoo?"; then
        BUILD_KAZOO=true
    fi

    if ask_yes_no "Build Kamailio?"; then
        BUILD_KAMAILIO=true
    fi
}

# Initialize the repository if it doesn't have metadata yet
if [ ! -d "$RPMS_DIR/repodata" ]; then
    echo "Initializing local repository metadata..."
    createrepo_c $RPMS_DIR/
fi

# Check if any arguments were provided
if [ $# -eq 0 ]; then
    echo "No arguments provided. You will be asked for each package."
    ask_interactively
else
    parse_arguments "$@"
fi

# Show build plan
echo "Build plan:"
echo "  Erlang: $([ "$BUILD_ERLANG" = true ] && echo "YES" || echo "NO")"
echo "  Rebar: $([ "$BUILD_REBAR" = true ] && echo "YES" || echo "NO")"
echo "  Elixir: $([ "$BUILD_ELIXIR" = true ] && echo "YES" || echo "NO")"
echo "  Kazoo: $([ "$BUILD_KAZOO" = true ] && echo "YES" || echo "NO")"
echo "  Kamailio: $([ "$BUILD_KAMAILIO" = true ] && echo "YES" || echo "NO")"
echo ""

# Proceed only if at least one package is selected
if [ "$BUILD_ERLANG" = false ] && [ "$BUILD_REBAR" = false ] && [ "$BUILD_ELIXIR" = false ] && [ "$BUILD_KAZOO" = false ] && [ "$BUILD_KAMAILIO" = false ]; then
    echo "No packages selected for building. Exiting."
    exit 0
fi

# Find the SRPMs for selected packages
if [ "$BUILD_ERLANG" = true ]; then
    ERLANG_SRPM=$(get_latest_srpm "erlang-")
    echo "Found Erlang SRPM: $(basename $ERLANG_SRPM)"
fi

if [ "$BUILD_REBAR" = true ]; then
    REBAR_SRPM=$(get_latest_srpm "rebar-")
    echo "Found Rebar SRPM: $(basename $REBAR_SRPM)"
fi

if [ "$BUILD_ELIXIR" = true ]; then
    ELIXIR_SRPM=$(get_latest_srpm "elixir-")
    echo "Found Elixir SRPM: $(basename $ELIXIR_SRPM)"
fi

if [ "$BUILD_KAZOO" = true ]; then
    KAZOO_SRPM=$(get_latest_srpm "kazoo-classic-")
    echo "Found Kazoo SRPM: $(basename $KAZOO_SRPM)"
fi

if [ "$BUILD_KAMAILIO" = true ]; then
    LIBPHONENUMBER_SRPM=$(get_latest_srpm "libphonenumber-")
    echo "Found Libphonenumber SRPM: $(basename $LIBPHONENUMBER_SRPM)"
    KAMAILIO_SRPM=$(get_latest_srpm "kamailio-")
    echo "Found Kamailio SRPM: $(basename $KAMAILIO_SRPM)"
fi

echo ""

# Build selected packages in order (dependencies first)
if [ "$BUILD_ERLANG" = true ]; then
    build_package "$ERLANG_SRPM"
fi

if [ "$BUILD_REBAR" = true ]; then
    build_package "$REBAR_SRPM"
fi

if [ "$BUILD_ELIXIR" = true ]; then
    build_package "$ELIXIR_SRPM"
fi

if [ "$BUILD_KAZOO" = true ]; then
    build_package "$KAZOO_SRPM"
fi

if [ "$BUILD_KAMAILIO" = true ]; then
    build_package "$LIBPHONENUMBER_SRPM"
    build_package "$KAMAILIO_SRPM"
fi

echo "=========================================================="
echo "All selected packages built successfully!"
echo "=========================================================="
echo "RPMs are available in: $RPMS_DIR"
echo "Build logs are available in: $RESULTS_DIR"

# List all built packages
echo ""
echo "Built packages:"
find $RPMS_DIR -name "*.rpm" | sort

exit 0