# Gnome Keyboard Layout Switch

It's a tool, that allow painlessly switching between multiple keyboard layouts.
It splits all input sources into groups: **primary** and **secondary**. By default first two input sources are used as **primary**. It could be changes with **-p** option.
It uses **LEFT ALT + LEFT SHIFT** to switching between **primary** input sources and **RIGHT ALT + RIGHT SHIFT** to switch between **secondary** input sources.

For example, I have 4 input sources **en,ru,pl,uk**.  I can switch between **en,ru** with **LEFT ALT + LEFT SHIFT** and between **pl,uk** with **RIGHT ALT + RIGHT SHIFT**.

If you already use **ALT + SHIFT** combination with **Gnome Tweeks** it should be turned off.

## How to install
    sudo apt install python3-gi libcairo2-dev libgirepository1.0-dev
    git clone https://github.com/un1t/gnome-keyboard-layout-switching
    cd gnome-keyboard-layout-switching
    make

# Ckeck if it works

Without options, first two languages are used as primary.

    ./venv/bin/python main.py

Select specific languages as primary.

    ./venv/bin/python main.py -p en,ru

# Add entry to "Startup Application Preferences"
    make autostart

File **~/.config/autostart/gnome-keyboard-layout-switch.desktop** is created. You can modify it to provide custom options.