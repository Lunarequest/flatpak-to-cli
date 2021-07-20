#!/usr/bin/env python3

import subprocess
import configparser
import logging as log
import asyncio
import getpass
from bs4 import BeautifulSoup as bs


async def get_ini(flatpak):
    out = subprocess.run(
        ["flatpak", "info", "-m", f"{flatpak}"], stdout=subprocess.PIPE
    )
    parser = configparser.ConfigParser()
    parser.read_string(out.stdout.decode("utf-8"))
    return parser


async def get_command(flatpak, command) -> str:
    if flatpak == command:
        # this is for stuff like FlatSeal
        with open(
            f"/home/{getpass.getuser()}/.local/share/flatpak/appstream/flathub/x86_64/active/appstream.xml",
            "r",
        ) as f:
            next_line = False
            content = f.readlines()
            for line in content:
                if next_line:
                    return (
                        line.replace("<name>", "")
                        .replace("</name>", "")
                        .strip()
                        .replace(" ", "-")
                        .lower()
                    )
                if flatpak in line:
                    next_line = True
            print(f"unable to find alias for {flatpak} falling back to {flatpak}")
            return flatpak
    else:
        return command


async def flatpak_to_alias():
    out = subprocess.run(["flatpak", "list", "--columns=ref"], stdout=subprocess.PIPE)
    flatpak_list = out.stdout.decode("utf-8").split("\n")
    alias_file = "#!/usr/bin/sh\n"
    aliases = []
    for flatpak in flatpak_list:
        if (
            flatpak == ""
            or "Sdk" in flatpak
            or "BaseApp" in flatpak
            or "Platform" in flatpak
            or "Gtk3theme" in flatpak
        ):
            pass
        else:
            try:
                ini = await get_ini(flatpak)
                try:
                    application = ini["Application"]
                    command_to_run = f"flatpak run {application['name']} &"
                    command = await get_command(
                        flatpak.replace("x86_64/stable", "").strip("/"),
                        application["command"],
                    )
                    if command in aliases:
                        command = (
                            flatpak.replace("x86_64/stable", "")
                            .strip("/")
                            .split(".")[-1]
                        )
                        alias_file += f"""alias {command}='{command_to_run}'\n"""
                        aliases.append(command)
                    elif command:
                        alias_file += f"""alias {command}='{command_to_run}'\n"""
                        aliases.append(command)
                    else:
                        pass
                except:
                    log.debug(f"{flatpak} not a application")
            except:
                log.error(f"{flatpak} ini is broken")
    print(alias_file)
    with open("flatpak_alias.sh", "w") as f:
        f.write(alias_file)


asyncio.get_event_loop().run_until_complete(flatpak_to_alias())
