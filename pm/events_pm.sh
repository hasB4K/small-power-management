#!/bin/bash

case "$1" in
    button/lid)
        case "$3" in
            close)
                python /usr/local/etc/pm/pm.py -p &
                ;;
            *)
                ;;
    esac
    ;;
    *)
        ;;
esac
