%global commit0 d02737f7eab1e17a7748fbe550dd982e3808525d
%global date 20221227
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})
#global tag %{version}

# buildforkernels macro hint: when you build a new version or a new release
# that contains bugfixes or other improvements then you must disable the
# "buildforkernels newest" macro for just that build; immediately after
# queuing that build enable the macro again for subsequent builds; that way
# a new akmod package will only get build when a new one is actually needed
%define buildforkernels akmod

%global debug_package %{nil}

%global mok_algo sha512
%global mok_key /usr/src/akmods/mok.key
%global mok_der /usr/src/akmods/mok.der

%define __spec_install_post \
  %{__arch_install_post}\
  %{__os_install_post}\
  %{__mod_install_post}

%define __mod_install_post \
  if [ $kernel_version ]; then \
    find %{buildroot} -type f -name '*.ko' | xargs %{__strip} --strip-debug; \
    if [ -f /usr/src/akmods/mok.key ] && [ -f /usr/src/akmods/mok.der ]; then \
      find %{buildroot} -type f -name '*.ko' | xargs echo; \
      find %{buildroot} -type f -name '*.ko' | xargs -L1 /usr/lib/modules/${kernel_version%%___*}/build/scripts/sign-file %{mok_algo} %{mok_key} %{mok_der}; \
    fi \
    find %{buildroot} -type f -name '*.ko' | xargs xz; \
  fi

Name:           xpad-noone-kmod
Version:        0
Release:        1%{!?tag:.%{date}git%{shortcommit0}}%{?dist}
Summary:        Original driver for Xbox controllers without Xbox One support
License:        GPLv2
URL:            https://github.com/medusalix/xpad-noone

%if 0%{?tag:1}
Source0:        %{url}/archive/v%{version}.tar.gz#/xpad-noone-%{version}.tar.gz
%else
Source0:        %{url}/archive/%{commit0}.tar.gz#/xpad-noone-%{shortcommit0}.tar.gz
%endif

# get the needed BuildRequires (in parts depending on what we build for)
BuildRequires:  kmodtool

# kmodtool does its magic here
%{expand:%(kmodtool --target %{_target_cpu} --repo negativo17.org --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null) }

%description
Original linux kernel driver for Xbox controllers without Xbox One support.

%prep
# error out if there was something wrong with kmodtool
%{?kmodtool_check}
# print kmodtool output for debugging purposes:
kmodtool  --target %{_target_cpu}  --repo negativo17.org --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null

%if 0%{?tag:1}
%autosetup -p1 -n xpad-noone-%{version}
%else
%autosetup -p1 -n xpad-noone-%{commit0}
%endif

for kernel_version in %{?kernel_versions}; do
    mkdir _kmod_build_${kernel_version%%___*}
    cp -fr bus driver transport Kbuild _kmod_build_${kernel_version%%___*}
done

%build
for kernel_version in %{?kernel_versions}; do
    pushd _kmod_build_${kernel_version%%___*}/
        %make_build -C "${kernel_version##*___}" M=$(pwd) VERSION="v%{version}" modules
    popd
done

%install
for kernel_version in %{?kernel_versions}; do
    mkdir -p %{buildroot}/%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/
    install -p -m 0755 _kmod_build_${kernel_version%%___*}/*.ko \
        %{buildroot}/%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/
done
%{?akmod_install}

%changelog
* Fri Feb 03 2023 Simone Caronni <negativo17@gmail.com> - 0-1.20221227gitd02737f
- First build.

