%global with_bundled 1
%global with_debug 0

%if 0%{?with_debug}
%global _find_debuginfo_dwz_opts %{nil}
%global _dwz_low_mem_die_limit 0
%else
%global debug_package   %{nil}
%endif

%define gobuild(o:) GO111MODULE=off go build -buildmode pie -compiler gc -tags=rpm_crashtraceback -ldflags "${LDFLAGS:-} -B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \\n') -extldflags '%__global_ldflags'" -a -v -x %{?**};

%global provider        github
%global provider_tld    com
%global project         cpuguy83
%global repo            go-md2man
# https://github.com/cpuguy83/go-md2man
%global provider_prefix %{provider}.%{provider_tld}/%{project}/%{repo}
%global import_path     %{provider_prefix}
%global commit          1d903dcb749992f3741d744c0f8376b4bd7eb3e1
%global shortcommit     %(c=%{commit}; echo ${c:0:7})

Name:           golang-%{provider}-%{project}-%{repo}
Version:        1.0.7
Release:        11%{?dist}
Summary:        Process markdown into manpages
License:        MIT
URL:            https://%{import_path}
Source0:        https://%{import_path}/archive/%{commit}/%{repo}-%{shortcommit}.tar.gz
# e.g. el6 has ppc64 arch without gcc-go, so EA tag is required
#ExclusiveArch: %%{?go_arches:%%{go_arches}}%%{!?go_arches:%%{ix86} x86_64 %%{arm}}
ExclusiveArch: aarch64 x86_64 ppc64le s390x i686
BuildRequires: %{?go_compiler:compiler(go-compiler)}%{!?go_compiler:golang}
BuildRequires: git
Provides: %{repo} = %{version}-%{release}

%description
%{repo} is a golang tool using blackfriday to process markdown into
manpages.

# Go Toolset
%if 0%{?rhel} > 7
%{?enable_gotoolset110}
%endif

%prep
%autosetup -Sgit -n %{repo}-%{commit}

%build
ln -s vendor src
mkdir -p src/%{provider}.%{provider_tld}/%{project}
ln -s $(pwd) src/%{import_path}
export GOPATH=$(pwd)
GOPATH=$GOPATH %gobuild -o bin/go-md2man %{import_path}

%install
# install go-md2man binary
install -d %{buildroot}%{_bindir}
install -p -m 755 bin/%{repo} %{buildroot}%{_bindir}
# generate man page
install -d -p %{buildroot}%{_mandir}/man1
bin/go-md2man -in=go-md2man.1.md -out=go-md2man.1
install -p -m 644 go-md2man.1 %{buildroot}%{_mandir}/man1

%check

#define license tag if not already defined
%{!?_licensedir:%global license %doc}

%files
%license LICENSE.md
%doc README.md
%{_bindir}/%{repo}
%{_mandir}/man1/*

%changelog
* Mon Aug 06 2018 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.7-11
- disable i686 temporarily

* Mon Aug 06 2018 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.7-10
- use both go-compilers and go-toolset on all rhel arches

* Mon Aug 06 2018 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.7-9
- update distro conditionals and go deps

* Mon Aug 06 2018 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.7-8
- go-toolset and go-compiler needed by all arches

* Mon Aug 06 2018 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.7-7
- use go-compiler for i686 and non-rhel-8

* Mon Aug 06 2018 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.7-6
- re-enable all go_arches

* Mon Aug 06 2018 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.7-5
- temp disable i686

* Mon Aug 06 2018 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.7-4
- use go-toolset-1.10-golang for rhel8

* Tue Jul 31 2018 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.7-3
- build with new scl macros for go-toolset

* Mon Jun 25 2018 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.7-2
- remove devel and unittest packages - unused
- make debuginfo package delve debugger friendly
- build with bundled deps (no need for russross/blackfriday rpm)
- don't execute %%check (doesn't work)
- add go-toolset deps and conditionals

* Tue Sep 19 2017 Jan Chaloupka <jchaloup@redhat.com> - 1.0.7-1
- Bump to upstream 1d903dcb749992f3741d744c0f8376b4bd7eb3e1
  related: #1222796

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.0.4-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.0.4-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Tue Mar 14 2017 Jan Chaloupka <jchaloup@redhat.com> - 1.0.4-7
- Bump to upstream a65d4d2de4d5f7c74868dfa9b202a3c8be315aaa
  related: #1222796

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.0.4-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Jul 21 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.4-5
- https://fedoraproject.org/wiki/Changes/golang1.7

* Sun Mar 06 2016 jchaloup <jchaloup@redhat.com> - 1.0.4-4
- Update list of provided packages
  resolves: #1222796

* Mon Feb 22 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.4-3
- https://fedoraproject.org/wiki/Changes/golang1.6

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.0.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Mon Dec 14 2015 jchaloup <jchaloup@redhat.com> - 1.0.4-1
- Rebase to 1.0.4
  resolves: #1291379

* Thu Sep 10 2015 jchaloup <jchaloup@redhat.com> - 1-13
- Generate man page as well
  related: #1222796

* Sun Aug 30 2015 jchaloup <jchaloup@redhat.com> - 1-12
- Change deps on compiler(go-compiler)
- Update %%build, %%test and main section accordingaly
  related: #1222796

* Sat Aug 29 2015 jchaloup <jchaloup@redhat.com> - 1-11
- Reduce build section after update of go-srpm-macros
- BUILD_ID for debug is needed only for golang compiler
  related: #1222796

* Tue Aug 25 2015 jchaloup <jchaloup@redhat.com> - 1-10
- Provide devel package on rhel7
  related: #1222796

* Thu Aug 20 2015 jchaloup <jchaloup@redhat.com> - 1-9
- Update spec file to spec-2.0
  related: #1222796

* Mon Jul 20 2015 jchaloup <jchaloup@redhat.com> - 1-8
- Add with_* macros

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Tue May 19 2015 jchaloup <jchaloup@redhat.com> - 1-6
- Remove runtime deps of devel on golang
- Polish spec file
  related: #1222796

* Sun May 17 2015 jchaloup <jchaloup@redhat.com> - 1-5
- Add debug info
- Add license
- Update spec file to build on secondary architectures as well
  related: #1222796

* Wed Feb 25 2015 jchaloup <jchaloup@redhat.com> - 1-4
- Bump to upstream 2831f11f66ff4008f10e2cd7ed9a85e3d3fc2bed
  related: #1156492

* Wed Feb 25 2015 jchaloup <jchaloup@redhat.com> - 1-3
- Add commit and shortcommit global variable
  related: #1156492

* Mon Oct 27 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1-2
- Resolves: rhbz#1156492 - initial fedora upload
- quiet setup
- no test files, disable check

* Thu Sep 11 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1-1
- Initial package
