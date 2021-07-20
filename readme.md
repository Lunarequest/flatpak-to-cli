# Flatpak to cli

This was inspired by pervious attempts to automate the aliasing of `flatpak run` commands to one word replacements. Thus making it more comfortable to replace applications such as [gitahead](https://github.com/flathub/io.github.gitahead.GitAhead) and [vscodium](com.vscodium.codium)

## Pros

- This script auto changes aliases of apps like flatseal to their names due to the binary name being the same as the actual name. This also is able to skip on Sdks, BaseApps, Platforms and runtimes which should not be aliased.

- This script also auto changes apps with conflicting Launch names to the last part of their flatpak id in lower cases when the binary conflicts with another one, an example would be vscodium and vscode.

- All packages required are in Stdlib in python.

## Cons

- Slow with a large amount of flatpaks that present situations like flatseal. This should be a very rare issues.

## Usage

Simply call the flatpak-to-cli like so

```bash
$ python flatpak-to-cli.py
```

You will see out put of how the `flatpak_alias.sh` file will look like this.

```bash
#!/usr/bin/sh
alias flatseal='flatpak run com.github.tchx84.Flatseal &'
alias wps='flatpak run com.wps.Office &'
alias gitahead='flatpak run io.github.gitahead.GitAhead &'
alias start-github-desktop='flatpak run io.github.shiftey.Desktop &'
alias flatpak-external-data-checker='flatpak run org.flathub.flatpak-external-data-checker &'
alias zoom='flatpak run us.zoom.Zoom &'
```

Finally in your ~/.bashrc source this file

```bash
source /path/to/flatpak_alias.sh
```
