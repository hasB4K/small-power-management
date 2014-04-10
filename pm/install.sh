#!/bin/bash

DIR="/usr/local/etc/pm"

install()
{
    cd "$( dirname "${BASH_SOURCE[0]}" )"
    mkdir -p $DIR
    cp events_pm events_pm.sh install.sh pm.py $DIR
    touch $DIR/user
    chmod 666 $DIR/user
    if [ ! -f /usr/bin/pm ]
    then
        ln -s $DIR/pm.py /usr/bin/pm
    fi
    echo "Please do \"pm -u\"."
    echo "If you want to have the user set by default on your login"
    echo "please add this to your .xinitrc file or .xsession file."
}

display_acpi_info()
{
    echo "Please restart your acpi daemon."
}

install_acpi()
{
    if [ -d /etc/acpi ]
    then
        if [ ! -L /etc/acpi/events/events_pm ]
        then
            ln -s $DIR/events_pm /etc/acpi/events/
            echo
            display_acpi_info
        fi
    else
        echo "acpi is not installed."
    fi
}

uninstall()
{
    rm -r $DIR
    if [ -L /etc/acpi/events/events_pm ]
    then
        rm /etc/acpi/events/events_pm
        display_acpi_info
    fi
    rm /usr/bin/pm
}

case "$1" in
    install)
        install
    ;;
    install_acpi)
        install_acpi
    ;;
    all)
        install
        install_acpi
    ;;
    uninstall)
        uninstall
    ;;
    *)
        echo "Usage: {install | uninstall}."
    ;;
esac
