%global debug_package %{nil}
%define _buildhost generic-builder

Name:           rebar
Version:        2.6.4
Release:        1%{?dist}
Summary:        Erlang build tool
License:        ASLv2
URL:            https://github.com/rebar/rebar
Source0:        https://github.com/rebar/rebar/archive/%{version}.tar.gz#/rebar-%{version}.tar.gz
BuildRequires:  erlang = 19.3
BuildRequires:  git
Requires:       erlang = 19.3

%description
rebar is an Erlang build tool that makes it easy to compile and test Erlang applications, port drivers and releases.

%prep
%setup -q

%build
./bootstrap

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_bindir}
cp rebar %{buildroot}%{_bindir}/rebar

%files
%{_bindir}/rebar
%license LICENSE
%doc README.md

%changelog
* Tue Oct 29 2024 Mooseable <mooseable@mooseable.com> - 2.6.4-1
- Initial package
