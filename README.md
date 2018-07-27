# 1.12 to 1.13 Comand Converter

Made by **TheAl_T**: [planetminecraft.com/member/theal_t](https://www.planetminecraft.com/member/theal_t)

HUGE thanks to **Onnowhere** for block state database, for testing and feedback: [youtube.com/onnowhere2](https://www.youtube.com/onnowhere2)

[Reddit](https://www.reddit.com/r/MinecraftCommands/comments/6prh1h/112_113_convert_script/)

# Usage

Use Python 2.7 _**or**_ 3.6

**Backup your world file before you use this tool**

The intended use is to drop both the `1_12to1_13.py` and `data.py` into the folder of the world you want to convert and run it there.

Available arguments:

Pass no arguments to display a menu
- `h`, `help`: Show help message and exit
- `strict_selectors`: Always sort selectors
- `menu {1,2,3,4}`: Use to access the menu from the CLI
- `files FILE [FILE ...]`: Use to convert only specific files. Overrides --menu

# Syntax explanation:

First character:
- `<` required token
- `[` optional token

Second character:
- `@` player name or entity selector
- `(` one of the literal values separated by `|`
- `*` one or more tokens (must be last)
- `0` a number
- `~` a number prefixed (or not) by `~`
- `%` a number suffixed (or not) by `L`
- `{` NBT tag
- `:` raw JSON
- `.` whatever
