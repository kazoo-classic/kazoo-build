# Based off [Copyright 2020 Adrien Vergé](https://github.com/adrienverge/)

# Do not include debuginfo symlinks from /usr/lib/.build-id because they
# conflict with other erlang packages:
%define _build_id_links none
# Needed to avoid build error: No build ID note found in [...].o
%undefine _missing_build_ids_terminate_build

Name:          couchdb
Version:       3.0.1
Release:       1%{?dist}
Summary:       A document database server, accessible via a RESTful JSON API
Group:         Applications/Databases
License:       Apache
URL:           http://couchdb.apache.org/
Source0:       couchdb-%{version}.tar.gz
Source1:       couchdb.service
Source2:       couchdb
Source3:       ibrowse-4.4.0.tar.gz
Source4:       couchdb-config-2.1.7.tar.gz
Source5:       couchdb-b64url-1.0.2.tar.gz
Source6:       couchdb-ets-lru-1.1.0.tar.gz
Source7:       couchdb-khash-1.1.0.tar.gz
Source8:       couchdb-snappy-CouchDB-1.0.4.tar.gz
Source9:       couchdb-documentation-3.0.1-RC1.tar.gz
Source10:      couchdb-fauxton-v1.2.4.tar.gz
Source11:      couchdb-folsom-CouchDB-0.8.3.tar.gz
Source12:      couchdb-hyper-CouchDB-2.2.0-6.tar.gz
Source13:      couchdb-jiffy-CouchDB-1.0.4-1.tar.gz
Source14:      couchdb-mochiweb-v2.20.0.tar.gz
Source15:      couchdb-meck-0.8.8.tar.gz
Source16:      couchdb-recon-2.5.0.tar.gz
Source17:      proper-v1.3.tar.gz
Source18:      couchdb-bear-0.8.1.tar.gz
%if 0%{?fedora} >= 33
# Erlang 22 or below is not available anymore on Fedora 33, so use the compiled
# version from https://copr.fedorainfracloud.org/coprs/adrienverge/couchdb/
BuildRequires: erlang = 21.3.8.7
%else
BuildRequires: erlang >= 19, erlang < 23
%endif
BuildRequires: git
BuildRequires: gcc
BuildRequires: gcc-c++
BuildRequires: libicu-devel
BuildRequires: mozjs60-devel
BuildRequires: rebar

Requires: mozjs60
Requires(pre): shadow-utils
Requires(post): systemd
Requires(preun): systemd


%description
Apache CouchDB is a distributed, fault-tolerant and schema-free
document-oriented database accessible via a RESTful HTTP/JSON API.
Among other features, it provides robust, incremental replication
with bi-directional conflict detection and resolution, and is
queryable and indexable using a table-oriented view engine with
JavaScript acting as the default view definition language.


%prep
%setup -q -n couchdb

# Create directories for dependencies
mkdir -p %{_builddir}/couchdb/src/deps
mkdir -p %{_builddir}/couchdb/src/docs
mkdir -p %{_builddir}/couchdb/src/fauxton

# Extract all the dependencies to their correct locations
tar -xzf %{_sourcedir}/ibrowse-4.4.0.tar.gz -C %{_builddir}/couchdb/src/
mv %{_builddir}/couchdb/src/ibrowse-4.4.0 %{_builddir}/couchdb/src/ibrowse

tar -xzf %{_sourcedir}/couchdb-config-2.1.7.tar.gz -C %{_builddir}/couchdb/src/
mv %{_builddir}/couchdb/src/couchdb-config-2.1.7 %{_builddir}/couchdb/src/config

tar -xzf %{_sourcedir}/couchdb-b64url-1.0.2.tar.gz -C %{_builddir}/couchdb/src/
mv %{_builddir}/couchdb/src/couchdb-b64url-1.0.2 %{_builddir}/couchdb/src/b64url

tar -xzf %{_sourcedir}/couchdb-ets-lru-1.1.0.tar.gz -C %{_builddir}/couchdb/src/
mv %{_builddir}/couchdb/src/couchdb-ets-lru-1.1.0 %{_builddir}/couchdb/src/ets_lru

tar -xzf %{_sourcedir}/couchdb-khash-1.1.0.tar.gz -C %{_builddir}/couchdb/src/
mv %{_builddir}/couchdb/src/couchdb-khash-1.1.0 %{_builddir}/couchdb/src/khash

tar -xzf %{_sourcedir}/couchdb-snappy-CouchDB-1.0.4.tar.gz -C %{_builddir}/couchdb/src/
mv %{_builddir}/couchdb/src/couchdb-snappy-CouchDB-1.0.4 %{_builddir}/couchdb/src/snappy

tar -xzf %{_sourcedir}/couchdb-documentation-3.0.1-RC1.tar.gz -C %{_builddir}/couchdb/src/
mv %{_builddir}/couchdb/src/couchdb-documentation-3.0.1-RC1 %{_builddir}/couchdb/src/docs

tar -xzf %{_sourcedir}/couchdb-fauxton-v1.2.4.tar.gz -C %{_builddir}/couchdb/src/
mv %{_builddir}/couchdb/src/couchdb-fauxton-1.2.4 %{_builddir}/couchdb/src/fauxton

tar -xzf %{_sourcedir}/couchdb-folsom-CouchDB-0.8.3.tar.gz -C %{_builddir}/couchdb/src/
mv %{_builddir}/couchdb/src/couchdb-folsom-CouchDB-0.8.3 %{_builddir}/couchdb/src/folsom

tar -xzf %{_sourcedir}/couchdb-hyper-CouchDB-2.2.0-6.tar.gz -C %{_builddir}/couchdb/src/
mv %{_builddir}/couchdb/src/couchdb-hyper-CouchDB-2.2.0-6 %{_builddir}/couchdb/src/hyper

tar -xzf %{_sourcedir}/couchdb-jiffy-CouchDB-1.0.4-1.tar.gz -C %{_builddir}/couchdb/src/
mv %{_builddir}/couchdb/src/couchdb-jiffy-CouchDB-1.0.4-1 %{_builddir}/couchdb/src/jiffy

tar -xzf %{_sourcedir}/couchdb-mochiweb-v2.20.0.tar.gz -C %{_builddir}/couchdb/src/
mv %{_builddir}/couchdb/src/couchdb-mochiweb-2.20.0 %{_builddir}/couchdb/src/mochiweb

tar -xzf %{_sourcedir}/couchdb-meck-0.8.8.tar.gz -C %{_builddir}/couchdb/src/
mv %{_builddir}/couchdb/src/couchdb-meck-0.8.8 %{_builddir}/couchdb/src/meck

tar -xzf %{_sourcedir}/couchdb-recon-2.5.0.tar.gz -C %{_builddir}/couchdb/src/
mv %{_builddir}/couchdb/src/couchdb-recon-2.5.0 %{_builddir}/couchdb/src/recon

tar -xzf %{_sourcedir}/proper-v1.3.tar.gz -C %{_builddir}/couchdb/src/
mv %{_builddir}/couchdb/src/proper-1.3 %{_builddir}/couchdb/src/proper

tar -xzf %{_sourcedir}/couchdb-bear-0.8.1.tar.gz -C %{_builddir}/couchdb/src/
mv %{_builddir}/couchdb/src/couchdb-bear-0.8.1 %{_builddir}/couchdb/src/bear



# Create fake .git dirs for each dependency to make the build system happy
#for dir in %{_builddir}/couchdb/src/*; do
#  if [ -d "$dir" ] && [ "$(basename "$dir")" != "rebar" ]; then
#    mkdir -p "$dir/.git"
#  fi
#done

%build
# Create bin directory if it doesn't exist
mkdir -p %{_builddir}/couchdb/bin

# Create needed directories
mkdir -p %{_builddir}/couchdb/share/docs/html
mkdir -p %{_builddir}/couchdb/share/www

./configure --skip-deps --disable-docs --spidermonkey-version 60

make release %{?_smp_mflags}

# Store databases in /var/lib/couchdb
sed -i 's|\./data\b|%{_sharedstatedir}/%{name}|g' rel/couchdb/etc/default.ini


%install
mkdir -p %{buildroot}/opt
rm rel/couchdb/bin/couchdb.cmd
cp -r rel/couchdb %{buildroot}/opt

install -D -m 755 %{SOURCE2} %{buildroot}%{_bindir}/%{name}

# Have conf in /etc/couchdb, not /opt/couchdb/etc
mkdir -p %{buildroot}%{_sysconfdir}
mv %{buildroot}/opt/couchdb/etc %{buildroot}%{_sysconfdir}/%{name}

install -D -m 644 %{SOURCE1} %{buildroot}/usr/lib/systemd/system/%{name}.service

mkdir -p %{buildroot}%{_sharedstatedir}/%{name}

rmdir %{buildroot}/opt/couchdb/var/log %{buildroot}/opt/couchdb/var


%pre
getent group %{name} >/dev/null || groupadd -r %{name}
getent passwd %{name} >/dev/null || \
  useradd -r -g %{name} -d %{_sharedstatedir}/%{name} -s /sbin/nologin %{name}

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service


%files
/opt/couchdb
%{_bindir}/%{name}

%config %attr(0644, %{name}, %{name}) %{_sysconfdir}/%{name}/default.d/README
%config %attr(0644, %{name}, %{name}) %{_sysconfdir}/%{name}/default.ini
%config %attr(0644, %{name}, %{name}) %{_sysconfdir}/%{name}/local.d/README
%config(noreplace) %attr(0644, %{name}, %{name}) %{_sysconfdir}/%{name}/local.ini
%config(noreplace) %attr(0644, %{name}, %{name}) %{_sysconfdir}/%{name}/vm.args

%dir %attr(0755, %{name}, %{name}) %{_sharedstatedir}/%{name}

/usr/lib/systemd/system/%{name}.service


%changelog
* Fri Mar 21 2025 Mooseable <mooseable@mooseable> 3.1.2-1
- Upgrade to CouchDB 3.1.2 for Kazoo with Erlang 19
- Define rebar path and add Rebar in buildrequires

* Thu Jul 02 2020 Adrien Vergé <adrienverge@gmail.com> 3.1.0-1
- Upgrade to CouchDB 3

* Mon Jun 29 2020 Adrien Vergé <adrienverge@gmail.com> 2.3.1-8
- Rebuild for CentOS 8

* Mon Dec 23 2019 Adrien Vergé <adrienverge@gmail.com> 2.3.1-7
- Improve logging when Systemd wait for CouchDB stop
- Update patch for -couch_ini since pull request

* Mon Nov 25 2019 Adrien Vergé <adrienverge@gmail.com> 2.3.1-6
- Properly wait termination on systemd 'systemctl stop couchdb'

* Fri Nov 01 2019 Adrien Vergé <adrienverge@gmail.com> 2.3.1-5
- Update patch for -couch_ini since pull request
- Support Fedora 31

* Thu Oct 10 2019 Adrien Vergé <adrienverge@gmail.com> 2.3.1-4
- Support CentOS 8

* Mon Oct 7 2019 Adrien Vergé <adrienverge@gmail.com> 2.3.1-3
- Do not include debuginfo symlinks from /usr/lib/.build-id

* Tue Oct 1 2019 Adrien Vergé <adrienverge@gmail.com> 2.3.1-2
- Use couch-js-devel instead of couch-js, and update docs

* Mon Mar 18 2019 Adrien Vergé <adrienverge@gmail.com> 2.3.1-1
- Update to new upstream version
- Use Erlang 21 (previously: 20) for CentOS 7 and Fedora 30+

* Mon Jan 28 2019 Adrien Vergé <adrienverge@gmail.com> 2.3.0-2
- Apply a patch to add snooze_period_ms for finer tuning, see https://github.com/apache/couchdb/pull/1880

* Tue Dec 11 2018 Adrien Vergé <adrienverge@gmail.com> 2.3.0-1
- Update to new upstream version (skip 2.2 that has bugs)
- Customizing args file is now supported upstream

* Mon Sep 24 2018 Adrien Vergé <adrienverge@gmail.com> 2.1.2-2
- Use Erlang 20 (previously: 16)

* Mon Jul 16 2018 Adrien Vergé <adrienverge@gmail.com> 2.1.2-1
- Update to new upstream version
- Build our custom couch-js like described on https://github.com/apache/couchdb-pkg/tree/7768c00/js

* Mon Apr 9 2018 Adrien Vergé <adrienverge@gmail.com> 2.1.1-2
- Increase number of open file descriptors

* Tue Dec 5 2017 Adrien Vergé <adrienverge@gmail.com> 2.1.1-1
- Update to new upstream version

* Fri Oct 6 2017 Adrien Vergé <adrienverge@gmail.com> 2.1.0-2
- Increase number of open file descriptors

* Tue Sep 5 2017 Adrien Vergé <adrienverge@gmail.com> 2.1.0-1
- Update to new upstream version

* Sat Jul 15 2017  Adrien Vergé <adrienverge@gmail.com> 2.0.0-5
- Remove patch https://github.com/apache/couchdb-couch/pull/194/commits/9970f18
- Rebuild to fix view doc error in Fedora 26

* Sat Dec 3 2016 Adrien Vergé <adrienverge@gmail.com> 2.0.0-4
- Improve signal forwarding (both SIGINT and SIGTERM)

* Mon Sep 26 2016 Adrien Vergé <adrienverge@gmail.com> 2.0.0-3
- Forward signals received by launcher script

* Sat Sep 24 2016 Adrien Vergé <adrienverge@gmail.com> 2.0.0-2
- Provide a launcher script in /usr/bin

* Sat Sep 24 2016 Adrien Vergé <adrienverge@gmail.com> 2.0.0-1
- Update to stable version 2.0.0
- Update patch to take config files from environment
- Remove unneeded systemd BuildRequires

* Fri Sep 9 2016 Adrien Vergé <adrienverge@gmail.com> 2.0.0RC4-8
- Add patch to take config files from environment

* Thu Sep 8 2016 Adrien Vergé <adrienverge@gmail.com> 2.0.0RC4-7
- Store data in /var/lib/couchdb instead of /opt/couchdb/data
- Remove unneeded BuildRequires
- Remove unused /opt/couchdb/var/log dir

* Fri Sep 2 2016 Adrien Vergé <adrienverge@gmail.com> 2.0.0RC4-6
- Patch https://github.com/apache/couchdb-couch/pull/194/commits/9970f18

* Thu Sep 1 2016 Adrien Vergé <adrienverge@gmail.com> 2.0.0RC4-5
- Restore `--disable-docs` because they take 12 MiB

* Thu Sep 1 2016 Adrien Vergé <adrienverge@gmail.com> 2.0.0RC4-4
- Don't install `npm` because Fauxton is already built
- Remove `--disable-docs` because they are already built

* Thu Sep 1 2016 Adrien Vergé <adrienverge@gmail.com> 2.0.0RC4-3
- Use dist version from Apache instead of git sources
- Remove unneeded Requires
- Remove unneeded BuildRequires `help2man`

* Wed Aug 31 2016 Adrien Vergé <adrienverge@gmail.com> 2.0.0RC4-2
- Put conf files in /etc/couchdb instead of /opt/couchdb/etc

* Wed Aug 31 2016 Adrien Vergé <adrienverge@gmail.com> 2.0.0RC4-1
- Initial RPM release