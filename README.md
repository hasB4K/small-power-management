PM
==

PM is a simple power management script.
It let you allow to suspend or lock your computer.

By default the script is executed when ACPI detect that the screen is closed.

Installation
------------

```bash
git clone https://github.com/hasB4K/small-power-management.git
cd small-power-management/pm
sudo ./install.sh all
pm -u $USER
```
You will to restart your ACPI daemon.

Please make sure to add the following line in your .xinitrc or .xprofile file:
```bash
pm -u $USER
```
This command will initialize the current user which is logged if they are
severals users.


All files are installed in `/usr/local/etc/pm/`.

Arguments
---------

This script takes severals arguments.
Some of them take these options: {lock, suspend, all}.

* -h, --help                Display the help
* -e, --enable [Options]    Enable the options.
* -d, --disable [Options]   Disable the options.
* -p, --perform             Execute the script with the setted options.
* -u, --user [User]         Set the current user
* -l, --locker              Set a default Locker (eg. i3lock, slimlock, ...).

Dependencies
------------

By default PM need to have the ACPI Daemon installed. He will install an event
file to `/etc/acpi/events/events_pm`.

Please make sure to have install ACPI before using this script. If you want to
use this script without ACPI, please notice that the script will no longer be
executed when the screen will be closed. However if you decide to use the
script "as is" you can install it by doing:

```bash
sudo ./install.sh install
```
