# 1.12 to 1.13 Comand Converter

Made by **TheAl_T**: [planetminecraft.com/member/theal_t](https://www.planetminecraft.com/member/theal_t)

Block data value -> block state database by: **Onnowhere**: [youtube.com/onnowhere2](https://www.youtube.com/onnowhere2)

# Usage

Pass filenames to convert as arguments or pass none for menu

# Syntax explanation:

First character:
- < - required token
- [ - optional token

Second character:
- @ - player name or entity selector
- ( - one of the literal values separated by '|'
- \* - one or more tokens (must be last)
- 0 - a number
- ~ - a number prefixed (or not) by '~'
- % - a number suffixed (or not) by 'L'
- = - Block data value or block state or -1 or *
- { - NBT tag
- : - raw JSON
- . - whatever
