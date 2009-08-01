#Module-Specific definitions
%define mod_name mod_auth_xradius
%define mod_conf 14_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary:	DSO module for the apache Web server
Name:		apache-%{mod_name}
Version:	0.4.6
Release:	%mkrel 11
Group:		System/Servers
License:	Apache License
URL:		http://www.outoforder.cc/projects/apache/mod_auth_xradius/
Source0:	http://www.outoforder.cc/downloads/mod_auth_xradius/%{mod_name}-%{version}.tar.bz2
Source1:	%{mod_conf}.bz2
Patch0:		mod_auth_xradius-0.4.5-no_ap_prefix.diff
Patch1:		mod_auth_xradius-apu13_fix.diff
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.0
Requires(pre):	apache >= 2.2.0
Requires:	apache-conf >= 2.2.0
Requires:	apache >= 2.2.0
BuildRequires:  apache-devel >= 2.2.0
BuildRequires:	apr-util-devel >= 1.3.0
BuildRequires:	automake1.7
Epoch:		1
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
mod_auth_xradius provides high performance authentication against
RFC 2865 RADIUS Servers. 

Features:

 o Supports popular RADIUS Servers including OpenRADIUS,
   FreeRADIUS and commercial servers.
 o Distributed Authentication Cache using apr_memcache.
 o Local Authentication Cache using DBM.
 o Uses standard HTTP Basic Authentication, unlike
 mod_auth_radius which uses cookies for sessions.

%prep

%setup -q -n %{mod_name}-%{version}
%patch0 -p0
%patch1 -p0

# lib64 fixes
perl -pi -e "s|/lib\ |/%{_lib}\ |g" m4/apr_memcache.m4
perl -pi -e "s|/lib/|/%{_lib}/|g" m4/apr_memcache.m4
perl -pi -e "s|/lib\b|/%{_lib}|g" m4/apr_memcache.m4

%build
#sh autogen.sh

%if %{mdkversion} >= 200910
cp `aclocal-1.7 --print-ac-dir`/{libtool,ltoptions,ltsugar,ltversion,lt~obsolete}.m4 m4/
%endif

rm -f configure
libtoolize --force --copy; aclocal -I m4; autoheader; automake --add-missing --copy --foreign; autoconf
rm -rf autom4te.cache

export APR_MEMCACHE_LIBS="`apu-1-config --link-ld`"
export APR_MEMCACHE_CFLAGS="`apu-1-config --includes`"

%configure2_5x --localstatedir=/var/lib \
    --with-apxs=%{_sbindir}/apxs \
    --with-apr-memcache=%{_prefix}

%make

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -d %{buildroot}%{_libdir}/apache-extramodules
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d

install -m0755 .libs/*.so %{buildroot}%{_libdir}/apache-extramodules/
bzcat %{SOURCE1} > %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

%post
if [ -f %{_var}/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f %{_var}/lock/subsys/httpd ]; then
        %{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc LICENSE NOTICE README
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}
