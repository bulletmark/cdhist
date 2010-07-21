# A bash directory stack "cd history" function.
#
# Copyright (C) 2010 Mark Blakeney, markb@berlios.de. This program is
# distributed under the terms of the GNU General Public License.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or any
# later version.
# 
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License at <http://www.gnu.org/licenses/> for more
# details.

DEST=/usr/local

PROG = cdhist.py
RC = bashrc_cdhist

all:
	@echo "Type make install or make home"

install:
	install -D $(PROG) $(DEST)/bin/$(PROG)
	install -m 644 -D $(RC) $(DEST)/etc/$(RC)
	@echo
	@echo "Now add \"source $(DEST)/etc/$(RC)\" to your ~/.bashrc."
	@echo

uninstall:
	rm -f $(DEST)/bin/$(PROG)
	rm -f $(DEST)/etc/$(RC)
	@echo
	@echo "Remove \"source $(DEST)/etc/$(RC)\" from your ~/.bashrc."
	@echo

home:
	install -D $(PROG) $(HOME)/bin/$(PROG)
	@echo "installing $(RC) to ~/.$(RC) and modifying path"
	@sed 's#^\(CDHISTPROG_=\).*$$#\1"$$HOME/bin/cdhist.py"#' $(RC) >~/.$(RC)
	@echo
	@echo "Now add \"source ~/.$(RC)\" to your ~/.bashrc."
	@echo
