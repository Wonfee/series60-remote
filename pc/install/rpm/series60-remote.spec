%{!?python_sitelib: %global python_sitelib %(python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           series60-remote
Version:        0.4.80
Release:        1%{?dist}
Summary:        Application to manage your S60 mobile phone

Group:          Applications/Communications
License:        GPLv2
URL:            http://series60-remote.sf.net
Source0:        http://downloads.sourceforge.net/%{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch

BuildRequires:  python-devel
BuildRequires:  PyQt4
BuildRequires:  desktop-file-utils

Requires:       python
Requires:       PyQt4
Requires:       pybluez
Requires:       python-obexftp
# It seems that rpmlint confused by "lib" string wrongly
Requires:       python-matplotlib

%description
Series60-Remote is an application for Linux and Windows that manages Nokia
mobile phones with the S60 operating system.
The application provides the following features:
 - Message management
 - Contact management
 - File management

%prep
%setup -q -n %{name}-%{version}
chmod +x pc/mkpyqt.py pc/series60_remote.py

%build
python setup.py build

%install
rm -rf %{buildroot}
python setup.py install -O1 --skip-build --root %{buildroot}

desktop-file-install --vendor=""                     \
       --dir=%{buildroot}%{_datadir}/applications/   \
       %{buildroot}%{_datadir}/applications/%{name}.desktop

chmod +x %{buildroot}/%{python_sitelib}/series60_remote/series60_remote.py
chmod +x %{buildroot}/%{python_sitelib}/series60_remote/mkpyqt.py

%post
# After install, we update the icons
touch --no-create %{_datadir}/icons/hicolor
if [ -x %{_bindir}/gtk-update-icon-cache ]; then
  %{_bindir}/gtk-update-icon-cache -q %{_datadir}/icons/hicolor;
fi
update-mime-database %{_datadir}/mime &> /dev/null || :
update-desktop-database &> /dev/null || :

%postun
# After uninstall, we update the icons
touch --no-create %{_datadir}/icons/hicolor
if [ -x %{_bindir}/gtk-update-icon-cache ]; then
  %{_bindir}/gtk-update-icon-cache -q %{_datadir}/icons/hicolor;
fi
update-mime-database %{_datadir}/mime &> /dev/null || :
update-desktop-database &> /dev/null || :


%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc PKG-INFO Changelog HACKING INSTALL LICENSE LICENSE.icons-oxygen README.icons-oxygen TODO
%{python_sitelib}/series60_remote/
%{python_sitelib}/*.egg-info
%{_datadir}/applications/%{name}.desktop
%{_datadir}/%{name}
%{_bindir}/%{name}

%changelog
* Thu Jul  1 2010 Lukas Hetzenecker <LuHe@gmx.at> - 0.4.80-1
- Update to 0.4.80

* Wed May 19 2010 pingou <pingou@pingoured.fr> - 0.3.93-2
- Add desktop-file-install
- Fix BR accordingly
- Remove PyQt4-devel from BR
- Add post and postun to update icons' cache

* Mon May 10 2010 Lukas Hetzenecker <LuHe@gmx.at> - 0.3.93-1
- Update to 0.3.93

* Mon Mar 29 2010 Lukas Hetzenecker <LuHe@gmx.at> - 0.3.92-1
- Update to 0.3.92

* Wed Jan 27 2010 Lukas Hetzenecker <LuHe@gmx.at> - 0.3.91-1
- Update to 0.3.91

* Sun Dec 20 2009 Lukas Hetzenecker <LuHe@gmx.at> - 0.3.90-1
- First release.

