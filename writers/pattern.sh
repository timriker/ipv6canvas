#! /bin/bash
prefix=2607:fa18:9ffe:4
color=80:80:80
color=1a:2a:54
for y1 in {0..9} {a..f} ; do
	for y2 in {0..9} {a..f} ; do
		for x1 in {0..9} {a..f} ; do
			for x2 in {0..9} {a..f} ; do
				echo -e -n $prefix:$x1$x2:$y1$y2:$x2$x1$y2$y1:$y2${y1}ff\\r
				ping -n -W 0.0001 -q -c 1 $prefix:$x1$x2:$y1$y2:$x2$y1$y2$x1:$y2${y1}ff >/dev/null &
			done
		done
	done
done
