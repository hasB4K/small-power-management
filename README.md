PM
==

PM is a simple power management script.
It let you allow to suspend or lock your computer.

By default the script is executed when ACPI detect that the screen is closed.

Installation
------------

### Full installation
If you want to fully install PM, proceed like this:
```bash
git clone https://github.com/hasB4K/small-power-management.git
cd small-power-management/pm
sudo ./install.sh all
pm -u $USER
```
You will need to restart your ACPI daemon.
If your using Systemd proceed like this:
```bash
sudo systemctl restart acpid
```

Please make sure to add the following line in your .xinitrc or .xprofile file:
```bash
pm -u $USER
```
This command will initialize the current user which is logged if they are
severals users.


All files are installed in `/usr/local/etc/pm/`.

###Disable Auto-Suspend on Systemd

If your using Systemd, the computer will be suspend when the computer screen is
closed. For avoiding the management of that feature by Systemd you need to
uncomment the line of `HandleLidSwicth` in the file `/etc/systemd/logind.conf`:

```bash
HandleLidSwicth=ignore
```

### Uninstallation

If you want to uninstall this script, please do:
```bash
sudo /usr/local/etc/pm/install.sh uninstall
```

Usage
---------

This script takes severals arguments.
Some of them take those options: {lock, suspend, all}.

* -u, --user [User]         Set the current user
* -l, --locker [Locker]     Set a default Locker (eg. i3lock, slimlock, ...).
* -e, --enable [Options]    Enable the options.
* -d, --disable [Options]   Disable the options.
* -p, --perform             Execute the script with the setted options.
* -h, --help                Display the help

Dependencies
------------

By default PM need to have the ACPI Daemon installed. An event file will be
installed to `/etc/acpi/events/events_pm`.

Please make sure to have installed ACPI before using this script. If you want
to use this script without ACPI, please notice that the script will no longer
be executed when the screen will be closed. However you still still can use
this script "as is". You can do that by doing:

```bash
sudo ./install.sh install
```
