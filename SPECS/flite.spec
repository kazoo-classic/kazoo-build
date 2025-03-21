Name:           flite
Version:        2.2
Release:        1%{?dist}
Summary:        Small, fast speech synthesis engine (text-to-speech)
License:        MIT
URL:            https://github.com/festvox/flite/

Source0:        https://github.com/festvox/flite/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}-release.tar.gz
BuildRequires:  texi2html
# texi2pdf
# WARNING see explanation about PDF doc below.
#BuildRequires:  texinfo-tex
BuildRequires:  gcc
BuildRequires:  autoconf automake libtool
BuildRequires:  ed alsa-lib-devel
BuildRequires:  texinfo
BuildRequires:  wget


%description
Flite (festival-lite) is a small, fast run-time speech synthesis engine
developed at CMU and primarily designed for small embedded machines and/or
large servers. Flite is designed as an alternative synthesis engine to
Festival for voices built using the FestVox suite of voice building tools.


%package devel
Summary: Development files for flite
Requires: %{name}%{?_isa} = %{version}-%{release}

%description devel
Development files for Flite, a small, fast speech synthesis engine.

%package voices
Summary: Voice packages for flite
Requires: %{name}%{?_isa} = %{version}-%{release}

%description voices
Additional voice packages for Flite, a small, fast speech synthesis engine.
Include standard American Englis voices.

%prep
%setup -q -n %{name}-%{version}


%build
autoreconf -vif
%configure --enable-shared --with-audio=alsa --disable-static
# This package fails parallel make (thus cannot be built using "_smp_flags")
make
# Add get_voices
make get_voices
# Build documentation
cd doc
# WARNING "make doc" provides a huge PDF file. It was decided not to produce/package it.
#make doc
make flite.html


%install
make install INSTALLBINDIR=%{buildroot}%{_bindir} INSTALLLIBDIR=%{buildroot}%{_libdir}  INSTALLINCDIR=%{buildroot}%{_includedir}/flite

#remove static libraries. Remove and uncomment the %files section if you need them
rm -f %{buildroot}%{_libdir}/*.a

# Create voices dir
mkdir -p %{buildroot}%{_datadir}/%{name}/voices
# Copy voices to voice dir
if [ -d "voices" ]; then
  cp -a voices/* %{buildroot}%{_datadir}/%{name}/voices/
fi


%post -p /sbin/ldconfig


%postun -p /sbin/ldconfig


%files
%license COPYING
%doc ACKNOWLEDGEMENTS README.md doc/html
%{_libdir}/*.so.*
%{_bindir}/*


%files devel
%{_libdir}/*.so
%{_includedir}/flite
# If we need static packages
# %{_libdir}/*.a
# %{_includedir}/flite


%files voices
%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/voices
%{_datadir}/%{name}/voices/*


%changelog
* Wed Mar 19 2025 Mooseable <mooseable@mooseable.com> 2.2-1
- Updated source address to festvox flite github
- added texinfo to buildrequires to build html documentation
- Fixed bogus changelog dates

* Wed Mar  7 2018 Peter Robinson <pbrobinson@fedoraproject.org> 1.3-31
- Add gcc BR, minor spec cleanups

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.3-30
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.3-29
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.3-28
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.3-27
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.3-26
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Fri Jan  8 2016 Peter Lemenkov <lemenkov@gmail.com> - 1.3-25
- Fixed FTBFS in Rawhide
- Remove pre-EPEL6 support

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3-24
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3-23
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3-22
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Mon Jan  6 2014 Rui Matos <rmatos@redhat.com> - 1.3-21
- Resolves: (CVE-2014-0027) flite: insecure temporary file use

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3-20
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3-19
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3-18
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3-17
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Sun Mar 13 2011 Francois Aucamp <faucamp@fedoraproject.org> - 1.3-16
- Added patch declaring explicit libm linking dependency (RHBZ #564899)
- Updated source and URL tags

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3-15
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3-14
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Sat Mar 21 2009 Robert Scheck <robert@fedoraproject.org> - 1.3-13
- Removed moving of non-existing documentation flite directory

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sat Oct 11 2008 Peter Lemenkov <lemenkov@gmail.com> - 1.3-11
- Fix for RHEL 4
 
* Fri Jul 18 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 1.3-10
- fix license tag

* Mon Feb 18 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 1.3-9
- Autorebuild for GCC 4.3

* Tue Nov 14 2006 Francois Aucamp <faucamp@csir.co.za> - 1.3-8
- Added comment to %%build stating why "_smp_flags" isn't used with make

* Mon Nov 13 2006 Francois Aucamp <faucamp@csir.co.za> - 1.3-7
- Modified alsa support patch file to patch "configure.in" instead of "configure"
- Added "autoconf" step to %%build
- Added BuildRequires: autoconf
- Fixed patch backup file suffixes
- Renamed patch files to a more standard format
- Moved header files from /usr/include to /usr/include/flite
- Added -p option to all cp operations (to preserve timestamps)

* Sun Nov 12 2006 Francois Aucamp <faucamp@csir.co.za> - 1.3-6
- Recreated patch to allow shared libraries to build correctly (sharedlibs.patch)
- "flite" and "flite_time" binaries now link to flite shared libraries (sharedlibs.patch)
- Simplified the documentation patch filename
- Modified patch steps in %%prep to create backup files with different suffixes
- Removed "_smp_flags" macro from %%build for all archs

* Fri Oct 20 2006 Francois Aucamp <faucamp@csir.co.za> - 1.3-5
- Modified "build" so that "_smp_flags" is only used for i386 arch

* Tue Oct 10 2006 Francois Aucamp <faucamp@csir.co.za> - 1.3-4
- Removed "_smp_flags" macro from "build" for x86_64 arch

* Tue Sep 26 2006 Francois Aucamp <faucamp@csir.co.za> - 1.3-3
- Added README-ALSA.txt (Source1)
- Removed subpackage: flite-devel-static
- Modified shared libraries patch (Patch0) to prevent building static libraries
- Renamed patch files: Patch0, Patch1

* Tue Sep 26 2006 Francois Aucamp <faucamp@csir.co.za> - 1.3-2
- Added flite 1.3 ALSA patch (Patch2) by Lukas Loehrer - thanks Anthony Green for pointing it out
- Added configure option: --with-audio=alsa
- Added BuildRequires: alsa-lib-devel

* Fri Sep 22 2006 Francois Aucamp <faucamp@csir.co.za> - 1.3-1
- Initial RPM build
