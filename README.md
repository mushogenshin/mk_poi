# mk_prefs_overkill_installer
A simple, yet overkill, installer for CG softwares' preferences, custom brushes/materials, etc.

![](./img/mk_prefs_overkill_installer_mascot.png)

## What is this?

- An easy way, primarily for myself, to manage the installation process of all the custom settings of CG softwares, especially when I have to migrate them among computers.
- A utility (currently Windows only) for CG artists who are either fairly new to the softwares like ZBrush, Maya, etc., or who are already proficient with these softwares but do not want to bother to remember exactly where to copy the preferences/custom brushes/custom materials, etc. into.

## What is this not?

- It's not a library nor a collection of any software's preferences/presets/custom brushes/custom materials. "Template packages" are provided, but only served as placeholders.

## Why the installer?

- I strongly believe in customizing and optimizing one's own workflow as much as possible in softwares of daily usage. The disadvantage of customization, of course, however, is the inevitable feeling of being disabled when you have to work on anybody else's machine, but as these days I no longer have to come to other fellow artists' machines to supervise their works, I gain the luxury of almost always using my own machine to work. Therefore, the urge to customize every detail of my workflow becomes stronger.
- Managing preferences between various Autodesk Maya versions is not as much of a trouble as doing so with ZBrush. As far as how much I've been playing with ZScripting lately, I feel the ability to tweak the environment variables in order for ZBrush to recognize custom paths and look for custom "stuffs" (e.g. brushes, materials, plugins, etc.) is quite limited: normally one has to install all those custom things directly into the ZBrush installation folders! And for brushes, materials, plugins, etc., you have to copy each set to a corresponding subdirectory, otherwise they won't be found.
- I have 2D-artist students who are getting their feet wet with 3D, and I saw that the technical nitty gritty (of copying what to where) was somewhat a turning-off for them. Unfortunately this is especially true with ZBrush customization. There should be a quick way to get them going, to focus more on creating. Any time later down the road they can learn more about the exact details if they ever want to.

## How to use

It'd be best shown by examples first:

- Download the repository and extract it to any location on your computer. You will see an "installer.exe" and a "public_packages" folder.
- Inside the "public_packages" folder, there're dedicated "ZBrush", "Maya", etc. subdirectories for organization cleanliness. Imagine you're dealing with "ZBrush", then going inside:
    - Copy all your custom brushes into the "Custom_Brushes" folder
    - Copy all your custom materials into the "Custom_Materials" folder
    - Copy all your custom ZPlugins into the "Custom_Plugins" folder
- Now run the "installer.exe" (this likely requires admin rights). If ZBrush was installed into the default location (C:/Program Files/Pixologic), everything should work properly. (Otherwise, we can tweak the config files to make it work, see section below).
- Congratulations, you're now done with setting up those aspects of your ZBrush customization. The installer already detected all ZBrush versions you have on your machine, and applied the action for each of those versions.

## Tweaking the config files

    multi_versions: True
    dst_root: C:\Program Files\Pixologic
    dst_variant_pattern: '^ZBrush\s()'
    dst_subdir: ZStartup\ZPlugs64

- `multi_versions`: set this to `False` if you only want the installer to execute for a specific software version.
- `dst_root`: the path to right before where the variation of versions happen, e.g. "ZBrush 4R8", "ZBrush 2018", "ZBrush 2019", are "variants", and the dst_root should be where all these variants reside.
- `dst_variant_pattern`: the regular expression used to distinguish what subdirectory is valid and invalid when the installer search right beneath the dst_root, e.g. for Maya that is "^20\d\d$" to target the "2018", "2019", etc., subdirectories.
    - If `muti_versions` is set to `False`, just leave this `dst_variant_pattern` blank, and put the exact version you want in the `dst_root`, e.g.: set `dst_root` to `C:\Program Files\Pixologic\2020` if you only want to perform install only for ZBrush 2020.
- `dst_subdir`: the appendage to the path to navigate to the final destination. For Maya scripts this usually is "scripts". With ZBrush this needs to be tweaked for packages of brushes, materials, etc., (templates are provided). Just leave this empty if there's no need to go levels deeper than the `dst_root`.
