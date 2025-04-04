Summary:    iLBC is a library for the iLBC low bit rate speech codec.
Name:       ilbc2
Version:    0.0.1
Release:    1%{?dist}
License:    Global IP Sound iLBC Public License, v2.0
Group:      System Environment/Libraries
URL:        http://www.soft-switch.org/voipcodecs
BuildRoot:  %{_tmppath}/%{name}-%{version}-root
Source:     http://www.soft-switch.org/downloads/voipcodecs/ilbc-0.0.1.tar.gz
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Docdir:     %{_prefix}/doc

BuildRequires: audiofile-devel
BuildRequires: doxygen
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: libtool

%description
iLBC is a library for the iLBC low bit rate speech codec.

%package devel
Summary:    iLBC development files
Group:      Development/Libraries
Requires:   ilbc2 = %{version}

%description devel
iLBC development files.

%prep
#%setup -q -n ilbc-%{version}
%setup -q -n libilbc

%build
./bootstrap.sh
%configure --enable-doc --disable-static --disable-rpath --libdir=%{_libdir}/ilbc2 --includedir=%{_includedir}/ilbc2
make

%install
%{__rm} -rf %{buildroot}
make install DESTDIR=%{buildroot}
%{__rm} %{buildroot}%{_libdir}/ilbc2/libilbc.la
%{__mkdir} -p %{buildroot}%{_libdir}/pkgconfig/
%{__mv} %{buildroot}%{_libdir}/ilbc2/pkgconfig/ilbc.pc %{buildroot}%{_libdir}/pkgconfig/ilbc2.pc

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc ChangeLog AUTHORS COPYING NEWS README 

%{_libdir}/ilbc2/libilbc.so.*

# %{_datadir}/ilbc

%files devel
%defattr(-,root,root,-)
%doc doc/api
%{_includedir}/ilbc2/ilbc.h
%{_includedir}/ilbc2
%{_libdir}/ilbc2/libilbc.so
%{_libdir}/pkgconfig/ilbc2.pc

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%changelog
* Thu Feb  7 2008 Steve Underwood <steveu@coppice.org> 0.0.1
- First pass