# 1.12 to 1.13 Comand Converter

Made by **TheAl_T**: [planetminecraft.com/member/theal_t](https://www.planetminecraft.com/member/theal_t)

HUGE thanks to **Onnowhere** for block state database, for testing and feedback: [youtube.com/onnowhere2](https://www.youtube.com/onnowhere2)

[Reddit](https://www.reddit.com/r/MinecraftCommands/comments/6prh1h/112_113_convert_script/)

# Usage

Use python 2.7 _**or**_ 3.6

Main file:
- When running the file, pass names of files you wish to convert as arguments or pass none for menu

MCEdit filter:
- Copy `1_12to1_13.py`, `1_12to1_13aMCEditPlugin.py` and `data.py` into your filters directory

# Syntax explanation:

First character:
- `<` required token
- `[` optional token

Second character:
- `@` player name or entity selector
- `(` one of the literal values separated by `'|'`
- `*` one or more tokens (must be last)
- `0` a number
- `~` a number prefixed (or not) by `'~'`
- `%` a number suffixed (or not) by `'L'`
- `{` NBT tag
- `:` raw JSON
- `.` whatever
