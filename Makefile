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
	@while read package; \
	do \
	  line="$$package"; \
	  [[ "$$line" == git+* ]] && \
	    line=`echo "$$line" | sed -e 's/git.*\///g' -e 's/.git$$//g'`; \
	  pip3 freeze 2>/dev/null | grep -P `echo "$$line" | sed 's/>=/.*/g'` > /dev/null 2>&1 || \
	    pip3 install --user "$$package"; \
	done < requirements.txt

build: init build-lang
	@echo "Building python package..."
	@mypy --silent-imports --package color_harmonization
	@echo "#! /bin/bash" > color-harmonization
	@echo "/usr/bin/env python3 -m color_harmonization" >> color-harmonization
	@chmod +x color-harmonization

run: build
	@echo "Running application..."
	@./color-harmonization

lang:
	@echo "Generating internationalization files..."
	@mkdir -p color_harmonization/gui/locale/de/LC_MESSAGES
	@intltool-extract --type=gettext/glade color_harmonization/gui/color-harmonization.glade
	@xgettext --from-code=UTF-8 --language=Python --keyword=_ --keyword=N_ \
	--output=color_harmonization/gui/locale/locale.pot \
	`find . -name "*.py" -type f` \
	color_harmonization/gui/color-harmonization.glade.h
	@msginit --input=color_harmonization/gui/locale/locale.pot \
	--locale=de.UTF-8 --output-file=color_harmonization/gui/locale/de/LC_MESSAGES/de.po

build-lang:
	@echo "Compiling internationalization files..."
	@msgfmt --output color_harmonization/gui/locale/de/LC_MESSAGES/color_harmonization.mo \
	color_harmonization/gui/locale/de/LC_MESSAGES/de.po
