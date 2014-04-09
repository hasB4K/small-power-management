#!/bin/sh

DIR="/usr/local/etc/pm"

install()
{
    mkdir -p $DIR
    cp -r * $DIR
    touch $DIR/user
    chmod 666 $DIR/user
    touch /etc/acpi/y
    if [ ! -f /usr/bin/pm ]
    then
        ln -s $DIR/pm.py /usr/bin/pm
    fi
}

display_acpi_info()
{
    echo "Please restart your acpi daemon."
}

install_acpi()
{
    if [ -d /etc/acpi ]
    then
        ln -s $DIR/events_pm /etc/acpi/events/
        display_acpi_info
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
