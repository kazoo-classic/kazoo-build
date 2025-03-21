Name: libphonenumber
Version: 9.0.1
Release: 1%{?dist}
Summary: Library to handle international phone numbers
# The project itself is ASL 2.0 but contains files from Chromium which are BSD and MIT.
License: ASL 2.0 and BSD and MIT
URL: https://github.com/google/libphonenumber/
Source0: https://github.com/google/%{name}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires: abseil-cpp-devel
BuildRequires: boost-devel
BuildRequires: cmake
BuildRequires: gcc-c++
BuildRequires: gtest-devel
%ifarch %{java_arches}
BuildRequires: java-devel
%endif
BuildRequires: pkgconfig(icu-io)
BuildRequires: protobuf-compiler
BuildRequires: protobuf-devel
BuildRequires: re2-devel

%description
Google's common C++ library for parsing, formatting, storing and validating
international phone numbers.


%package devel
Summary: Development files for %{name}
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: abseil-cpp-devel

%description devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%prep
%autosetup -p1
# Gtest 1.13.0 requires at least C++14; C++17 matches how abseil-cpp is built;
# simply setting -DCMAKE_CXX_STANDARD=17 does not override this in practice.
sed -r -i 's/\b(CMAKE_CXX_STANDARD[[:blank:]]+)11\b/\117/' \
    cpp/CMakeLists.txt tools/cpp/CMakeLists.txt


%build
pushd cpp
%ifarch %{java_arches}
%cmake \
%else
touch src/phonenumbers/test_metadata.h
%cmake -DREGENERATE_METADATA=OFF \
%endif
    -DCMAKE_POSITION_INDEPENDENT_CODE=ON
%cmake_build
popd


%install
pushd cpp
%cmake_install
find %{buildroot} -name '*.a' -delete
find %{buildroot} -name '*.la' -delete
popd


%files
%doc cpp/README
%license cpp/LICENSE
%{_libdir}/libgeocoding.so.8*
%{_libdir}/libphonenumber.so.8*


%files devel
%{_includedir}/phonenumbers
%{_libdir}/libgeocoding.so
%{_libdir}/libphonenumber.so
%{_libdir}/cmake/libphonenumber/


%changelog
* Fri Apr 19 2024 Mooseable <mooseable@mooseable.com> - 9.0.1-1
- Update to version 9.0.1
- Resolves: 

* Fri Apr 19 2024 Packit <hello@packit.dev> - 8.13.35-1
- Update to version 8.13.35
- Resolves: rhbz#2273675

* Mon Mar 25 2024 Packit <hello@packit.dev> - 8.13.33-1
- [maven-release-plugin] prepare release v8.13.33 (Kavitha Keshava)
- Metadata updates for release 8.13.33 (#3414) (kkeshava)
- Update README.md (#3411) (mandlil)
- Mandlil maven update (#3410) (mandlil)
- Resolves rhbz#2269223

* Sun Feb 25 2024 Packit <hello@packit.dev> - 8.13.31-1
- [maven-release-plugin] prepare release v8.13.31 (Mandali Reddy)
- Revert "Kkeshava maven update (#3403)" (#3405) (kkeshava)
- Update java runtime version to support App Engine (#3404) (mandlil)
- Kkeshava maven update (#3403) (kkeshava)
- Metadata updates for release 8.13.31 (#3402) (kkeshava)
- Mandlil maven update (#3399) (mandlil)
- Update README.md (#3400) (mandlil)
- Resolves rhbz#2265930

* Fri Feb 09 2024 Packit <hello@packit.dev> - 8.13.30-1
- [maven-release-plugin] prepare release v8.13.30 (Mandali Reddy)
- Metadata updates for release 8.13.30 (#3398) (mandlil)
- Update README.md (#3397) (kkeshava)
- Kkeshava maven update (#3396) (kkeshava)
- Resolves rhbz#2263484

* Sun Feb 04 2024 Benjamin A. Beasley <code@musicinmybrain.net> - 8.13.29-2
- Rebuilt for abseil-cpp-20240116.0

* Fri Feb 02 2024 Packit <hello@packit.dev> - 8.13.29-1
- [maven-release-plugin] prepare release v8.13.29 (Kavitha Keshava)
- Metadata updates for release 8.13.29 (#3395) (kkeshava)
- Mandlil patch 2 (#3393) (mandlil)
- Update README.md (#3386) (mandlil)
- Mandlil maven update (#3385) (mandlil)
- Resolves rhbz#2258931

* Wed Jan 31 2024 Pete Walter <pwalter@fedoraproject.org> - 8.13.28-7
- Rebuild for ICU 74

* Thu Jan 25 2024 Fedora Release Engineering <releng@fedoraproject.org> - 8.13.28-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_40_Mass_Rebuild

* Sun Jan 21 2024 Benjamin A. Beasley <code@musicinmybrain.net> - 8.13.28-5
- Always build as position-independent code (PIC)

* Sun Jan 21 2024 Fedora Release Engineering <releng@fedoraproject.org> - 8.13.28-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_40_Mass_Rebuild

* Thu Jan 18 2024 Sérgio Basto <sergio@serjux.com> - 8.13.28-3
- add support to protobuf 3.25.1

* Thu Jan 18 2024 Jonathan Wakely <jwakely@redhat.com> - 8.13.28-2
- Rebuild for Boost 1.83.0 again

* Thu Jan 18 2024 Packit <hello@packit.dev> - 8.13.28-1
- [maven-release-plugin] prepare release v8.13.28 (Mandali Reddy)
- Metadata updates for release 8.13.28 (#3383) (mandlil)
- Update README.md (#3356) (mandlil)
- Mandlil maven update (#3348) (mandlil)

* Thu Jan 18 2024 Jonathan Wakely <jwakely@redhat.com> - 8.13.27-2
- Rebuilt for Boost 1.83

* Tue Dec 19 2023 Sérgio M. Basto <sergio@serjux.com> - 8.13.27-1
- [maven-release-plugin] prepare release v8.13.27 (Mandali Reddy)
- Metadata updates for release 8.13.27 (#3346) (rohininidhi)
- Replace uses of `int64` with `int64_t` and similar integer type aliases (#3345) (mandlil)
- Update method phonenumberutil.format to return 'empty' instead of value '0'. (#3305) (mandlil)
- Update README.md (#3304) (kkeshava)
- Kkeshava maven update1 (#3303) (kkeshava)

* Sat Sep 02 2023 Sérgio Basto <sergio@serjux.com> - 8.13.19-2
- We need to build it in the side tag

* Sat Sep 02 2023 Sérgio Basto <sergio@serjux.com> - 8.13.19-1
- Update libphonenumber to 8.13.19 (#2221771)

* Wed Aug 30 2023 Benjamin A. Beasley <code@musicinmybrain.net> - 8.13.15-4
- Rebuilt for abseil-cpp 20230802.0

* Thu Jul 20 2023 Fedora Release Engineering <releng@fedoraproject.org> - 8.13.15-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_39_Mass_Rebuild

* Tue Jul 11 2023 František Zatloukal <fzatlouk@redhat.com> - 8.13.15-2
- Rebuilt for ICU 73.2

* Fri Jun 23 2023 Fedora Release Monitoring <release-monitoring@fedoraproject.org> - 8.13.15-1
- Update to 8.13.15 (#2209210)

* Tue May 16 2023 Sérgio Basto <sergio@serjux.com> - 8.13.11-1
- Update libphonenumber to 8.13.11

* Thu Mar 23 2023 Sérgio Basto <sergio@serjux.com> - 8.12.57-8
- Rebuilt for abseil-cpp

* Mon Feb 20 2023 Jonathan Wakely <jwakely@redhat.com> - 8.12.57-7
- Rebuilt for Boost 1.81

* Mon Jan 30 2023 Benjamin A. Beasley <code@musicinmybrain.net> - 8.12.57-6
- Correctly build as C++17 instead of C++11 for gtest-1.13.0, which needs C++14

* Thu Jan 19 2023 Fedora Release Engineering <releng@fedoraproject.org> - 8.12.57-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_38_Mass_Rebuild

* Sat Dec 31 2022 Pete Walter <pwalter@fedoraproject.org> - 8.12.57-4
- Rebuild for ICU 72

* Tue Dec 06 2022 Sérgio Basto <sergio@serjux.com> - 8.12.57-3
- (#1893839#c53) use ifarch %%{java_arches} to build on i686

* Mon Dec 05 2022 Sérgio Basto <sergio@serjux.com> - 8.12.57-2
- (#2150896) Add requires abseil-cpp-devel in the -devel package

* Thu Nov 03 2022 Sérgio Basto <sergio@serjux.com> - 8.12.57-1
- Update libphonenumber to 8.12.57 (#1893839)

* Mon Aug 01 2022 Frantisek Zatloukal <fzatlouk@redhat.com> - 8.12.11-15
- Rebuilt for ICU 71.1

* Thu Jul 21 2022 Fedora Release Engineering <releng@fedoraproject.org> - 8.12.11-14
- Rebuilt for https://fedoraproject.org/wiki/Fedora_37_Mass_Rebuild

* Wed May 04 2022 Thomas Rodgers <trodgers@redhat.com> - 8.12.11-13
- Rebuilt for Boost 1.78

* Thu Jan 20 2022 Fedora Release Engineering <releng@fedoraproject.org> - 8.12.11-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_36_Mass_Rebuild

* Fri Nov 05 2021 Adrian Reber <adrian@lisas.de> - 8.12.11-11
- Rebuilt for protobuf 3.19.0

* Tue Oct 26 2021 Adrian Reber <adrian@lisas.de> - 8.12.11-10
- Rebuilt for protobuf 3.18.1

* Fri Aug 06 2021 Jonathan Wakely <jwakely@redhat.com> - 8.12.11-9
- Rebuilt for Boost 1.76

* Thu Jul 22 2021 Fedora Release Engineering <releng@fedoraproject.org> - 8.12.11-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild

* Thu May 20 2021 Pete Walter <pwalter@fedoraproject.org> - 8.12.11-7
- Rebuild for ICU 69

* Wed May 19 2021 Pete Walter <pwalter@fedoraproject.org> - 8.12.11-6
- Rebuild for ICU 69

* Tue Mar 30 2021 Jonathan Wakely <jwakely@redhat.com> - 8.12.11-5
- Rebuilt for removed libstdc++ symbol (#1937698)

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 8.12.11-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Fri Jan 22 2021 Jonathan Wakely <jwakely@redhat.com> - 8.12.11-3
- Rebuilt for Boost 1.75

* Wed Jan 13 16:57:48 CET 2021 Adrian Reber <adrian@lisas.de> - 8.12.11-2
- Rebuilt for protobuf 3.14

* Fri Oct 30 2020 Nikhil Jha <hi@nikhiljha.com> - 8.12.11-1
- Update to 8.12.11

* Thu Sep 24 2020 Adrian Reber <adrian@lisas.de> - 8.12.8-2
- Rebuilt for protobuf 3.13

* Thu Aug 20 2020 Torrey Sorensen <sorensentor@tuta.io> - 8.12.8-1
- Update to 8.12.8

* Wed Aug 05 2020 Peter Robinson <pbrobinson@fedoraproject.org> - 8.12.7-1
- Update to 8.12.7

* Sat Aug 01 2020 Fedora Release Engineering <releng@fedoraproject.org> - 8.12.3-5
- Second attempt - Rebuilt for
  https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Tue Jul 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 8.12.3-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Sun Jun 14 2020 Adrian Reber <adrian@lisas.de> - 8.12.3-3
- Rebuilt for protobuf 3.12

* Sat May 30 2020 Jonathan Wakely <jwakely@redhat.com> - 8.12.3-2
- Rebuilt for Boost 1.73

* Tue May 19 2020 Nikhil Jha <hi@nikhiljha.com> - 8.12.3-1
- Release 8.12.3

* Tue Mar 31 2020 Nikhil Jha <hi@nikhiljha.com> - 8.12.1-1
- Rebuild for ICU 67

* Tue Mar 31 2020 Nikhil Jha <hi@nikhiljha.com> - 8.12.1-1
- Release 8.12.1

* Wed Mar 25 2020 Nikhil Jha <hi@nikhiljha.com> - 8.12.0-1
- Release 8.12.0

* Fri Dec 27 2019 Anthony Messina <amessina@messinet.com> - 8.11.1-1
- Release 8.11.1

* Sat Oct 05 2019 Anthony Messina <amessina@messinet.com> - 8.10.20-1
- Release 8.10.20

* Wed Jul 31 2019 Anthony Messina <amessina@messinet.com> - 8.10.15-1
- Release 8.10.15

* Fri Apr 19 2019 Anthony Messina <amessina@messinet.com> - 8.10.10-1
- Release 8.10.10

* Sat Feb 16 2019 Anthony Messina <amessina@messinet.com> - 8.10.5-1
- Release 8.10.5

* Fri Oct 26 2018 Anthony Messina <amessina@messinet.com> - 8.9.16-1
- Release 8.9.16

* Sun Aug 19 2018 Anthony Messina <amessina@messinet.com> - 8.9.11-1
- Release 8.9.11
- Refs #100 https://fedoraproject.org/wiki/Changes/Removing_ldconfig_scriptlets
- Refs #103 https://fedoraproject.org/wiki/Changes/Remove_GCC_from_BuildRoot

* Sat Apr 28 2018 Anthony Messina <amessina@messinet.com> - 8.9.4-1
- Release 8.9.4

* Sat Apr 07 2018 Anthony Messina <amessina@messinet.com> - 8.9.3-1
- Release 8.9.3
- https://fedoraproject.org/wiki/Changes/Removing_ldconfig_scriptlets: Refs #100

* Wed Jan 17 2018 Anthony Messina <amessina@messinet.com> - 8.8.9-1
- Initial RPM based on Gil Cattaneo's spec file
  https://gil.fedorapeople.org/libphonenumber.spec
  https://bugzilla.redhat.com/show_bug.cgi?id=1200115
