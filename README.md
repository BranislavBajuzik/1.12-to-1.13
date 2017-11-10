# 1.12 to 1.13 Comand Converter

Made by **TheAl_T**: [planetminecraft.com/member/theal_t](https://www.planetminecraft.com/member/theal_t)

Block data value -> block state database by: **Onnowhere**: [youtube.com/onnowhere2](https://www.youtube.com/onnowhere2)

[Reddit](https://www.reddit.com/r/MinecraftCommands/comments/6prh1h/112_113_convert_script/)

# Usage

Use python 2.7

Main file:
- Pass filenames to convert as arguments or pass none for menu

MCEdit filter:
- Copy **both** files into your filters directory

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
- `=` Block data value or block state or `-1` or `*`
- `{` NBT tag
- `:` raw JSON
- `.` whatever