Summary:        A high-performance implementation of MPI
Name:           mpich
Version:        4.0.1
Release:        1
License:        MIT
URL:            http://www.mpich.org/
Source0:        http://www.mpich.org/static/downloads/%{version}/mpich-%{version}.tar.gz
Source1:        mpich.macros
Source2:        mpich.pth.py3
Patch0:         autogen-only-deal-with-json-yaksa-if-enabled.patch
Patch1:         autoconf-pull-dynamic-and-not-static-libs-from-pkg-config.patch
Patch2:         mpich-modules.patch

BuildRequires:  gcc gcc-c++ gcc-gfortran hwloc-devel >= 2.0 valgrind-devel
BuildRequires:  python3-devel automake libtool
Provides:       mpi
Provides:       mpich2 = %{version}
Obsoletes:      mpich2 < 3.0
Requires:       environment(modules)

%description
MPICH is a high performance and widely portable implementation
of the Message Passing Interface (MPI) standard.

%package autoload
Summary:        Load mpich automatically into profile
Requires:       mpich = %{version}-%{release}
Provides:       mpich2-autoload = 3.0.1
Obsoletes:      mpich2-autoload < 3.0

%description autoload
This package contains profile files that make mpich automatically loaded.

%package devel
Summary:        Development files for mpich
Requires:       mpich = %{version}-%{release} pkgconfig gcc-gfortran
Provides:       mpich-devel-static = %{version}-%{release}
Provides:       mpich2-devel = 3.0.1
Obsoletes:      mpich2-devel < 3.0

%description devel
Contains development headers and libraries for mpich.

%package help
Summary:        Documentations and examples for mpich
BuildArch:      noarch
Requires:       mpich-devel = %{version}-%{release}
Provides:       mpich2-doc = 3.0.1
Provides:       mpich-doc = %{version}-%{release}
Obsoletes:      mpich2-doc < 3.0
Obsoletes:      mpich-doc < %{version}-%{release}

%description help
Contains documentations, examples and man-pages for mpich.

%package -n python3-mpich
Summary:        mpich support for Python 3

%description -n python3-mpich
mpich support for Python 3.

%prep
%setup

%patch0
%patch1
%patch2 -p1

%build
# Fix 'aclocal-1.15' is missing on your system
autoreconf -f -i -v
CONFIGURE_OPTS=(
        --enable-sharedlibs=gcc
        --enable-shared
        --enable-static=no
        --enable-lib-depend
        --disable-rpath
        --disable-silent-rules
        --enable-fc
        --with-device=ch3:nemesis
        --with-pm=hydra:gforker
        --includedir=%{_includedir}/%{name}-%{_arch}
        --bindir=%{_libdir}/%{name}/bin
        --libdir=%{_libdir}/%{name}/lib
        --datadir=%{_datadir}/%{name}
        --mandir=%{_mandir}/%{name}-%{_arch}
        --docdir=%{_datadir}/%{name}/doc
        --htmldir=%{_datadir}/%{name}/doc
        --with-hwloc-prefix=system
)

%configure "${CONFIGURE_OPTS[@]}" FFLAGS="$FFLAGS -w -fallow-argument-mismatch" FCFLAGS="$FCFLAGS -w -fallow-argument-mismatch" CFLAGS="%optflags -fPIC" CXXLAGS="%optflags -fPIC" MPICHLIB_CFLAGS="%{optflags}" MPICHLIB_CXXFLAGS="%{optflags}"

sed -r -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -r -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
sed -i -e 's| -shared | -Wl,--as-needed\0|g' libtool

%make_build V=1 VERBOSE=1

%install
%make_install

mkdir -p %{buildroot}%{_fmoddir}/mpich
mv %{buildroot}%{_includedir}/mpich-*/*.mod %{buildroot}%{_fmoddir}/mpich/
sed -r -i 's|^modincdir=.*|modincdir=%{_fmoddir}/mpich|' %{buildroot}%{_libdir}/mpich/bin/mpifort

mkdir -p %{buildroot}%{_sysconfdir}/modulefiles/mpi
sed -r 's|%{_bindir}|%{_libdir}/mpich/bin|;
        s|@LIBDIR@|%{_libdir}/mpich|;
        s|@MPINAME@|mpich|;
        s|@py3sitearch@|%{python3_sitearch}|;
        s|@ARCH@|%{_arch}|;
        s|@fortranmoddir@|%{_fmoddir}|;
     ' \
     <src/packaging/envmods/mpich.module \
     >%{buildroot}%{_sysconfdir}/modulefiles/mpi/mpich-%{_arch}

mkdir -p %{buildroot}%{_sysconfdir}/profile.d
cat >%{buildroot}%{_sysconfdir}/profile.d/mpich-%{_arch}.sh <<EOF
module load mpi/mpich-%{_arch}
EOF
cp -p %{buildroot}%{_sysconfdir}/profile.d/mpich-%{_arch}.{sh,csh}

install -pDm0644 %{SOURCE1} %{buildroot}%{_rpmconfigdir}/macros.d/macros.mpich

mkdir -p %{buildroot}%{python3_sitearch}/mpich
install -pDm0644 %{SOURCE2} %{buildroot}%{python3_sitearch}/mpich.pth

find %{buildroot} -type f -name "*.la" -delete

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(-,root,root)
%license COPYRIGHT
%doc CHANGES README README.envvar RELEASE_NOTES
%dir %{_libdir}/mpich
%dir %{_libdir}/mpich/lib
%dir %{_libdir}/mpich/bin
%{_libdir}/mpich/lib/*.so.*
%{_libdir}/mpich/bin/hydra*
%{_libdir}/mpich/bin/mpichversion
%{_libdir}/mpich/bin/mpiexec*
%{_libdir}/mpich/bin/mpirun
%{_libdir}/mpich/bin/mpivars
%{_libdir}/mpich/bin/parkill
%{_sysconfdir}/modulefiles/mpi/

%files autoload
%defattr(-,root,root)
%{_sysconfdir}/profile.d/mpich-%{_arch}.*

%files devel
%defattr(-,root,root)
%{_includedir}/mpich-%{_arch}/
%{_libdir}/mpich/lib/pkgconfig/
%{_libdir}/mpich/lib/*.so
%{_libdir}/mpich/bin/mpicc
%{_libdir}/mpich/bin/mpic++
%{_libdir}/mpich/bin/mpicxx
%{_libdir}/mpich/bin/mpif77
%{_libdir}/mpich/bin/mpif90
%{_libdir}/mpich/bin/mpifort
%{_fmoddir}/mpich/
%{_rpmconfigdir}/macros.d/macros.mpich

%files help
%defattr(-,root,root)
%dir %{_datadir}/mpich
%{_datadir}/mpich/doc/
%dir %{_mandir}/mpich-%{_arch}
%{_mandir}/mpich-%{_arch}/man1/
%{_mandir}/mpich-%{_arch}/man3/

%files -n python3-mpich
%defattr(-,root,root)
%dir %{python3_sitearch}/mpich
%{python3_sitearch}/mpich.pth

%changelog
* Thu Mar 17 2022 misaka00251 <misaka00251@misakanet.cn> - 4.0.1-1
- Upgrade version to 4.0.1

* Fri Mar 11 2022 wangyangdahai <admin@you2.top> - 3.2.1-14
- fix m64 flags riscv64

* Mon Aug 02 2021 linjiaxin5 <linjiaxin5@huawei.com> - 3.2.1-13
- Fix failure caused by GCC upgrade to 10

* Fri Oct 30 2020 wangxiao <wangxiao65@huawei.com> - 3.2.1-12
- delete unnessary file

* Wed Oct 21 2020 wangxiao <wangxiao65@huawei.com> - 3.2.1-11
- drop python2 subpackage

* Sat Mar 14 2020 sunguoshuai <sunguoshuai@huawei.com> - 3.2.1-10
- del rpm-mpi-hooks deps.

* Thu Nov 25 2019 openEuler Buildteam <buildteam@openeuler.org> - 3.2.1-9
- Package init
