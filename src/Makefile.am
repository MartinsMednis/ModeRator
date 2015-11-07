## Process this file with automake to produce Makefile.in
## Created by Anjuta


uidir = $(pkgdatadir)/ui
ui_DATA = moderator_gtk.ui


## The main script
bin_SCRIPTS = moderator_gtk.py

## Directory where .class files will be installed
moderator_gtkdir = $(pythondir)/moderator_gtk


moderator_gtk_PYTHON = \
	moderator_gtk.py


EXTRA_DIST = $(ui_DATA)


# Remove ui directory on uninstall
uninstall-local:

	-rm -r $(uidir)

	-rm -r $(pkgdatadir)
