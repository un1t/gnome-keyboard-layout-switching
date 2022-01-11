.PHONY: venv

install: venv
	venv/bin/pip install wheel
	venv/bin/pip install -r requirements.txt


venv:
	[ -d venv ] || python3 -m venv venv


clean:
	rm -rf venv


autostart:
	cp gnome-keyboard-layout-switch.desktop ~/.config/autostart/
	sed -i 's#{dir}#'`pwd`'#g' ~/.config/autostart/gnome-keyboard-layout-switch.desktop
