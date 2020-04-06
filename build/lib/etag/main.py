#!/usr/bin/env python3

import sys

from .argsParser import parse_arguments


def main(argv):
    args = parse_arguments(argv)
    print(args)


if __name__ == "__main__":
    main(sys.argv[1:])
