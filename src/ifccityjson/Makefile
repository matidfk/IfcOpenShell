# IfcCityJSON - Python CityJSON to IFC converter
# Copyright (C) 2020-2024 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcCityJSON.
#
# IfcCityJSON is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcCityJSON is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcCityJSON.  If not, see <http://www.gnu.org/licenses/>.

VERSION:=$(shell cat ../../VERSION)
SED:=sed -i
ifeq ($(UNAME_S),Darwin)
SED:=sed -i '' -e
endif

.PHONY: qa
qa:
	black .

.PHONY: dist
dist:
	rm -rf dist
	cp pyproject.toml pyproject.toml.bak
	cp ifccityjson/__init__.py __init__.py.bak
	$(SED) 's/version = "0.0.0"/version = "$(VERSION)"/' pyproject.toml
	$(SED) 's/version = "0.0.0"/version = "$(VERSION)"/' ifccityjson/__init__.py
	python -m build
	mv pyproject.toml.bak pyproject.toml
	mv __init__.py.bak ifccityjson/__init__.py
