%define _buildhost generic-builder

Name:           kazoo-classic
Version:        4.3
Release:        3%{?dist}
Summary:        Kazoo - Open-Source Cloud Communications Platform
License:        MPL-2.0
URL:            https://github.com/kazoo-classic/kazoo
Source0:        %{name}-%{version}.tar.gz
Source1:        kazoo-configs-core-%{version}.tar.gz
Source2:        pqueue-1.7.0.tar.gz
BuildRequires:  git
BuildRequires:  erlang = 19.3
BuildRequires:  elixir = 1.5.3
BuildRequires:  rebar = 2.6.4
BuildRequires:  make
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  wget
BuildRequires:  ncurses-devel
BuildRequires:  openssl-devel
BuildRequires:  unixODBC-devel
BuildRequires:  curl
BuildRequires:  python2
BuildRequires:  python2-devel
BuildRequires:  expat-devel
Requires:       erlang = 19.3

%description
Kazoo is an open-source, distributed, highly scalable platform designed to provide robust telecom services.

%prep
%setup -q -n kazoo
%setup -T -D -a 1 -n kazoo
%setup -T -D -a 2 -n kazoo

# Set up pqueue
mkdir -p %{_builddir}/kazoo/deps/pqueue
mv %{_builddir}/kazoo/pqueue-1.7.0/* %{_builddir}/kazoo/deps/pqueue/

# Fix Python shebang
find %{_builddir}/kazoo -name '*.py' -type f -exec sed -i '1s|^#!.*python$|#!/usr/bin/env python2|' {} +

%build
# Set locale to UTF-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# Create python symlink if needed
if [ -f /usr/bin/python2 ] && [ ! -f /usr/bin/python ]; then
    ln -sf /usr/bin/python2 /usr/bin/python
fi

# Build pqueue
cd %{_builddir}/kazoo/deps/pqueue
rebar get-deps
rebar compile

# Build Kazoo
cd %{_builddir}/kazoo
make compile-lean
make build-release

%install
rm -rf $RPM_BUILD_ROOT

# Create directory structure
mkdir -p %{buildroot}/opt/kazoo/{bin,lib,releases,sounds,log}
mkdir -p %{buildroot}/opt/kazoo/sounds/{ru/ru,es/es,fr/ca,en/us}
mkdir -p %{buildroot}/etc/kazoo/core
mkdir -p %{buildroot}/usr/sbin
mkdir -p %{buildroot}/usr/lib/systemd/system
mkdir -p %{buildroot}/etc/init.d
mkdir -p %{buildroot}/etc/logrotate.d
mkdir -p %{buildroot}/etc/rsyslog.d
mkdir -p %{buildroot}/etc/security/limits.d
mkdir -p %{buildroot}/usr/share/doc/kazoo-core-%{version}
mkdir -p %{buildroot}/var/log/kazoo

# Install Kazoo
cp -R %{_builddir}/kazoo/_rel/kazoo/* %{buildroot}/opt/kazoo/

# Install config files from kazoo-configs-core
install -m 640 %{_builddir}/kazoo/kazoo-configs-core/core/config.ini %{buildroot}/etc/kazoo/core/
install -m 644 %{_builddir}/kazoo/kazoo-configs-core/core/sys.config %{buildroot}/etc/kazoo/core/

# Install system files
install -m 644 %{_builddir}/kazoo/kazoo-configs-core/system/systemd/* %{buildroot}/usr/lib/systemd/system/
install -m 755 %{_builddir}/kazoo/kazoo-configs-core/system/init.d/* %{buildroot}/etc/init.d/
install -m 644 %{_builddir}/kazoo/kazoo-configs-core/system/logrotate.d/* %{buildroot}/etc/logrotate.d/
install -m 644 %{_builddir}/kazoo/kazoo-configs-core/system/rsyslog.d/* %{buildroot}/etc/rsyslog.d/
install -m 644 %{_builddir}/kazoo/kazoo-configs-core/system/security/limits.d/* %{buildroot}/etc/security/limits.d/
install -m 755 %{_builddir}/kazoo/kazoo-configs-core/system/sbin/* %{buildroot}/usr/sbin/

# Create sup symlink if it doesn't exist in sbin
if [ ! -f %{buildroot}/usr/sbin/sup ]; then
    ln -s /opt/kazoo/bin/sup %{buildroot}/usr/sbin/sup
fi

# Install documentation
install -m 644 %{_builddir}/kazoo/{README.md,LICENSE,VERSION} %{buildroot}/usr/share/doc/kazoo-core-%{version}/

%files
%defattr(-, root, root, -)
# Main application directories
%dir %attr(755, kazoo, daemon) /opt/kazoo
%dir %attr(755, kazoo, daemon) /opt/kazoo/bin
%dir %attr(755, kazoo, daemon) /opt/kazoo/lib
%dir %attr(755, kazoo, daemon) /opt/kazoo/releases
%dir %attr(755, kazoo, daemon) /opt/kazoo/sounds
%dir %attr(755, kazoo, daemon) /opt/kazoo/erts-*
%attr(-, kazoo, daemon) /opt/kazoo/bin/*
%attr(-, kazoo, daemon) /opt/kazoo/lib/*
%attr(-, kazoo, daemon) /opt/kazoo/releases/*
%attr(-, kazoo, daemon) /opt/kazoo/erts-*/*

# Sound directories
%dir %attr(755, kazoo, daemon) /opt/kazoo/sounds/ru/ru
%dir %attr(755, kazoo, daemon) /opt/kazoo/sounds/es/es
%dir %attr(755, kazoo, daemon) /opt/kazoo/sounds/fr/ca
%dir %attr(755, kazoo, daemon) /opt/kazoo/sounds/en/us

# Configuration
%dir %attr(750, root, daemon) /etc/kazoo/core
%attr(640, root, daemon) %config(noreplace) /etc/kazoo/core/config.ini
%attr(644, root, daemon) %config(noreplace) /etc/kazoo/core/sys.config

# System files
%attr(-, root, root) /usr/sbin/*
%attr(644, root, root) /usr/lib/systemd/system/*
%attr(755, root, root) /etc/init.d/*
%attr(644, root, root) %config(noreplace) /etc/logrotate.d/*
%attr(644, root, root) %config(noreplace) /etc/rsyslog.d/*
%attr(644, root, root) %config(noreplace) /etc/security/limits.d/*

# Logs
%dir %attr(777, kazoo, daemon) /var/log/kazoo

# Documentation
%doc %attr(644, root, root) /usr/share/doc/kazoo-core-%{version}/*

%pre
# Create kazoo user if it doesn't exist
if ! /usr/bin/getent passwd kazoo >/dev/null 2>&1; then
    /usr/sbin/useradd -r -g daemon -d /opt/kazoo -s /sbin/nologin kazoo
fi

%post
/sbin/ldconfig
systemctl daemon-reload
systemctl enable kazoo-applications

# Set proper permissions
chown -R kazoo:daemon /opt/kazoo
chmod 750 /etc/kazoo/core
chmod 640 /etc/kazoo/core/config.ini
chmod 644 /etc/kazoo/core/sys.config
chmod 755 /var/log/kazoo

%postun
/sbin/ldconfig
if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
    systemctl disable kazoo-applications
    /usr/sbin/userdel kazoo
    rm -f /usr/lib/systemd/system/kazoo-applications.service
    systemctl daemon-reload
    rm -rf /opt/kazoo
    rm -rf /var/log/kazoo
fi

%changelog
* Fri Mar 14 2025 Mooseable <mooseable@mooseable.com> - 4.3-3
- Removed erroneous file copy
- Removed deletion of /etc/kazoo on uninstall
- Added service file cleanup and daemon-reload

* Fri Mar 14 2025 Mooseable <mooseable@mooseable.com> - 4.3-2
- Updated kazoo-applications script to better detect that kazoo is running

* Fri Oct 18 2024 Mooseable <mooseable@mooseable.com> - 4.3-1
- Updated directory structure and permissions
- Added proper configuration file handling
- Fixed user/group permissions for security
- Added sound directories
- Added logging directory with proper permissions
