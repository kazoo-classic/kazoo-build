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
git clone https://github.com/kazoo-classic/kazoo-build.git
```

### Compile the Source RPMs

ALL

```bash
cd /opt/rpmbuild
./build-srpm-all.sh
```

OR TARGETED (example: freeswitch)

```bash
cd /opt/rpmbuild
./build-srpm-all.sh freeswitch
```


### Build the RPMs

ALL

```bash
cd /opt/rpmbuild
./build-rpm-all.sh
```

OR TARGETED (example: freeswitch)

```bash
cd /opt/rpmbuild
./build-rpm-all.sh freeswitch
```
