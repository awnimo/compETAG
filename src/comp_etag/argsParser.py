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


def parse_arguments(argsv: str = "") -> argparse.Namespace:
    """\

    Parameters
    ----------

    argsv
        command line arguments

    Returns
    -------
        :class:`~argparse.Namespace`
    """
    parser = argparse.ArgumentParser()
    group1 = parser.add_mutually_exclusive_group()
    group2 = parser.add_mutually_exclusive_group()

    group2.add_argument(
        "-i",
        "--infiles",
        dest="infiles",
        action="store",
        nargs="+",
        help="Input one or more file names to compute ETags.",
    )

    parser.add_argument(
        "-s",
        "--chunk_size",
        dest="chunk_size",
        action="store",
        default="8MB",
        type=validate_chunks,
        nargs="?",
        help="Read chunks in bytes with the defined size. Default: `'8MB'` chunks. "
        "Acceptable literal values: `'KB'`, `'MB'`, `'GB'`, `'TB'`, or `None` ("
        "`'bytes'`).",
    )

    parser.add_argument(
        "-m",
        "--mode",
        dest="mode",
        default="etag",
        choices=["etag", "md5", "s3uri"],
        action="store",
        nargs="?",
        help="Choose between `'etag'` or `'md5'` for hash digest. Or, retrieve Etag "
        "of Key on S3URI. This option requires providing a Bucket name and a Key.",
    )

    group2.add_argument(
        "-b",
        "--bucket",
        dest="bucket",
        action="store",
        nargs="+",
        help="S3URI Bucket.",
    )

    parser.add_argument(
        "-k", "--key", dest="key", action="store", nargs="+", help="S3URI Key.",
    )

    parser.add_argument(
        "-p",
        "--pattern",
        dest="pattern",
        action="store",
        nargs="+",
        help="Look for Keys in Bucket matching the pattern.",
    )

    group1.add_argument(
        "-c",
        "--check",
        dest="check",
        action="store",
        nargs="?",
        help="Read input file content, compare hash tables and exit.",
    )

    group1.add_argument(
        "-o",
        "--fout",
        dest="fout",
        action="store",
        nargs="?",
        help="Save computed ETags to provided filename.",
    )

    args = parser.parse_args(argsv)

    return args
