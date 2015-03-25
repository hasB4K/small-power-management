#!/bin/python
import subprocess
import argparse
import getpass
import pwd
import sys
import os


# DEFAULT VARIABLE
# Those variables should never be changed during the execution!
# dir_user_name = "/usr/local/etc/pm/user"
dir_user_name = os.path.dirname(os.path.realpath(__file__)) + "/user"
default_locker = ["slimlock"]
suspend_command = "systemctl suspend"


# CONFIG MANAGEMENT
def get_config(config):
    suspend, lock, locker = True, True, default_locker
    if (not os.path.isfile(config)):
        return (suspend, lock, locker)
    for line in open(config).read().split("\n"):
        line = line.split('=')
        if (len(line) <= 1):
            continue
        if (line[0] == "suspend" and line[1] == "False"):
            suspend = False
        elif (line[0] == "lock" and line[1] == "False"):
            lock = False
        elif (line[0] == "locker"):
            locker = line[1].split()
    return (suspend, lock, locker)


def write_config(dirconf, configs):
    suspend, lock, locker = configs
    f = open(dirconf, "w")
    f.write("suspend=%s\n" % ("True" if suspend else "False"))
    f.write("lock=%s\n" % ("True" if lock else "False"))
    f.write("locker=%s\n" % " ".join(locker))
    f.close()


def display_config(configs):
    suspend, lock, locker = configs
    print("Lock option is %s" % ("Enabled" if lock else "Disabled"))
    print("Suspend option is %s" % ("Enabled" if suspend else "Disabled"))
    print("Locker is %s" % " ".join(locker))


def perform_config(user, display, configs):     # The script execute commands
    suspend, lock, locker = configs
    os.environ["DISPLAY"] = display             # For i3lock
    if (lock and subprocess.call(["pgrep", locker[0]])):
        if (getpass.getuser() == user):
            subprocess.Popen(locker)
        else:
            subprocess.Popen(["su", user, "-c"] + locker)
    if (suspend):
        subprocess.Popen(suspend_command.split())


# USER CONFIG MANAGEMENT
def error_user():
    print("Please initialize correctly the username with -u/--user.")
    sys.exit(1)


def check_user(user):
    for item in pwd.getpwall():
        if (item[0] == user):
            return                              # The user exist. No errors.
    error_user()                                # The user doesn't exist.


def get_user():
    user, display = "", ""
    if (not os.path.isfile(dir_user_name)):
        error_user()
    else:
        lines = open(dir_user_name).read().split("\n")
        if (len(lines) <= 1):
            error_user()
        else:
            user = lines[0]
            display = lines[1]                  # We fetch the saved display
            check_user(user)
    return (user, display)


def write_user():
    user = getpass.getuser()
    exist = os.path.isfile(dir_user_name)
    f = open(dir_user_name, "w")
    f.write("%s\n" % user)
    f.write("%s\n" % os.environ["DISPLAY"])     # We save the display var
    if (not exist):                             # This should never happen!
        subprocess.Popen(["chmod", "666", dir_user_name])


# OPTIONS MANAGEMENT
def get_options(option):                        # Return Supend,Lock
    if (option == "all" or option == "a"):
        return (True, True)
    if (option == "suspend" or option == "s"):
        return (True, False)
    if (option == "lock" or option == "l"):
        return (False, True)
    return (False, False)


def get_new_value(enable, disable, conf):       # We privileged "Enable".
    # If you want to have "Disable" privileged uncomment the following line
    # return (not disable) and (conf or enable)
    return enable or (conf and not disable)


# ARGUMENTS MANAGEMENT
def set_options(user, dirconf, args, configs):
    conf_suspend, conf_lock, conf_locker = configs
    en_suspend, en_lock = get_options(args.enable)
    dis_suspend, dis_lock = get_options(args.disable)

    suspend = get_new_value(en_suspend, dis_suspend, conf_suspend)
    lock = get_new_value(en_lock, dis_lock, conf_lock)
    locker = conf_locker if args.locker is None else args.locker
    configs = (suspend, lock, locker)
    write_config(dirconf, configs)
    return configs


def fetch_args():
    options = ["suspend", "s", "lock", "l", "all", "a"]
    parser = argparse.ArgumentParser(
        description="A power management scipt. Enable or disable Options.",
        epilog="Options are {lock | l, suspend | s, all | a}.")
    parser.add_argument("-p", "--perform", help="Perform power management",
                        action="store_true")
    parser.add_argument("-u", "--user", help="Set user.", action="store_true")
    parser.add_argument("-l", "--locker", help="Set locker.", nargs="*")
    parser.add_argument("-d", "--disable", metavar="OPTIONS", choices=options,
                        help='Disable options')
    parser.add_argument("-e", "--enable", metavar="OPTIONS", choices=options,
                        help='Enable options [PRIVILEGED]')
    return parser.parse_args()


# MAIN
def main():
    args = fetch_args()
    if (args.user):
        write_user()
    user, display = get_user()
    dirconf = os.path.expanduser("~%s/.pmconfig" % user)
    configs = get_config(dirconf)
    if (args.disable or args.enable or args.locker):
        configs = set_options(user, dirconf, args, configs)
    if (args.perform):
        perform_config(user, display, configs)
    display_config(configs)


if __name__ == "__main__":
    main()
