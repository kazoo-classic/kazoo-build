#!/bin/bash
set -e  # Exit on any error

# Load configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/build-config.json"
if [ ! -f "$CONFIG_FILE" ]; then
  echo "Error: Configuration file $CONFIG_FILE not found"
  exit 1
fi

# Check if jq is installed
if ! command -v jq &> /dev/null; then
  echo "Error: jq is required but not installed. Please install jq package."
  exit 1
fi

# Extract paths from config
RPMBUILD_DIR=$(jq -r '.rpmbuild_dir' "$CONFIG_FILE")
MOCK_CONFIG_PATH=$(jq -r '.mock_config_path' "$CONFIG_FILE")
SRPMS_DIR="${RPMBUILD_DIR}/SRPMS"
RPMS_DIR="${RPMBUILD_DIR}/RPMS"
RESULTS_DIR=$(jq -r '.results_dir' "$CONFIG_FILE")
LOG_DIR=$(jq -r '.log_dir' "$CONFIG_FILE")

# Create directories if they don't exist
mkdir -p $RPMS_DIR $RESULTS_DIR $LOG_DIR

# Initialize repository
createrepo_c --update $RPMS_DIR/

# Empty build dir
rm -rf ${RPMBUILD_DIR}/{BUILD,BUILDROOT}
mkdir -p ${RPMBUILD_DIR}/{BUILD,BUILDROOT}

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

# Store package build status
declare -A PACKAGES_TO_BUILD

# Parse command line arguments
parse_arguments() {
    # If specific packages are provided, disable all by default
    if [ $# -gt 0 ]; then
        # Initialize all packages to false
        PACKAGE_COUNT=$(jq '.packages | length' "$CONFIG_FILE")
        for i in $(seq 0 $(($PACKAGE_COUNT - 1))); do
            PKG_NAME=$(jq -r ".packages[$i].name" "$CONFIG_FILE")
            PACKAGES_TO_BUILD["$PKG_NAME"]=false
        done
        
        # Enable only specified packages
        for arg in "$@"; do
            # Check if the provided argument matches any package name
            for i in $(seq 0 $(($PACKAGE_COUNT - 1))); do
                PKG_NAME=$(jq -r ".packages[$i].name" "$CONFIG_FILE")
                if [ "$arg" = "$PKG_NAME" ]; then
                    PACKAGES_TO_BUILD["$PKG_NAME"]=true
                    break
                fi
            done
        done
    else
        # If no arguments, use the enabled flag from config
        PACKAGE_COUNT=$(jq '.packages | length' "$CONFIG_FILE")
        for i in $(seq 0 $(($PACKAGE_COUNT - 1))); do
            PKG_NAME=$(jq -r ".packages[$i].name" "$CONFIG_FILE")
            PKG_ENABLED=$(jq -r ".packages[$i].enabled" "$CONFIG_FILE")
            PACKAGES_TO_BUILD["$PKG_NAME"]=$PKG_ENABLED
        done
    fi
}

# Function to ask yes/no question for each package
ask_interactively() {
    PACKAGE_COUNT=$(jq '.packages | length' "$CONFIG_FILE")
    for i in $(seq 0 $(($PACKAGE_COUNT - 1))); do
        PKG_NAME=$(jq -r ".packages[$i].name" "$CONFIG_FILE")
        read -p "Build $PKG_NAME? (y/n): " response
        case $response in
            [Yy]* ) PACKAGES_TO_BUILD["$PKG_NAME"]=true;;
            [Nn]* ) PACKAGES_TO_BUILD["$PKG_NAME"]=false;;
            * ) echo "Please answer yes or y or no or n."; i=$((i-1));;
        esac
    done
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

# Resolve dependencies
resolve_dependencies() {
    local changed=true
    
    # Repeat until no changes
    while [ "$changed" = true ]; do
        changed=false
        
        # Check every package
        PACKAGE_COUNT=$(jq '.packages | length' "$CONFIG_FILE")
        for i in $(seq 0 $(($PACKAGE_COUNT - 1))); do
            PKG_NAME=$(jq -r ".packages[$i].name" "$CONFIG_FILE")
            
            # If this package is selected to build
            if [ "${PACKAGES_TO_BUILD[$PKG_NAME]}" = true ]; then
                # Check its dependencies
                if jq -e ".packages[$i].depends_on" "$CONFIG_FILE" > /dev/null; then
                    DEPS_COUNT=$(jq ".packages[$i].depends_on | length" "$CONFIG_FILE")
                    
                    if [ "$DEPS_COUNT" -gt 0 ]; then
                        for j in $(seq 0 $(($DEPS_COUNT - 1))); do
                            DEP_NAME=$(jq -r ".packages[$i].depends_on[$j]" "$CONFIG_FILE")
                            
                            # If dependency is not yet selected, select it
                            if [ "${PACKAGES_TO_BUILD[$DEP_NAME]}" != true ]; then
                                PACKAGES_TO_BUILD["$DEP_NAME"]=true
                                changed=true
                                echo "Automatically added dependency: $DEP_NAME (required by $PKG_NAME)"
                            fi
                        done
                    fi
                fi
            fi
        done
    done
}

# Resolve dependencies for selected packages
resolve_dependencies

# Show build plan
echo "Build plan:"
PACKAGE_COUNT=$(jq '.packages | length' "$CONFIG_FILE")
for i in $(seq 0 $(($PACKAGE_COUNT - 1))); do
    PKG_NAME=$(jq -r ".packages[$i].name" "$CONFIG_FILE")
    echo "  $PKG_NAME: $([ "${PACKAGES_TO_BUILD[$PKG_NAME]}" = true ] && echo "YES" || echo "NO")"
done
echo ""

# Check if any package is selected
any_selected=false
for pkg_name in "${!PACKAGES_TO_BUILD[@]}"; do
    if [ "${PACKAGES_TO_BUILD[$pkg_name]}" = true ]; then
        any_selected=true
        break
    fi
done

if [ "$any_selected" = false ]; then
    echo "No packages selected for building. Exiting."
    exit 0
fi

# Find SRPMs for selected packages and build them in correct order
echo "Finding SRPMs for selected packages..."

# Build an ordered list of packages to build
declare -a BUILD_ORDER
build_order_dfs() {
    local pkg_name=$1
    local -A visited
    local -a temp_order
    
    # Define a helper function for DFS
    _dfs() {
        local current=$1
        visited["$current"]=true
        
        # Get dependencies
        local idx=$(jq -r ".packages | map(.name == \"$current\") | index(true)" "$CONFIG_FILE")
        if [ "$idx" != "null" ]; then
            if jq -e ".packages[$idx].depends_on" "$CONFIG_FILE" > /dev/null; then
                local deps_count=$(jq ".packages[$idx].depends_on | length" "$CONFIG_FILE")
                
                if [ "$deps_count" -gt 0 ]; then
                    for j in $(seq 0 $(($deps_count - 1))); do
                        local dep=$(jq -r ".packages[$idx].depends_on[$j]" "$CONFIG_FILE")
                        if [ -z "${visited[$dep]}" ]; then
                            _dfs "$dep"
                        fi
                    done
                fi
            fi
        fi
        
        # Add current package to order after all its dependencies
        temp_order+=("$current")
    }
    
    # Run DFS for the starting package
    _dfs "$pkg_name"
    
    # Return the ordered list
    echo "${temp_order[@]}"
}

# Build complete order for all selected packages
for pkg_name in "${!PACKAGES_TO_BUILD[@]}"; do
    if [ "${PACKAGES_TO_BUILD[$pkg_name]}" = true ]; then
        # Get order for this package and its dependencies
        local_order=($(build_order_dfs "$pkg_name"))
        
        # Add to global order if not already present
        for item in "${local_order[@]}"; do
            if [[ ! " ${BUILD_ORDER[*]} " =~ " ${item} " ]]; then
                BUILD_ORDER+=("$item")
            fi
        done
    fi
done

echo "Build order determined: ${BUILD_ORDER[*]}"

# Find SRPMs and build packages in order
for pkg_name in "${BUILD_ORDER[@]}"; do
    if [ "${PACKAGES_TO_BUILD[$pkg_name]}" = true ]; then
        # Get the prefix to use for finding the SRPM
        SRPM=$(get_latest_srpm "$pkg_name")
        echo "Found $pkg_name SRPM: $(basename $SRPM)"
        
        # Build the package
        build_package "$SRPM"
    fi
done

echo "=========================================================="
echo "All selected packages built successfully!"
echo "=========================================================="
echo "RPMs are available in: $RPMS_DIR"
echo "Build logs are available in: $RESULTS_DIR"

# List all built packages
echo ""
echo "Built packages:"
find $RPMS_DIR -name "*.rpm" -not -name "*.src.rpm" | sort

exit 0