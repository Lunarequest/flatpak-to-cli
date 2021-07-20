#!/usr/bin/env python3

import subprocess
import configparser
import logging as log
import asyncio
import getpass
import gi

gi.require_version("Flatpak", "1.0")
gi.require_version("AppStreamGlib", "1.0")

from gi.repository import Flatpak


async def get_command_from_ini(flatpak: str):
    out = subprocess.run(
        ["flatpak", "info", "-m", f"{flatpak}"], stdout=subprocess.PIPE
    )
    parser = configparser.ConfigParser()
    parser.read_string(out.stdout.decode("utf-8"))
    return parser["Application"]["command"]


async def check_for_fallback_command(
    flatpak_id: str, command: str, arch: str, branch: str
) -> str:
    if flatpak_id == command:
        # this is for stuff like FlatSeal
        installation = Flatpak.get_system_installations()[0]
        app = installation.get_installed_ref(
            Flatpak.RefKind(0), flatpak_id, arch, branch
        )
        return app.get_appdata_name().lower().replace(" ", "-")
    else:
        return command


async def flatpak_to_alias():
    out = subprocess.run(["flatpak", "list", "--columns=ref"], stdout=subprocess.PIPE)
    flatpak_list = out.stdout.decode("utf-8").split("\n")
    alias_file = "#!/usr/bin/sh\n"
    aliases = []
    installations = Flatpak.get_system_installations()
    for installation in installations:
        apps = installation.list_installed_refs_by_kind(Flatpak.RefKind(0))
        arch = Flatpak.get_default_arch()
        for app in apps:
            if "BaseApp" in app.get_name():
                pass
            else:
                flatpak_id = app.get_name()
                command = await get_command_from_ini(flatpak_id)
                command = await check_for_fallback_command(
                    flatpak_id, command, arch, app.get_branch()
                )
                if command in aliases:
                    command = flatpak_id.split(".")[
                        -1
                    ]  # last part of flatpak id,normally app name
                    aliases.append(command)
                    alias_file += f"alias {command}='flatpak run {flatpak_id} &'\n"
                elif command:
                    aliases.append(command)
                    alias_file += f"alias {command}='flatpak run {flatpak_id} &'\n"
                else:
                    log.debug(f"{flatpak_id} has no command")
        print(alias_file)
        with open("flatpak_alias.sh", "w") as f:
            f.write(alias_file)
        f.close()


asyncio.get_event_loop().run_until_complete(flatpak_to_alias())
