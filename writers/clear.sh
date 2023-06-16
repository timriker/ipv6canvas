#! /bin/bash
prefix=2607:fa18:9ffe:4
#color=8080:80ff
color=1a2a:54ff
for y1 in {0..9} {a..f} ; do
	for y2 in {0..9} {a..f} ; do
		for x1 in {0..9} {a..f} ; do
			for x2 in {0..9} {a..f} ; do
				echo -e -n $prefix:00$x1$x2:00$y1$y2:$color\\r
				ping -n -W 0.0001 -q -c 1 $prefix:00$x1$x2:00$y1$y2:$color >/dev/null
			done
		done
	done
done
