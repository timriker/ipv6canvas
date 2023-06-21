#!/usr/bin/env python3

# python script to ping IPv6 space canvas given an image
# https://github.com/serverscanning/place-ipv6-server
# Copywrite (c) Tim Riker <timriker@gmail.com>

import argparse
import socket
import struct
import random
from PIL import Image
import time

def old_parse_ipv6_address(ipv6_prefix, x, y, red, green, blue, alpha):
    address = ipv6_prefix + ':'
    address += '1' + format(x, 'x').zfill(3) + ':' + format(y, 'x').zfill(4) + ':'
    address += format(red, 'x').zfill(2) + ':' + format(green, 'x').zfill(2) + format(blue, 'x').zfill(2)
    return address

def parse_ipv6_address(ipv6_prefix, x, y, red, green, blue, alpha, use_half=False):
    address = ipv6_prefix + ':'
    segment_x = '1' if not use_half else '2'
    segment_x += format(x, 'x').zfill(3) if not use_half else format(x * 2, 'x').zfill(3)
    segment_y = format(y, 'x').zfill(4) if not use_half else format(y * 2, 'x').zfill(4)
    address += segment_x + ':' + segment_y + ':'
    address += format(red, 'x').zfill(2) + ':' + format(green, 'x').zfill(2) + format(blue, 'x').zfill(2)
    return address

def create_icmpv6_packet(address, reply=False, calculate_checksum=False):
    ICMPV6_TYPE_ECHO_REQUEST = 128
    ICMPV6_TYPE_ECHO_REPLY = 129

    if reply:
        type_ = ICMPV6_TYPE_ECHO_REPLY
    else:
        type_ = ICMPV6_TYPE_ECHO_REQUEST

    checksum = 0
    identifier = random.randint(0, 65535)
    sequence_number = 1

    # Construct the ICMPv6 packet
    packet = struct.pack('!BBHHH', type_, 0, checksum, identifier, sequence_number)

    if calculate_checksum:
        packet_checksum = calculate_checksum(packet)

        # Replace the checksum field with the calculated checksum
        packet = packet[:2] + packet_checksum + packet[4:]

    return packet

def calculate_checksum(data):
    checksum = 0

    if len(data) % 2 == 1:
        data += b'\x00'

    for i in range(0, len(data), 2):
        word = (data[i] << 8) + data[i + 1]
        checksum += word

    while checksum >> 16:
        checksum = (checksum & 0xFFFF) + (checksum >> 16)

    checksum = ~checksum & 0xFFFF

    return struct.pack('!H', checksum)

def ping_ipv6_site(image_file, ipv6_prefix='::', resize=None, offset=None, alpha=60, verbose=False, loop=False, reply=False, delay=0, output=False, half=False, calculate_checksum=False):
    # Load the image using PIL
    try:
        im = Image.open(image_file).convert("RGBA")
    except IOError:
        print(f"Failed to open image file: {image_file}")
        return

    # Resize the image if specified
    if resize:
        try:
            resize_width, resize_height = map(int, resize.split('x'))
            im = im.resize((resize_width, resize_height))
        except ValueError:
            print(f"Invalid resize format: {resize}")
            return

    # Calculate the offset if specified
    if offset:
        try:
            offset_x, offset_y = map(int, offset.split('x'))
        except ValueError:
            print(f"Invalid offset format: {offset}")
            return
    else:
        offset_x, offset_y = 0, 0

    # list of addresses to ping
    addresses = []

    # Iterate through each pixel in the image
    for y in range(im.height):
        for x in range(im.width):
            # Calculate the coordinates with offset
            coord_x = x + offset_x
            coord_y = y + offset_y

            # Ignore pixels with alpha less than the specified value
            red, green, blue, pixel_alpha = im.getpixel((x, y))
            if pixel_alpha < alpha:
                continue

            # Construct the IPv6 address based on the pixel values
            address = parse_ipv6_address(ipv6_prefix, coord_x, coord_y, red, green, blue, pixel_alpha, half)

            addresses.append(address)

    # Shuffle the list
    random.shuffle(addresses)

    if output:
        print(address)
    else:
        # Create a socket for sending ICMPv6 packets
        sock = socket.socket(socket.AF_INET6, socket.SOCK_RAW, socket.IPPROTO_ICMPV6)

        # Increase the socket buffer size
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 2 * 1024 * 1024)

        while True:
            for address in addresses:
                # Create the ICMPv6 packet
                packet = create_icmpv6_packet(address, reply=reply, calculate_checksum=calculate_checksum)

                # Send the ICMPv6 packet
                while True:
                    try:
                        sock.sendto(packet, (address, 0, 0, 0))
                        break
                    except socket.error as e:
                        if e.errno == 105:
                            if verbose:
                                print("No buffer space available, retrying...", end="\r")
                            time.sleep(.01)
                        else:
                            print(f"Failed to send ICMPv6 packet to {address}: {e}")
                            break

                if verbose:
                    print(f"Sent ICMPv6 packet to {address}", end='\r')

                time.sleep(delay / 1000)

            if not loop:
                break


        # Close the socket
        sock.close()

# Command-line argument parsing
parser = argparse.ArgumentParser(description='Ping an IPv6 site using raw sockets based on image pixel values.')
parser.add_argument('image', help='PNG image file')
parser.add_argument('--prefix', '-P', help='IPv6 prefix (default: ::)')
parser.add_argument('--resize', '-r', help='Resize image in format XxY (e.g., 640x480)')
parser.add_argument('--offset', '-o', help='Offset in format XxY (e.g., 100x50)')
parser.add_argument('--alpha', '-A', type=int, default=60, help='Ignore pixels with alpha less than this value (default: 60)')
parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
parser.add_argument('--loop', '-l', action='store_true', help='Loop through the image continuously')
parser.add_argument('--reply', '-R', action='store_true', help='Send ICMPv6 reply packets instead of request packets')
parser.add_argument('--delay', '-d', type=int, default=0, help='Delay in milliseconds between sending packets (default: 0)')
parser.add_argument('--output', '-O', action='store_true', help='Write IP addresses to stdout instead of sending pings')
parser.add_argument('--half', '-H', action='store_true', help='Skip every other IP on both x and y axes, use "2" in IP address instead of "1"')
parser.add_argument('--checksum', '-c', action='store_true', default=False, help='Calculate checksums in the ICMPv6 packets')

args = parser.parse_args()

# Call the ping_ipv6_site() function with command-line arguments
ping_ipv6_site(args.image, args.prefix, args.resize, args.offset, args.alpha, args.verbose, args.loop, args.reply, args.delay, args.output, args.half, args.checksum)
