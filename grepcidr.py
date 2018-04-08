import ipaddress
import optparse
import os
import re
import sys

__version__ = "1.0.0"

STDIN_FILENAME = "-"
EX_NOT_FOUND = 1

ipv4_loose_re = re.compile(r'''
    \b
    \d+
    (\.\d+){3}
    \b
    ''',
    re.VERBOSE
    )
ipv6_loose_re = re.compile(r'''
    \b
    [0-9a-f:]{3,39}
    \b
    ''',
    re.VERBOSE
    )

if sys.version_info[0] >= 3:
    unicode = str

def make_pattern_list(pattern_list):
    patterns = []
    for pattern in pattern_list:
        pattern = unicode(pattern) # ip_network/ip_address wants unicode
        try:
            network = ipaddress.ip_network(pattern, strict=False)
        except ValueError:
            try:
                address_only = ipaddress.ip_address(pattern)
            except ValueError:
                sys.stderr.write(
                    "invalid network specification: %s\n" % pattern
                    )
                break
            else:
                try:
                    network = ipaddress.ip_network(
                        pattern + "/" + address_only.max_prefixlen,
                        strict=False,
                        )
                except ValueError:
                    sys.stderr.write(
                        "invalid IP specification: %s\n" % pattern
                        )
                    break
        patterns.append(network)
    return patterns

def build_parser():
    parser = optparse.OptionParser(
        usage="usage: %prog [options] [filename | - ..]",
        version=__version__,
        )
    parser.add_option("-i", "--invert",
        help="Invert IP address/range",
        dest="invert_range",
        action="store_true",
        default=False,
        )
    parser.add_option("-v",
        help="Show lines that do NOT match",
        dest="invert_match",
        action="store_true",
        default=False,
        )
    parser.add_option("-x", "--strict",
        help="Only match whole lines",
        dest="whole_lines",
        action="store_true",
        default=False,
        )
    parser.add_option("-o", "--only",
        help="Show the matching IPs",
        dest="only",
        action="store_true",
        default=False,
        )
    parser.add_option("-c", "--count",
        help="Show the count of matches instead of actual matches",
        dest="count",
        action="store_true",
        default=False,
        )
    parser.add_option("-q", "--quick",
        help="Quit after the first match",
        dest="quick",
        action="store_true",
        default=False,
        )
    parser.add_option("--with-filename",
        help="Print filename for each match "
            "(the default when there is more than one file to search)",
        dest="with_filename",
        action="store_true",
        default=False,
        )
    parser.add_option("--no-filename",
        help="Suppress filenames in output",
        dest="no_filename",
        action="store_true",
        default=False,
        )
    parser.add_option("-f", "--file",
        help="Read patterns from FILENAME",
        dest="filename",
        action="store",
        default=None,
        )
    parser.add_option("-e",
        help="Specify one or more patterns on the command-line",
        dest="patterns",
        action="append",
        default=[],
        )
    return parser

def process(options, patterns, iterable):
    """Search through iterable for lines matching patterns
    Yields either the entire line or the matching portion
    """
    for line in iterable:
        line = line.strip()
        addrs_to_test = [] # (address, source)
        try:
            addrs_to_test.append(
                (ipaddress.ip_address(unicode(line)), line)
                )
        except ValueError:
            pass
        if not options.whole_lines:
            for finder in (ipv4_loose_re, ipv6_loose_re):
                for match in finder.finditer(line):
                    v = match.group(0)
                    try:
                        addrs_to_test.append(
                            (ipaddress.ip_address(unicode(v)), v)
                            )
                    except ValueError:
                        pass
        keep_trying = True
        for addr, source_text in addrs_to_test:
            for pattern in patterns:
                if addr in pattern:
                    keep_trying = False
                    if options.only:
                        yield source_text
                    else:
                        yield line
                    break
            if not keep_trying: break

def main():
    parser = build_parser()
    options, args = parser.parse_args()
    
    if options.filename:
        with open(options.filename) as fp:
            for line in fp:
                line = line.strip()
                if line:
                    options.patterns.append(line)

    if not options.patterns:
        if args:
            options.patterns.append(args.pop(0))

    patterns = make_pattern_list(options.patterns)
    if not patterns:
        sys.stderr.write("no pattern specified\n")
        parser.print_help()
        return os.EX_USAGE

    if not args:
        args.append(STDIN_FILENAME) # read from stdin by default

    if options.quick:
        def report(fname, source):
            for _ in process(options, patterns, source):
                return True
            return False
    elif options.count:
        def report(fname, source):
            i = 0
            for _ in process(options, patterns, source):
                i += 1
            print("%s:%i" % (fname, i))
            return i > 0
    elif options.with_filename or (
            len(args) > 1 and not options.no_filename
            ):
        def report(fname, source):
            found = False
            for s in process(options, patterns, source):
                found = True
                print("%s: %s" % (fname, s))
            return found
    else:
        def report(fname, source):
            found = False
            for s in process(options, patterns, source):
                found = True
                print(s)
            return found

    found = False
    for fname in args:
        if fname == STDIN_FILENAME:
            found = report(fname, sys.stdin) or found
        else:
            with open(fname) as fp:
                found = report(fname, fp) or found
        if found and options.quick:
            break
    return os.EX_OK if found else EX_NOT_FOUND

if __name__ == "__main__":
    sys.exit(main())
