Name:           libks
Version:        1.8.2
Release:        1%{?dist}
Summary:        Foundational support for signalwire C products

License:        MIT
URL:            https://github.com/signalwire/libks/
Source0:        libks-1.8.2.tar.gz

# Build dependencies for AlmaLinux 8 (which already has cmake)
BuildRequires:  cmake >= 3.7.2
BuildRequires:  gcc-c++
BuildRequires:  openssl-devel
BuildRequires:  libatomic

%description
Foundational support for signalwire C products
%prep
%setup -q

%build
cmake . -DCMAKE_INSTALL_PREFIX=%{_prefix} -DCMAKE_BUILD_TYPE=Release
make %{?_smp_mflags}


%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}

%files
/usr/lib/libks.so*
%{_includedir}/libks/*
/usr/lib64/pkgconfig/libks.pc
%doc /usr/share/doc/libks/copyright


%changelog
* Fri Mar 21 2025 Mooseable <mooseable@mooseable.com>- 2.0.2-1
- Initial package for libks-2.
