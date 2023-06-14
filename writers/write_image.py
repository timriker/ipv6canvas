#!/usr/bin/env python3

# Blatant Self-Advertising on the IPv6 Canvas
# https://ewpratten.com/blog/ipv6-canvas/
# https://github.com/ewpratten/v6-canvas-writer

from PIL import Image
from pathlib import Path
from typing import List
from random import randrange
import subprocess

#DOMAIN_OFFSET = (155, 78-12)
DOMAIN_OFFSET = (20, 20)

def make_address(x: int, y: int, r: int, g: int, b: int) -> str:
    return f"2607:fa18:9ffe:4:{x:02x}{y:02x}:{r:02x}:{g:02x}:{b:02x}"

def image_to_addresses(image_path: Path, x_offset: int, y_offset: int) -> List[str]:
    # Load the image
    image = Image.open(image_path)
    image = image.convert('RGBA')
    x_offset = randrange(0, 256 - image.width);
    y_offset = randrange(0, 256 - image.height);

    # Convert to address list
    addresses = []
    for x in range(image.width):
        for y in range(image.height):
            # Get bitmap pixel
            r, g, b, a = image.getpixel((x, y))
            if a != 0:
                addresses.append(make_address(x + x_offset, y + y_offset, r, g, b))

    return addresses

def ping_address(address: str):
    print(f"Pinging {address}")
    subprocess.Popen(["ping", "-n", "-q", "-c", "1", address])

def main():
    addresses = image_to_addresses(Path(__file__).parent / "Tux-64.png", *DOMAIN_OFFSET)

    # Update the display
    for address in addresses:
        ping_address(address)

if __name__ == "__main__":
    main()