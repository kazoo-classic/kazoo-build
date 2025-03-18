%global debug_package %{nil}
%define _buildhost generic-builder

Name:           elixir
Version:        1.5.3
Release:        1%{?dist}
Summary:        A functional meta-programming aware language built on top of the Erlang VM
License:        ASLv2
URL:            https://elixir-lang.org
Source0:        https://github.com/elixir-lang/elixir/archive/v%{version}.tar.gz#/elixir-%{version}.tar.gz
BuildRequires:  erlang = 19.3
BuildRequires:  git
BuildRequires:  rebar = 2.6.4
Requires:       erlang = 19.3
Requires:       rebar = 2.6.4

%description
Elixir is a dynamic, functional language designed for building scalable
and maintainable applications. Elixir leverages the Erlang VM, known
for running low-latency, distributed and fault-tolerant systems.

%prep
%setup -q

%build
# Set UTF-8 locale
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
export LC_CTYPE=en_US.UTF-8

make %{?_smp_mflags}

%install
rm -rf %{buildroot}
make install PREFIX=%{buildroot}/usr

# Fix permissions
find %{buildroot} -type f -exec chmod 644 {} \;
find %{buildroot} -type d -exec chmod 755 {} \;
chmod 755 %{buildroot}%{_bindir}/*
chmod 755 %{buildroot}%{_prefix}/lib/elixir/bin/*

%files
%license LICENSE
%doc README.md

# Binaries in /usr/bin
%{_bindir}/elixir
%{_bindir}/elixirc
%{_bindir}/iex
%{_bindir}/mix

# Man pages
%{_mandir}/man1/elixir.1*
%{_mandir}/man1/elixirc.1*
%{_mandir}/man1/iex.1*
%{_mandir}/man1/mix.1*

# Elixir lib directory structure
%dir %{_prefix}/lib/elixir
%dir %{_prefix}/lib/elixir/bin
%dir %{_prefix}/lib/elixir/lib

# Binaries in lib directory
%{_prefix}/lib/elixir/bin/elixir
%{_prefix}/lib/elixir/bin/elixirc
%{_prefix}/lib/elixir/bin/iex
%{_prefix}/lib/elixir/bin/mix

# Library files
%{_prefix}/lib/elixir/lib/eex/**
%{_prefix}/lib/elixir/lib/elixir/**
%{_prefix}/lib/elixir/lib/ex_unit/**
%{_prefix}/lib/elixir/lib/iex/**
%{_prefix}/lib/elixir/lib/logger/**
%{_prefix}/lib/elixir/lib/mix/**

%changelog
* Tue Oct 29 2024 Mooseable <mooseable@mooseable.com> - 1.5.3-1
- Initial package
