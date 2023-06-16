#!/usr/bin/env python3

# https://git.sr.ht/~jae/PixelPinger

# This program sends IPv6 pings to a target in order to change pixels.
# It was made during the IPv6Canvas experiment.

from platform import system
from sys import argv
from socket import socket, AF_INET6, SOCK_RAW, IPPROTO_ICMPV6
import time, random

from PIL import Image

base_address = "2607:fa18:9ffe:4"
pixels = []

sock = socket(AF_INET6, SOCK_RAW, IPPROTO_ICMPV6)

def make_address(x, y, r, g, b, a):
    final_address = f"{base_address}:{x:04x}:{y:04x}:{r:02x}{g:02x}:{b:02x}{a:02x}"

    return final_address

def do_ping(dest_addr, timeout=1):
    #print(f"Rendering current: {dest_addr}", end="\r")

    try:
        # Raw sockets, who cares, it's fast
        sock.sendto(b"\x80\0\0\0\0\0\0\0", (dest_addr, 0))
    except:
        # We don't care about failing
        # The pixel is usually re-written in next pass
        pass

def write_to_file(filename):
    file = open(filename, "w")
    for addr in pixels:
        file.write(f"{addr}\n")
    file.close()

def make_image_and_start(ox, oy, image_path, to_file=False, filename="image.txt"):
    image = Image.open(image_path).convert("RGBA")
    max_w, max_h = image.size

    curr_w, curr_h = 0, 0

    start_w = int(ox)
    start_h = int(oy)

    max_w -= 1
    max_h -= 1

    # Now, let's convert the image
    while True:
        coordinates = x, y = curr_w, curr_h
        r, g, b, a = image.getpixel(coordinates)

        # Check for alpha (transparency support)
        if a > 0:
            pixels.append(make_address(curr_w + start_w, curr_h + start_h, r, g, b, a))

        # Basic printer that goes left-> right and starts again
        if curr_h == max_h:
            curr_h = 0
            curr_w += 1
            print(f"Converting: {x},{y} -> {r}:{g}:{b}/{a}", end="\r")
        else:
            curr_h += 1

        if curr_w == max_w and curr_h == max_h:
            curr_h = start_h
            curr_w = start_w
            break

    # shuffle pixels randomly
    random.shuffle(pixels)

    if not to_file:
        while True:
            print("Sending", len(pixels), "pings")
            for addr in pixels:
                time.sleep(0.00001)
                do_ping(addr)
            break
    else:
        write_to_file(filename)

if __name__ == "__main__":
    if not argv or len(argv) < 4 or "--help" in argv:
        print(
            "Usage: pixelpinger.py <offset x> <offset y> <image file> [true/false generate to file] [filename]"
        )
        exit(1)

    print(argv)

    if len(argv) > 1 and len(argv) < 6:
        make_image_and_start(argv[1], argv[2], argv[3])
    elif len(argv) == 6:
        make_image_and_start(argv[1], argv[2], argv[3], argv[4], argv[5])
