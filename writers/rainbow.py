#!/usr/bin/env python3
import subprocess

def pingit(x, y, color):
    addr = f"2607:fa18:9ffe:4:{x:04x}:{y:04x}:{color[0]:02x}{color[1]:02x}:{color[2]:02x}ff"
    subprocess.run(["ping6", "-c1", addr])

red    = (0xcf, 0x0f, 0x0f)
orange = (0xff, 0xa0, 0x00)
yellow = (0xff, 0xd2, 0x00)
green  = (0x36, 0xa0, 0x30)
blue   = (0x1b, 0x77, 0xcd)
purple = (0x4d, 0x14, 0x8c)

row = [purple, purple, blue, blue, green, green, yellow, yellow, orange, orange, red, red]

for y in range(255, 243, -1):
    for x, color in enumerate(row):
        pingit(255-x, y, color)
    row.pop(0)
