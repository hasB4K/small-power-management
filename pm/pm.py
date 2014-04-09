#!/bin/python
import subprocess
import argparse
import getpass
import pwd
import sys
import os


#DEFAULT VARIABLE
#Those variables should never be changed during the execution!
#dir_user_name = "/usr/local/etc/pm/user"
dir_user_name = os.path.dirname(os.path.realpath(__file__)) + "/user"
default_locker = "slimlock"
suspend_command = "systemctl suspend"


#CONFIG MANAGEMENT
def get_config(config):
    suspend, lock, locker = True, True, default_locker
    if (not os.path.isfile(config)):
        return (suspend, lock, locker)
    listconfs = open(config).read().split()
    for i in range(len(listconfs)):
        listconfs[i] = listconfs[i].split('=')
        if (len(listconfs[i]) != 2):
            continue
        if (listconfs[i][0] == "suspend" and listconfs[i][1] == "False"):
            suspend = False
        elif (listconfs[i][0] == "lock" and listconfs[i][1] == "False"):
            lock = False
        elif (listconfs[i][0] == "locker"):
            locker = listconfs[i][1]
    return (suspend, lock, locker)


def write_config(dirconf, configs):
    suspend, lock, locker = configs
    f = open(dirconf, "w")
    f.write("suspend=" + ("True" if suspend else "False") + "\n")
    f.write("lock=" + ("True" if lock else "False") + "\n")
    f.write("locker="+locker+"\n")
    f.close()


def display_config(configs):
    suspend, lock, locker = configs
    print("Lock option is " + ("Enabled" if lock else "Disabled"))
    print("Suspend option is " + ("Enabled" if suspend else "Disabled"))
    print("Locker is " + locker)


def perform_config(user, display, configs):     #The script execute commands
    suspend, lock, locker = configs
    os.environ["DISPLAY"] = display             #For i3lock
    if (lock and subprocess.call(["pgrep","slimlock"]) != 0):
        if (getpass.getuser() == user):
            subprocess.Popen(locker)
        else:
            subprocess.Popen(["su", user, "-c", locker ])
    if (suspend):
        subprocess.Popen(suspend_command.split())


#USER CONFIG MANAGEMENT
def check_user(user):
    for item in pwd.getpwall():
        if (item[0] == user):
            return False                        #The user exist. No errors.
    return True                                 #The user doesn't exist.


def get_user():
    error, user, display = False, "", ""
    if (not os.path.isfile(dir_user_name)):
        error = True
    else:
        lines = open(dir_user_name).read().split()
        if (len(lines) <= 1):
            error = True
        else:
            user = lines[0]
            display = lines[1]                  #We fetch the saved display var
            error = check_user(user)
    if (error):
        print("Please initialize correctly the username with -u/--user.")
        sys.exit(1)
    return (user, display)


def write_user(user):
    exist = os.path.isfile(dir_user_name)
    f = open(dir_user_name, "w")
    check_user(user)
    f.write(user+"\n")
    f.write(os.environ["DISPLAY"]+"\n")         #We save the display var
    if (not exist):                             #This should never happen!
        subprocess.Popen(["chmod", "666", dir_user_name])


#OPTIONS MANAGEMENT
def get_options(option):
    suspend = (option == "all" or option == "suspend")
    lock = (option == "all" or option == "lock")
    return (suspend, lock)


def get_new_value(enable, disable, conf):       #We privileged "Enable".
    #If you want to have "Disable" privileged uncomment the following line
    #return (not disable) and (conf or enable)
    return enable or (conf and not disable)


#ARGUMENTS MANAGEMENT
def set_options(user, dirconf, args, configs):
    conf_suspend, conf_lock, conf_locker = configs
    en_suspend, en_lock = get_options(args.enable)
    dis_suspend, dis_lock = get_options(args.disable)

    suspend = get_new_value(en_suspend,dis_suspend,conf_suspend)
    lock = get_new_value(en_lock,dis_lock, conf_lock)
    locker = conf_locker if args.locker == None else args.locker
    configs = (suspend, lock, locker)
    write_config(dirconf, configs)
    return configs


def fetch_args():
    parser = argparse.ArgumentParser(
            description="A power management scipt. Enable or disable Options.",
            epilog="Options are {lock, suspend, all}.")
    parser.add_argument("-p", "--perform", help="Perform power management",
            action="store_true")
    parser.add_argument("-u", "--user", help="Set user.")
    parser.add_argument("-l", "--locker", help="Set locker.")
    parser.add_argument("-d", "--disable",metavar="OPTIONS", choices =
            ["suspend", "lock", "all"], help='Disable options')
    parser.add_argument("-e", "--enable",metavar="OPTIONS", choices =
            ["suspend", "lock", "all"], help='Enable options [PRIVILEGED]')
    return parser.parse_args()


#MAIN
def main():
    args = fetch_args()
    if (args.user != None):
        write_user(args.user)
    user,display = get_user()
    dirconf = os.path.expanduser("~"+user+"/.pmconfig")
    configs = get_config(dirconf)
    if (args.disable != None or args.enable != None or args.locker != None):
        configs = set_options(user,dirconf, args, configs)
    if (args.perform):
        perform_config(user, display, configs)
    display_config(configs)


if __name__ == "__main__":
    main()
