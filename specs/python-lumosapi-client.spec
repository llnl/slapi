%global srcname lumosapi-client
%global modulename lumosapi_client
%global __pytest /usr/bin/pytest-%{python3_pkgversion}
%define _debugsource_template %{nil}
%global debug_package %{nil}

Name:           python-%{srcname}
Version:        2.1.0
Release:        1%{?dist}
Summary:        LumOS API Client

License:        MIT
URL:            https://github.com/pydantic/pydantic-core
Source:         %{url}/archive/v%{version}/python-%{srcname}-%{version}.tar

BuildRequires:  python%{python3_pkgversion}-devel
BuildRequires:  python%{python3_pkgversion}-build
BuildRequires:  python%{python3_pkgversion}-pyproject-hooks

%global _description %{expand:
LumOS API Client.}

%description %_description

%package -n python%{python3_pkgversion}-%{srcname}
Summary:  %{summary}
Requires: python%{python3_version}dist(pydantic)
Requires: python%{python3_version}dist(lazy-imports)

%description -n python%{python3_pkgversion}-%{srcname} %_description

%prep
export PYO3_PYTHON=/usr/bin/python%{python3_pkgversion}
%autosetup -n python-%{srcname}-%{version}
make .quilt-lumosapi-client
pushd src/lumosapi_client

# stub to build using setuptools instead of flit.core
#cat >setup.py <<EOF
#from setuptools import setup
#setup()
#EOF

%build
export PYO3_PYTHON=/usr/bin/python%{python3_pkgversion}
pushd src/lumosapi_client
mv patches ../patches_link
mv series  ../series_link
python%{python3_pkgversion} -m build --wheel
pushd dist
unzip %{modulename}-%{version}-*.whl
rm -rf %{modulename}-%{version}-*.whl
popd
mv ../patches_link patches
mv ../series_link  series
popd

%install
export PYO3_PYTHON=/usr/bin/python%{python3_pkgversion}
pushd src/lumosapi_client
mv patches ../patches_link
mv series  ../series_link
mkdir -p %{buildroot}%{python3_sitearch}
mkdir -p %{buildroot}%{python3_sitearch}
cp -a dist/%{modulename}-%{version}.dist-info %{buildroot}%{python3_sitearch}/
cp -a dist/%{modulename} %{buildroot}%{python3_sitearch}/
mv ../patches_link patches
mv ../series_link  series
popd

%files -n python%{python3_pkgversion}-%{srcname}
%{python3_sitearch}/%{modulename}*

%changelog
* Thu Feb 27 2025 Herb Wartens <wartens2@llnl.gov>
- First LLNL version packaged.
