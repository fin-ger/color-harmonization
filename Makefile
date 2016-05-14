# Copyright (C) 2016  David Bögelsack, Fin Christensen
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

all: build

init:
	@which python3 > /dev/null 2>&1 || (echo "python3 is not installed on this system" && exit 1)
	@which pip3 > /dev/null 2>&1 || (echo "pip3 is not installed on this system" && exit 1)
	@echo "Installing requirements with pip3..."
	@pip3 install --user -r requirements.txt

build: init
	@echo "Building python package..."
	@mypy -m color_harmonization
	@echo "#! /bin/bash" > color-harmonization
	@echo "/usr/bin/env python3 -m color_harmonization" >> color-harmonization
	@chmod +x color-harmonization

run: build
	@echo "Running application..."
	@./color-harmonization
