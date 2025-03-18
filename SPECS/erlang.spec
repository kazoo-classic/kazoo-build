# Disable automatic debug package creation
%global debug_package %{nil}
%define _buildhost generic-builder

Name:           erlang
Version:        19.3
Release:        2%{?dist}
Summary:        Erlang 19.3
License:        EPL-1.0
URL:            https://www.erlang.org/
Source0:        otp_src_%{version}.tar.gz
Source1:        openssl-1.0.2r.tar.gz
Source2:        fop-2.10-bin.tar.gz

BuildRequires: epel-release
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  glibc-devel
BuildRequires:  ncurses-devel
BuildRequires:  java-1.8.0-openjdk-devel
BuildRequires:  unixODBC-devel
BuildRequires:  perl-interpreter
BuildRequires:  perl-core
BuildRequires:  perl-WWW-Curl
BuildRequires:  autoconf
Requires: epel-release
Requires: perl-WWW-Curl

# Create subpackage
%package devel
Summary:        Development files for Erlang OTP
Requires:       %{name} = %{version}-%{release}

%description
Erlang is a programming language and runtime system for building massively scalable soft real-time systems with requirements on high availability.

%description devel
Development files for Erlang OTP.

%prep
%setup -q -n otp-OTP-%{version}
%setup -T -D -a 1 -n otp-OTP-%{version}
%setup -T -D -a 2 -n otp-OTP-%{version}

%build
# FOP setup
mkdir -p %{_builddir}/fop
mv fop-2.10 %{_builddir}/fop/
export FOP_HOME=%{_builddir}/fop/fop-2.10/fop
export PATH=%{_builddir}/fop/fop-2.10/fop:$PATH
chmod +x %{_builddir}/fop/fop-2.10/fop/fop

# Java setup
export JAVA_HOME=/usr/lib/jvm/java-1.8.0

# OpenSSL build
pushd openssl-1.0.2r
./config --prefix=%{_builddir}/openssl-1.0.2r -fPIC no-shared
make
make install
mkdir -p %{_builddir}/openssl-1.0.2r/lib/pkgconfig
cp *.pc %{_builddir}/openssl-1.0.2r/lib/pkgconfig/
chmod 644 %{_builddir}/openssl-1.0.2r/lib/pkgconfig/*.pc
popd

# Erlang build
export KERL_CONFIGURE_OPTIONS="--with-ssl=%{_builddir}/openssl-1.0.2r"
export LD_LIBRARY_PATH=%{_builddir}/openssl-1.0.2r/lib:$LD_LIBRARY_PATH

./otp_build autoconf
%configure \
    --prefix=%{_prefix} \
    --exec-prefix=%{_exec_prefix} \
    --bindir=%{_bindir} \
    --libdir=%{_libdir} \
    --disable-hipe \
    --enable-threads \
    --enable-smp-support \
    --enable-kernel-poll \
    --enable-dynamic-ssl-lib \
    --with-ssl=%{_builddir}/openssl-1.0.2r

make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
make DESTDIR=$RPM_BUILD_ROOT install

# OpenSSL install
mkdir -p %{buildroot}/usr/local/openssl-1.0.2r
cp -R %{_builddir}/openssl-1.0.2r/* %{buildroot}/usr/local/openssl-1.0.2r/

# FOP install
mkdir -p %{buildroot}/opt/fop
cp -R %{_builddir}/fop/* %{buildroot}/opt/fop/
mkdir -p %{buildroot}%{_bindir}
ln -sf /opt/fop/fop-2.10/fop %{buildroot}%{_bindir}/fop

# Create symlinks for important binaries
mkdir -p %{buildroot}%{_bindir}
for binary in erl erlc escript run_erl to_erl epmd dialyzer typer ct_run; do
    ln -sf %{_libdir}/erlang/bin/$binary %{buildroot}%{_bindir}/$binary
done

%files
%{_bindir}/*
%dir %{_libdir}/erlang
%{_libdir}/erlang/erts-*
%{_libdir}/erlang/bin
%{_libdir}/erlang/lib
%{_libdir}/erlang/misc
%{_libdir}/erlang/releases
%{_libdir}/erlang/usr
/usr/local/openssl-1.0.2r
/opt/fop
%exclude %{_bindir}/fop
%exclude %{_libdir}/erlang/Install

%files devel
%{_bindir}/fop
%dir %{_libdir}/erlang
%{_libdir}/erlang/Install

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%changelog
* Fri Mar 14 2025 Mooseable <mooseable@mooseable.com> - 19.3-2
- Fix wx dependency requirements on install

* Fri Oct 18 2024 Mooseable <mooseable@mooseable.com> - 19.3-1
- Initial RPM release
