#!/bin/bash
# Build SRPM packages using a shared configuration file
set -e  # Exit on error

# Load configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/build-config.json"
if [ ! -f "$CONFIG_FILE" ]; then
  echo "Error: Configuration file $CONFIG_FILE not found"
  exit 1
fi

# Parse command line arguments
TARGET_PACKAGE=""
if [ $# -ge 1 ]; then
  TARGET_PACKAGE="$1"
  echo "Target package specified: $TARGET_PACKAGE"
fi

# Check if jq is installed
if ! command -v jq &> /dev/null; then
  echo "Error: jq is required but not installed. Please install jq package."
  exit 1
fi

# Extract paths from config
RPMBUILD_DIR=$(jq -r '.rpmbuild_dir' "$CONFIG_FILE")
TEMP_DIR=$(jq -r '.temp_dir' "$CONFIG_FILE")
SPEC_DIR="${RPMBUILD_DIR}/SPECS"
SOURCES_DIR="${RPMBUILD_DIR}/SOURCES"
SRPMS_DIR="${RPMBUILD_DIR}/SRPMS"

# Create a local repo meta
echo "Creating local repo metadata..."
createrepo_c ${RPMBUILD_DIR}/RPMS/

# Set up RPM build environment
echo "Setting up RPM build environment..."
mkdir -p ${RPMBUILD_DIR}/{SOURCES,SPECS,SRPMS,RPMS}

# Empty SRPMS dir
mkdir -p ${SRPMS_DIR}

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

# Function to handle git repositories
handle_git_repo() {
  local repo_name="$1"
  local repo_url="$2"
  local branch="$3"
  local tarball_name="$4"
  
  echo "Processing $repo_name from $repo_url (branch: $branch)..."
  
  local repo_path="${TEMP_DIR}/${repo_name}"
  
  if [ ! -d "$repo_path" ]; then
    rm -rf "$repo_path"
    git clone "$repo_url" "$repo_path"
    if [ -n "$branch" ] && [ "$branch" != "master" ]; then
      (cd "$repo_path" && git checkout "$branch")
    fi
  else
    echo "Updating $repo_name..."
    (cd "$repo_path" && git reset --hard HEAD && git pull)
  fi
  
  tar -czf "${SOURCES_DIR}/${tarball_name}" -C "$TEMP_DIR" "$repo_name"
}

# Function to build an SRPM from a spec file
build_srpm() {
  local spec_file="$1"
  echo "Building SRPM from ${spec_file}..."
  rpmbuild --define "_topdir ${RPMBUILD_DIR}" --define "_buildhost generic-builder" -bs "${SPEC_DIR}/${spec_file}"
}

# Function to check if a package should be processed
should_process_package() {
  local package_name="$1"
  local package_enabled="$2"
  
  if [ "$package_enabled" != "true" ]; then
    return 1
  fi
  
  if [ -n "$TARGET_PACKAGE" ] && [ "$package_name" != "$TARGET_PACKAGE" ]; then
    return 1
  fi
  
  return 0
}

# Main script execution starts here

# Process all packages defined in config
PACKAGE_COUNT=$(jq '.packages | length' "$CONFIG_FILE")

echo "Found $PACKAGE_COUNT packages in configuration"
if [ -n "$TARGET_PACKAGE" ]; then
  # Verify the target package exists in the config
  PACKAGE_EXISTS=$(jq -r ".packages[] | select(.name == \"$TARGET_PACKAGE\") | .name" "$CONFIG_FILE")
  if [ -z "$PACKAGE_EXISTS" ]; then
    echo "Error: Package '$TARGET_PACKAGE' not found in configuration"
    exit 1
  fi
fi

# Download all source files first
echo "Downloading sources..."
cd "$SOURCES_DIR"

for i in $(seq 0 $(($PACKAGE_COUNT - 1))); do
  PACKAGE_NAME=$(jq -r ".packages[$i].name" "$CONFIG_FILE")
  PACKAGE_ENABLED=$(jq -r ".packages[$i].enabled" "$CONFIG_FILE")
  
  # Skip if we shouldn't process this package
  if ! should_process_package "$PACKAGE_NAME" "$PACKAGE_ENABLED"; then
    echo "Skipping package: $PACKAGE_NAME"
    continue
  fi
  
  echo "Preparing sources for: $PACKAGE_NAME"
  
  # Process regular sources
  SOURCE_COUNT=$(jq ".packages[$i].sources | length" "$CONFIG_FILE")
  if [ "$SOURCE_COUNT" -gt 0 ]; then
    for j in $(seq 0 $(($SOURCE_COUNT - 1))); do
      SOURCE_FILE=$(jq -r ".packages[$i].sources[$j].file" "$CONFIG_FILE")
      SOURCE_URL=$(jq -r ".packages[$i].sources[$j].url" "$CONFIG_FILE")
      
      echo "  Downloading: $SOURCE_FILE"
      download_source "$SOURCE_URL" "$SOURCE_FILE"
    done
  fi
  
  # Process git repos
  if jq -e ".packages[$i].git_repos" "$CONFIG_FILE" > /dev/null; then
    GIT_REPO_COUNT=$(jq ".packages[$i].git_repos | length" "$CONFIG_FILE")
    
    if [ "$GIT_REPO_COUNT" -gt 0 ]; then
      for j in $(seq 0 $(($GIT_REPO_COUNT - 1))); do
        REPO_NAME=$(jq -r ".packages[$i].git_repos[$j].name" "$CONFIG_FILE")
        REPO_URL=$(jq -r ".packages[$i].git_repos[$j].url" "$CONFIG_FILE")
        BRANCH=$(jq -r ".packages[$i].git_repos[$j].branch" "$CONFIG_FILE")
        OUTPUT=$(jq -r ".packages[$i].git_repos[$j].output" "$CONFIG_FILE")
        
        echo "  Processing git repo: $REPO_NAME"
        handle_git_repo "$REPO_NAME" "$REPO_URL" "$BRANCH" "$OUTPUT"
      done
    fi
  fi
done

# Build SRPMs
echo "Building SRPMs..."
for i in $(seq 0 $(($PACKAGE_COUNT - 1))); do
  PACKAGE_NAME=$(jq -r ".packages[$i].name" "$CONFIG_FILE")
  PACKAGE_ENABLED=$(jq -r ".packages[$i].enabled" "$CONFIG_FILE")
  
  # Skip if we shouldn't process this package
  if ! should_process_package "$PACKAGE_NAME" "$PACKAGE_ENABLED"; then
    continue
  fi
  
  SPEC_FILE=$(jq -r ".packages[$i].spec_file" "$CONFIG_FILE")
  echo "Building SRPM for: $PACKAGE_NAME"
  build_srpm "$SPEC_FILE"
done

if [ -n "$TARGET_PACKAGE" ]; then
  echo "SRPM build process for $TARGET_PACKAGE completed successfully!"
else
  echo "SRPM build process for all enabled packages completed successfully!"
fi

echo "SRPM files are located at: $SRPMS_DIR"
ls -la "$SRPMS_DIR"