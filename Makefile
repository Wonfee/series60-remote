# $Id: Makefile,v 1.6 2010/02/16 13:49:02 lukas Exp $
#

PYTHON=`which python`
DESTDIR=/
BUILDIR=$(CURDIR)/debian/series60-remote
RPMROOT=$(HOME)/rpmbuild
RPMSOURCE=$(RPMROOT)/SOURCES
RPMSRCRPM=$(RPMROOT)/SRPMS
RPMBINRPM=$(RPMROOT)/RPMS/noarch
PROJECT=series60-remote
VERSION=0.4.80

all:
	@echo "make build - Build everything needed to install"
	@echo "make install - Install on local system"
	@echo "make clean - Get rid of scratch and byte files"
	@echo "make source - Create source package"
	@echo "make buildrpm - Generate a rpm package"
	@echo "make builddeb - Generate a deb package"

build:
	$(PYTHON) setup.py build

source:
	$(PYTHON) setup.py sdist $(COMPILE)

install:
	$(PYTHON) setup.py install --root $(DESTDIR) $(COMPILE)

buildrpm:
	# setup rpmbuild tree in $HOME/rpmbuild
	`which rpmdev-setuptree`
	# build the source package in the SOURCES directory
	$(PYTHON) setup.py sdist $(COMPILE) --dist-dir=$(RPMSOURCE) --prune
	# build the binary and source package
	`which rpmbuild` -ba pc/install/rpm/series60-remote.spec
	# move the generated files to the dist/ directory
	mkdir -p dist
	mv $(RPMSRCRPM)/$(PROJECT)*.src.rpm dist/
	mv $(RPMBINRPM)/$(PROJECT)*.noarch.rpm dist/

builddeb:
	# remove temp debian directory
	rm -rf debian
	# remove previous builds
	rm -f dist/$(PROJECT)*.deb dist/$(PROJECT)*.dsc dist/$(PROJECT)*.changes dist/$(PROJECT)*.diff.gz dist/$(PROJECT)*.orig.tar.gz
	# copy the debian install scripts to current directory
	cp -r pc/install/debian .
	# build the source package in the parent directory
	# then rename it to project_version.orig.tar.gz
	$(PYTHON) setup.py sdist $(COMPILE) --dist-dir=../ --prune
	rename -f 's/$(PROJECT)-(.*)\.tar\.gz/$(PROJECT)_$$1\.orig\.tar\.gz/' ../*
	# build the package
	dpkg-buildpackage -i -I -us -uc -rfakeroot
	# move to dist/ directory
	mkdir -p dist
	mv ../$(PROJECT)*.deb ../$(PROJECT)*.dsc ../$(PROJECT)*.changes ../$(PROJECT)*.diff.gz ../$(PROJECT)*.orig.tar.gz dist/
	# remove temp debian directory
	rm -rf debian

clean:	
	$(PYTHON) setup.py clean
	rm -rf build/ debian/ pc/ui/ui_*.py pc/ui/resource_*.py mobile/*.sis MANIFEST
	find . -name '*.pyc' -delete
