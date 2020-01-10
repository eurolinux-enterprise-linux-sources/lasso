%global with_java 0
%global with_php 0
%global with_perl 0
%global with_python 1
%global with_wsf 0

%if %{with_php}
%if "%{php_version}" < "5.6"
%global ini_name     %{name}.ini
%else
%global ini_name     40-%{name}.ini
%endif
%endif

Summary: Liberty Alliance Single Sign On
Name: lasso
Version: 2.5.1
Release: 3%{?dist}
License: GPLv2+
Group: System Environment/Libraries
Source: http://dev.entrouvert.org/lasso/lasso-%{version}.tar.gz
Source2:	lasso.ini
%if %{with_wsf}
BuildRequires: cyrus-sasl-devel
%endif
BuildRequires: gtk-doc, libtool-ltdl-devel
BuildRequires: glib2-devel >= 2.42, swig
Requires: glib2 >= 2.42
BuildRequires: libxml2-devel, xmlsec1-devel, openssl-devel, xmlsec1-openssl-devel
BuildRequires: zlib-devel, check-devel
BuildRequires: libtool autoconf automake
BuildRequires: python-six
Url: http://lasso.entrouvert.org/

patch1: cflags.patch
patch2: validate_idp_list_test.patch
patch3: 0003-Choose-the-Reference-transform-based-on-the-chosen-S.patch
patch4: 0004-Fix-ECP-signature-not-found-error-when-only-assertio.patch
Patch5:	changeset_r7c075657a4d64f4d8dbcd03521a0694287d5059f.diff

%description
Lasso is a library that implements the Liberty Alliance Single Sign On
standards, including the SAML and SAML2 specifications. It allows to handle
the whole life-cycle of SAML based Federations, and provides bindings
for multiple languages.

%package devel
Summary: Lasso development headers and documentation
Group: Development/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}

%description devel
This package contains the header files, static libraries and development
documentation for Lasso.

%if %{with_perl}
%package perl
Summary: Liberty Alliance Single Sign On (lasso) Perl bindings
Group: Development/Libraries
BuildRequires: perl(ExtUtils::MakeMaker)
BuildRequires: perl(Test::More)
Requires: perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
Requires: %{name}%{?_isa} = %{version}-%{release}

%description perl
Perl language bindings for the lasso (Liberty Alliance Single Sign On) library.
%endif

%if %{with_java}
%package java
Summary: Liberty Alliance Single Sign On (lasso) Java bindings
Group: Development/Libraries
BuildRequires: java-devel
BuildRequires: jpackage-utils
Requires: java-headless
Requires: jpackage-utils
Requires: %{name}%{?_isa} = %{version}-%{release}

%description java
Java language bindings for the lasso (Liberty Alliance Single Sign On) library.
%endif

%if %{with_php}
%package php
Summary: Liberty Alliance Single Sign On (lasso) PHP bindings
Group: Development/Libraries
BuildRequires: php-devel, expat-devel
BuildRequires: python2
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: php(zend-abi) = %{php_zend_api}
Requires: php(api) = %{php_core_api}
Provides: php-lasso = %{version}-%{release}
Provides: php-lasso%{?_isa} = %{version}-%{release}

%description php
PHP language bindings for the lasso (Liberty Alliance Single Sign On) library.
%endif

%if %{with_python}
%package python
Summary: Liberty Alliance Single Sign On (lasso) Python bindings
Group: Development/Libraries
BuildRequires: python2-devel
BuildRequires: python-lxml
Requires: python
Requires: %{name}%{?_isa} = %{version}-%{release}

%description python
Python language bindings for the lasso (Liberty Alliance Single Sign On)
library.
%endif

%prep
%setup -q -n %{name}-%{version}
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1

%build
autoreconf -vif
%configure --prefix=%{_prefix} \
%if !%{with_java}
           --disable-java \
%endif
%if !%{with_python}
           --disable-python \
%endif
%if !%{with_perl}
           --disable-perl \
%endif
%if %{with_php}
           --enable-php5=yes \
           --with-php5-config-dir=%{php_inidir} \
%else
           --enable-php5=no \
%endif
%if %{with_wsf}
           --enable-wsf \
           --with-sasl2=%{_prefix}/sasl2 \
%endif
#           --with-html-dir=%{_datadir}/gtk-doc/html

make %{?_smp_mflags} CFLAGS="%{optflags}"

%check
make check

%install
#install -m 755 -d %{buildroot}%{_datadir}/gtk-doc/html

make install exec_prefix=%{_prefix} DESTDIR=%{buildroot}
find %{buildroot} -type f -name '*.la' -exec rm -f {} \;
find %{buildroot} -type f -name '*.a' -exec rm -f {} \;

# Perl subpackage
%if %{with_perl}
find %{buildroot} \( -name perllocal.pod -o -name .packlist \) -exec rm -v {} \;

find %{buildroot}/usr/lib*/perl5 -type f -print |
        sed "s@^%{buildroot}@@g" > %{name}-perl-filelist
if [ "$(cat %{name}-perl-filelist)X" = "X" ] ; then
    echo "ERROR: EMPTY FILE LIST"
    exit -1
fi
%endif

# PHP subpackage
%if %{with_php}
install -m 755 -d %{buildroot}%{_datadir}/php/%{name}
mv %{buildroot}%{_datadir}/php/lasso.php %{buildroot}%{_datadir}/php/%{name}

# rename the PHP config file when needed (PHP 5.6+)
if [ "%{name}.ini" != "%{ini_name}" ]; then
  mv %{buildroot}%{php_inidir}/%{name}.ini \
     %{buildroot}%{php_inidir}/%{ini_name}
fi
%endif

# Remove bogus doc files
rm -fr %{buildroot}%{_defaultdocdir}/%{name}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(-,root,root)
%{_libdir}/liblasso.so.*
%doc AUTHORS COPYING NEWS README

%files devel
%defattr(-,root,root)
%{_libdir}/liblasso.so
%{_libdir}/pkgconfig/lasso.pc
%{_includedir}/%{name}

%if %{with_perl}
%files perl -f %{name}-perl-filelist
%defattr(-,root,root)
%endif

%if %{with_java}
%files java
%defattr(-,root,root)
%{_libdir}/java/libjnilasso.so
%{_javadir}/lasso.jar
%endif

%if %{with_php}
%files php
%defattr(-,root,root)
%attr(755,root,root) %{php_extdir}/lasso.so
%config(noreplace) %attr(644,root,root) %{php_inidir}/%{ini_name}
%attr(755,root,root) %dir %{_datadir}/php/%{name}
%attr(644,root,root) %{_datadir}/php/%{name}/lasso.php
%endif

%if %{with_python}
%files python
%defattr(-,root,root)
%{python_sitearch}/lasso.py*
%{python_sitearch}/_lasso.so
%endif

%changelog
* Thu Aug 08 2019 Scientific Linux Auto Patch Process <SCIENTIFIC-LINUX-DEVEL@LISTSERV.FNAL.GOV>
- Added Patch: changeset_r7c075657a4d64f4d8dbcd03521a0694287d5059f.diff
-->  Fix expired cert
- Added Source: lasso.ini
-->  Config file for automated patch script

* Sun Feb 10 2019 Jakub Hrozek <jhrozek@redhat.com> - 2.5.1-3
- Resolves: #1634267 - ECP signature check fails with
                       LASSO_DS_ERROR_SIGNATURE_NOT_FOUND when assertion signed
                       instead of response

* Fri Jun 17 2016 John Dennis <jdennis@redhat.com> - 2.5.1-2
- Rebase to upstream 2.5.1
  Resolves: #1310860
- add validate_idp_list_test patch

* Thu Jun  9 2016 John Dennis <jdennis@redhat.com> - 2.5.1-1
- Rebase to upstream 2.5.1
  Resolves: #1310860

* Thu Sep  3 2015 John Dennis <jdennis@redhat.com> - 2.5.0-1
- Rebase to upstream, now includes our ECP patches, no need to patch any more
  Resolves: #1205342

* Tue Sep  1 2015 John Dennis <jdennis@redhat.com> - 2.4.1-8
- Add explicit minimum dependency on glib2 2.42,
  for some reason RPM is not automatically detecting the dependency
  Resolves: #1254989

* Wed Aug 19 2015 John Dennis <jdennis@redhat.com> - 2.4.1-7
- Add ECP support, brings Lasso up to current upstream tip + revised ECP patches
  Resolves: #1205342

* Mon Jun 22 2015 John Dennis <jdennis@redhat.com> - 2.4.1-6
- Add ECP support, brings Lasso up to current upstream tip + ECP patches
  Resolves: #1205342

* Fri Dec  5 2014 Simo Sorce <simo@redhat.com> - 2.4.1-5
- Add support for ADFS interoperability
- Resolves: #1160803

* Thu Sep 11 2014 Simo Sorce <simo@redhat.com> - 2.4.1-4
- Add missing covscan related patches previously sent upstream
- Related: #1120360

* Thu Sep 11 2014 Simo Sorce <simo@redhat.com> - 2.4.1-3
- ppc4le fails to build without autoreconf being run first
- Resolves: #1140419

* Fri Sep  5 2014 Simo Sorce <simo@redhat.com> - 2.4.1-2
- Import packge in RHEL7
- Resolves: #1120360

* Thu Aug 28 2014 Simo Sorce <simo@redhat.com> - 2.4.1-1
- New upstream relase 2.4.1
- Drop patches as they have all been integrated upstream

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Fri Jun 20 2014 Remi Collet <rcollet@redhat.com> - 2.4.0-4
- rebuild for https://fedoraproject.org/wiki/Changes/Php56
- add numerical prefix to extension configuration file
- drop unneeded dependency on pecl
- add provides php-lasso

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Fri Apr 25 2014 Simo Sorce <simo@redhat.com> - 2.4.0-2
- Fixes for arches where pointers and integers do not have the same size
  (ppc64, s390, etc..)

* Mon Apr 14 2014 Stanislav Ochotnicky <sochotnicky@redhat.com> - 2.4.0-1
- Use OpenJDK instead of GCJ for java bindings

* Sat Jan 11 2014 Simo Sorce <simo@redhat.com> 2.4.0-0
- Update to final 2.4.0 version
- Drop all patches, they are now included in 2.4.0
- Change Source URI

* Mon Dec  9 2013 Simo Sorce <simo@redhat.com> 2.3.6-0.20131125.5
- Add patches to fix rpmlint license issues
- Add upstream patches to fix some build issues

* Thu Dec  5 2013 Simo Sorce <simo@redhat.com> 2.3.6-0.20131125.4
- Add patch to support automake-1.14 for rawhide

* Mon Nov 25 2013 Simo Sorce <simo@redhat.com> 2.3.6-0.20131125.3
- Initial packaging
- Based on the spec file by Jean-Marc Liger <jmliger@siris.sorbonne.fr>
- Code is updated to latest master via a jumbo patch while waiting for
  official upstream release.
- Jumbo patch includes also additional patches sent to upstream list)
  to build on Fedora 20
- Perl bindings are disabled as they fail to build
- Disable doc building as it doesn't ork correctly for now
