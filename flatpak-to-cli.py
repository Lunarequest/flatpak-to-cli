#!/usr/bin/env python3

import configparser
import logging as log
import asyncio
import gi

gi.require_version("Flatpak", "1.0")
gi.require_version("AppStreamGlib", "1.0")

from gi.repository import Flatpak

arch = Flatpak.get_default_arch()


async def gen_command(flatpak: Flatpak.InstalledRef) -> str:
    parser = configparser.ConfigParser()
    try:
        parser.read_string(flatpak.load_metadata().get_data().decode("utf-8"))
        command = parser["Application"]["command"]
        flatpak_id = flatpak.get_name()
        if flatpak_id == command:
            # this is for stuff like FlatSeal
            return flatpak.get_appdata_name().lower().replace(" ", "-")
        return command
    except Exception:
        flatpak_id = flatpak.get_name()
        return flatpak_id.split(".")[-1]


async def flatpak_to_alias():
    alias_file = "#!/usr/bin/sh\n"
    aliases = []
    installations = Flatpak.get_system_installations()
    for installation in installations:
        apps = installation.list_installed_refs_by_kind(Flatpak.RefKind(0))
        for app in apps:
            if "BaseApp" in app.get_name():
                pass  # for stuff like the Electron base app
            else:
                command = await gen_command(app)
                flatpak_id = app.get_name()
                if command in aliases:
                    # last part of flatpak id,normally app name
                    command = flatpak_id.split(".")[-1]
                    aliases.append(command)
                    alias_file += f"alias {command}='flatpak run {flatpak_id}'\n"
                else:
                    aliases.append(command)
                    alias_file += f"alias {command}='flatpak run {flatpak_id}'\n"
        print(alias_file)
        with open("flatpak_alias.sh", "w") as f:
            f.write(alias_file)
        f.close()


asyncio.get_event_loop().run_until_complete(flatpak_to_alias())
