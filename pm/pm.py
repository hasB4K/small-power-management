#!/usr/bin/env python

from typing import Dict, List, Optional, Self

import argparse
import getpass
import os
import subprocess
import sys

import pydantic
import yaml


class Config(pydantic.BaseModel):
    user: Optional[str] = None
    enable_suspend: bool = True
    enable_lock: bool = True
    locker_cmd: str = "i3lock"
    suspend_cmd: str = "systemctl suspend"
    envs_to_save: List[str] = ["DISPLAY"]

    @classmethod
    def filepath(self, user):
        return os.path.expanduser(f"~{user}/.pmconfig.yaml")

    def update_and_save_config(self, args):
        should_save_config = False
        for k in ["enable_suspend", "enable_lock", "locker_cmd", "suspend_cmd", "envs_to_save"]:
            if getattr(args, k) is None:
                continue
            should_save_config = True
            setattr(self, k, getattr(args, k))
        if should_save_config:
            self.write()
        return self

    def write(self, user=None) -> Self:
        self.user = user or self.user
        if "DISPLAY" not in self.envs_to_save:
            self.envs_to_save.append("DISPLAY")
        with open(self.filepath(self.user), "w") as file:
            yaml.safe_dump(self.model_dump(), file)

    @classmethod
    def load(cls, user):
        if not os.path.exists(cls.filepath(user)):
            cls().write(user)
        with open(cls.filepath(user), "r") as file:
            return cls(user=user, **yaml.safe_load(file))

    @classmethod
    def display(cls, user):
        print("CONFIG:")
        with open(cls.filepath(user), "r") as f:
            config_str = "\n    ".join(f.read().split("\n"))
            print("    " + config_str.strip())


class UserInfo(pydantic.BaseModel):
    user: str
    envs: Dict[str, str]

    @classmethod
    def filepath(self):
        return "/tmp/pm_user_info"

    @classmethod
    def create_and_write_from_config(cls, config: Config) -> Self:
        user_info = cls(user=getpass.getuser(),
                        envs={k: os.environ[k] for k in config.envs_to_save if k in os.environ})
        with open(cls.filepath(), "wt") as file:
            yaml.safe_dump(user_info.model_dump(), file)
        return user_info

    @classmethod
    def load(cls):
        if not os.path.isfile(cls.filepath()):
            print("Please initialize correctly the username with --set-user-info.")
            sys.exit(1)
        with open(cls.filepath(), "r") as file:
            return cls(**yaml.safe_load(file))


def apply_power_management(user_info, config):
    os.environ.update({k: v for k, v in user_info.envs.items()})
    locker_cmd = config.locker_cmd.split()
    if (config.enable_lock and subprocess.call(["pgrep", locker_cmd[0]])):
        if (getpass.getuser() != user_info.user):
            locker_cmd = [
                "sudo",
                f"--preserve-env={','.join(user_info.envs.keys())}",
                f"--user={user_info.user}"
            ] + locker_cmd
        subprocess.Popen(locker_cmd)
    if (config.enable_suspend):
        subprocess.Popen(config.suspend_cmd.split())


def validate_option(enable_option, disable_option, possible_options):
    enable_option = (enable_option in possible_options) or None
    disable_option = (disable_option in possible_options) or None
    if enable_option and disable_option:
        print("You cannot enable and disable the same option.")
        sys.exit(1)
    if enable_option is None and disable_option is None:
        return None
    return enable_option or not disable_option


def fetch_args():
    lock_options, suspend_options = ["lock", "all"], ["suspend", "all"]
    options = sorted(set(lock_options) | set(suspend_options))

    parser = argparse.ArgumentParser(
        description="A power management scipt. Enable or disable Options.",
        epilog="Options are {lock | l, suspend | s, all | a}.")
    parser.add_argument("--apply", help="Apply power management", action="store_true")
    parser.add_argument("--set-user-info", help="Set user.", action="store_true")
    parser.add_argument("--disable", metavar="OPTIONS", choices=options, help='Disable options')
    parser.add_argument("--enable", metavar="OPTIONS", choices=options, help='Enable options')
    parser.add_argument("--locker-cmd", help="Set locker command.", nargs="*")
    parser.add_argument("--suspend-cmd", help="Set suspend command.", nargs="*")
    parser.add_argument("--envs-to-save", help="Set envs variables to save.", nargs="*")

    args = parser.parse_args()
    args.locker_cmd = " ".join(args.locker_cmd) if args.locker_cmd else None
    args.suspend_cmd = " ".join(args.suspend_cmd) if args.suspend_cmd else None
    args.enable_suspend = validate_option(args.enable, args.disable, suspend_options)
    args.enable_lock = validate_option(args.enable, args.disable, lock_options)
    return args


def main():
    args = fetch_args()
    if args.set_user_info:
        print("Setting user info.")
        UserInfo.create_and_write_from_config(Config.load(getpass.getuser()))
        return

    user_info = UserInfo.load()
    config = Config.load(user=user_info.user).update_and_save_config(args)
    if args.apply:
        apply_power_management(user_info, config)
    else:
        Config.display(user=user_info.user)


if __name__ == "__main__":
    main()
