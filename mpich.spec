Summary:        A high-performance implementation of MPI
Name:           mpich
Version:        3.2.1
Release:        10
License:        MIT
URL:            http://www.mpich.org/
Source0:        http://www.mpich.org/static/downloads/%{version}/mpich-%{version}.tar.gz
Source1:        mpich.macros
Source2:        mpich.pth.py2
Source3:        mpich.pth.py3
Patch0:         mpich-modules.patch
Patch3:         0003-soften-version-check.patch

BuildRequires:  gcc gcc-c++ gcc-gfortran hwloc-devel >= 1.8 valgrind-devel
BuildRequires:  python2-devel python3-devel automake
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

%package -n python2-mpich
Summary:        mpich support for Python 2

%description -n python2-mpich
mpich support for Python 2.

%package -n python3-mpich
Summary:        mpich support for Python 3

%description -n python3-mpich
mpich support for Python 3.

%{!?opt_cc: %global opt_cc gcc}
%{!?opt_fc: %global opt_fc gfortran}
%{!?opt_f77: %global opt_f77 gfortran}

%{!?opt_cc_cflags: %global opt_cc_cflags %{optflags}}
%{!?opt_fc_fflags: %global opt_fc_fflags %{optflags}}
%{!?opt_f77_fflags: %global opt_f77_fflags %{optflags}}

%ifarch aarch64
%global m_option ""
%else
%global m_option -m64
%endif
%global selected_channels ch3:nemesis
%global XFLAGS -fPIC

%prep
%autosetup -p1

%build
%configure      \
        --enable-sharedlibs=gcc                                 \
        --enable-shared                                         \
        --enable-static=no                                      \
        --enable-lib-depend                                     \
        --disable-rpath                                         \
        --disable-silent-rules                                  \
        --enable-fc                                             \
        --with-device=%{selected_channels}                      \
        --with-pm=hydra:gforker                                 \
        --includedir=%{_includedir}/mpich-%{_arch}            \
        --bindir=%{_libdir}/mpich/bin                         \
        --libdir=%{_libdir}/mpich/lib                         \
        --datadir=%{_datadir}/mpich                           \
        --mandir=%{_mandir}/mpich-%{_arch}                    \
        --docdir=%{_datadir}/mpich/doc                        \
        --htmldir=%{_datadir}/mpich/doc                       \
        --with-hwloc-prefix=system                              \
        FC=%{opt_fc}                                            \
        F77=%{opt_f77}                                          \
        CFLAGS="%{m_option} -O2 %{?XFLAGS}"                     \
        CXXFLAGS="%{m_option} -O2 %{?XFLAGS}"                   \
        FCFLAGS="%{m_option} -O2 %{?XFLAGS}"                    \
        FFLAGS="%{m_option} -O2 %{?XFLAGS}"                     \
        LDFLAGS='-Wl,-z,noexecstack'                            \
        MPICHLIB_CFLAGS="%{?opt_cc_cflags}"                     \
        MPICHLIB_CXXFLAGS="%{optflags}"                         \
        MPICHLIB_FCFLAGS="%{?opt_fc_fflags}"                    \
        MPICHLIB_FFLAGS="%{?opt_f77_fflags}"
#       MPICHLIB_LDFLAGS='-Wl,-z,noexecstack'                   \
#       MPICH_MPICC_FLAGS="%{m_option} -O2 %{?XFLAGS}"  \
#       MPICH_MPICXX_FLAGS="%{m_option} -O2 %{?XFLAGS}" \
#       MPICH_MPIFC_FLAGS="%{m_option} -O2 %{?XFLAGS}"  \
#       MPICH_MPIF77_FLAGS="%{m_option} -O2 %{?XFLAGS}"
#       --with-openpa-prefix=embedded                           \
#       FCFLAGS="%{?opt_fc_fflags} -I%{_fmoddir}/mpich %{?XFLAGS}"    \

sed -r -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -r -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
sed -i -e 's| -shared | -Wl,--as-needed\0|g' libtool

%make_build V=1

%install
%make_install

mkdir -p %{buildroot}%{_fmoddir}/mpich
mv %{buildroot}%{_includedir}/mpich-*/*.mod %{buildroot}%{_fmoddir}/mpich/
sed -r -i 's|^modincdir=.*|modincdir=%{_fmoddir}/mpich|' %{buildroot}%{_libdir}/mpich/bin/mpifort

mkdir -p %{buildroot}%{_sysconfdir}/modulefiles/mpi
sed -r 's|%{_bindir}|%{_libdir}/mpich/bin|;
        s|@LIBDIR@|%{_libdir}/mpich|;
        s|@MPINAME@|mpich|;
        s|@py2sitearch@|%{python2_sitearch}|;
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

mkdir -p %{buildroot}%{python2_sitearch}/mpich
install -pDm0644 %{SOURCE2} %{buildroot}%{python2_sitearch}/mpich.pth
mkdir -p %{buildroot}%{python3_sitearch}/mpich
install -pDm0644 %{SOURCE3} %{buildroot}%{python3_sitearch}/mpich.pth

find %{buildroot} -type f -name "*.la" -delete

%check
make check V=1

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
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
%{_sysconfdir}/profile.d/mpich-%{_arch}.*

%files devel
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
%dir %{_datadir}/mpich
%{_datadir}/mpich/doc/
%dir %{_mandir}/mpich-%{_arch}
%{_mandir}/mpich-%{_arch}/man1/
%{_mandir}/mpich-%{_arch}/man3/

%files -n python2-mpich
%dir %{python2_sitearch}/mpich
%{python2_sitearch}/mpich.pth

%files -n python3-mpich
%dir %{python3_sitearch}/mpich
%{python3_sitearch}/mpich.pth

%changelog
* Sat Mar 14 2020 sunguoshuai <sunguoshuai@huawei.com> - 3.2.1-10
- del rpm-mpi-hooks deps.

* Thu Nov 25 2019 openEuler Buildteam <buildteam@openeuler.org> - 3.2.1-9
- Package init
