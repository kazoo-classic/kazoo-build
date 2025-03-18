# Kazoo Build

This repository contains platform specific builds. The main branch will always target the current recommended OS.
It leverages Mock to create clean build environments every time.

## Requirements

### Install required packages first

```bash
dnf update -y; dnf upgrade -y
dnf install epel-release -y
dnf install git rpm-build mock tar createrepo_c -y
```

### Clone this repo into /opt/rpmbuid

```bash
cd /opt
git clone URL-TBD
```

### Compile the Source RPMs

```bash
cd /opt/rpmbuild
./build-srpm-all.sh
```

### Build the RPMs

```bash
cd /opt/rpmbuild
./build-rpm-all.sh
```

