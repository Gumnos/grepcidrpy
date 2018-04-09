# grepcidrpy
A grep-like tool for searching input with CIDR-style IPv4/IPv6 patterns

A tool somewhat like
http://www.pc-tools.net/unix/grepcidr/
only written from scratch in Python and provided under a BSD license.

## Usage

```
Usage: grepcidr.py [options] [filename | - ..]

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -v                    Show lines that do NOT match
  -x, --strict          Only match whole lines
  -o, --only            Show the matching IPs
  -c, --count           Show the count of matches instead of actual matches
  -q, --quick           Quit after the first match
  --with-filename       Print filename for each match (the default when there
                        is more than one file to search)
  --no-filename         Suppress filenames in output
  -f FILENAME, --file=FILENAME
                        Read patterns from FILENAME
  -e PATTERNS           Specify one or more patterns on the command-line
```

## Examples

Output all lines in `file.txt` with an IP address matching `192.168.0.0/24`

```
$ ./grepcidr.py 192.168.0.0/24 file.txt
```

Output all lines in `file.txt` with an IP address matching `FD::/64`

```
$ ./grepcidr.py FD::/64 file.txt
```

Output all lines in `file.txt` that do not match the network `192.168.0.0/24`

```
$ ./grepcidr.py -v 192.168.0.0/24 file.txt
```

Quickly test if `file.txt` contains any matches on the network
`192.168.0.0/24`

```
$ ./grepcidr.py -q 192.168.0.0/24 file.txt && echo yep || echo nope
```

Count the number of matches on the network `192.168.0.0/24` in `file.txt`

```
$ ./grepcidr.py -c 192.168.0.0/24 file.txt
```

Assuming `log.txt` has a number of fields per row but you only want the
IP addresses without all the other information

```
$ ./grepcidr.py -o 192.168.0.0/24 log.txt
```

Print `192.168.0.0/16` addresses associated with the current machine

```
$ ifconfig -a | ./grepcidr.py -o 192.168.0.0/24
```
