#!/usr/bin/env python3

"""\
Parser for command line arguments.
"""

import argparse
import re


def validate_chunks(chunksize: str = "8MB") -> int:
    """\
    Parameters
    ----------

    chunksize
        Chunk size in bytes with or without KB, MB, GB, TB suffixes.

    Returns
    -------
        Size value of read chunks.
    """
    convert_literals = {
        "": 1024 ** 0,
        "KB": 1024 ** 1,
        "MB": 1024 ** 2,
        "GB": 1024 ** 3,
        "TB": 1024 ** 4,
    }
    # get suffix and value
    m = re.fullmatch(r"(\d+)([KMGT]B)?", chunksize)
    if not m:
        raise ValueError("invalid chunk size {}!".format(chunksize))
    size = convert_literals[m.groups("")[1]]
    chunksize = int(m.groups("")[0]) * size

    return chunksize


def parse_arguments(argsv: str = None) -> argparse:
    """\

    Parameters
    ----------

    argsv
        command line arguments

    Returns
    -------
        :class:`~argparse.ArgumentParser`
    """
    parser = argparse.ArgumentParser(fromfile_prefix_chars="@", add_help=False)

    parser.add_argument(
        "-i", "--infiles",
        dest="infiles",
        action="store",
        nargs="+",
        help="Input one or more file names to compute Etags."
    )

    parser.add_argument(
        "-s", "--chunk_size",
        dest="chunk_size",
        default="8MB",
        type=validate_chunks,
        nargs = "?",
        action="store",
        help="Read chunks in bytes with the defined size. Default: `8MB` chunks. "
             "Acceptable literal values: KB, MB, GB, TB, or none (bytes)."
    )

    parser.add_argument(
        "-c", "--check",
        dest="check",
        action="store_true",
        help="Check and compare Etags."
    )

    args = parser.parse_args(argsv)

    return args
