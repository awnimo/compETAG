#!/usr/bin/env python3

"""\
Core methods to compute and compare ETags.
"""
import re
import hashlib
from typing import Union, Tuple, Pattern, List

import boto3
import numpy as np


def md5_checksum(filename: str) -> str:
    """\
    Compute the `MD5` digest of an object.

    :param filename:
        Path to file target file

    :return:
        `MD5` `hexdigest`
    """
    m = hashlib.md5()
    with open(filename, "rb") as f:
        for data in iter(lambda: f.read(1024 * 1024), b""):
            m.update(data)
    return m.hexdigest()


def etag_checksum(filename: str, chunk_size: int = 8 * 1024 ** 2) -> str:
    """\
    Compute the `ETag` digest (which is not the `MD5` digest) of an object.

    :param filename:
        Path to file target file
    :param chunk_size:
        Chunk size to hash

    :return:
        `ETag` `hexdigest`
    """
    md5s = []
    with open(filename, "rb") as f:
        for data in iter(lambda: f.read(chunk_size), b""):
            md5s.append(hashlib.md5(data).digest())
    m = hashlib.md5(b"".join(md5s))
    return "{}-{}".format(m.hexdigest(), len(md5s)) if len(md5s) > 1 else m.hexdigest()


def etag_compare(
    filename: str,
    etag: str,
    mode: Union["etag", "md5"] = "etag",
    chunk_size: int = 8 * 1024 ** 2,
) -> Tuple[bool, str, str]:
    """\
    Checks the integrity of files copied to `S3`.

    :param filename:
        Path to target file
    :param etag:
        `ETag` hash of `S3` object.
    :param mode:
        Choose mode for hash digest, `"etag"`, or `"md5"`.
    :param chunk_size:
        Chunk size to hash

    :return:
        Checksum values of the object
    """
    et = etag.strip('"')
    if mode == "etag":
        a = etag_checksum(filename, chunk_size=chunk_size)
    elif mode == "md5":
        a = md5_checksum(filename)
    if et == a:
        return True, a, et

    return False, a, et


def get_objects(
    bucket: str = None, key: str = None, pattern: Pattern = None
) -> List[str]:
    """\
    Filter keys of a bucket with objects matching a pattern.

    :param bucket:
        Bucket name
    :param key:
        Searchable object key
    :param pattern:
        Compiled regular expression object

    :return:
        list of filtered objects in bucket
    """
    s3r = boto3.resource("s3")
    bucket_s3 = s3r.Bucket(bucket)
    k = []
    for obj in bucket_s3.objects.filter(Prefix=key):
        if not pattern:
            hit = obj.key
        else:
            hit = pattern.search(obj.key)

        if hit:
            k.append(obj.key)

    return k


def get_object_etag(bucket: str = None, key: str = None) -> Tuple:
    """\
    Etag lookup for an object on Amazon S3 bucket.

    :param bucket:
        S3URI Bucket.
    :param key:
        S3URI Key.

    :return:
        `str`
    """
    obj = boto3.resource("s3").Object(bucket, key)
    return obj.e_tag.strip('"'), obj.key


def get_etags_from_s3uri(
    bucket: str = None, key: str = None, pattern: Pattern = None
) -> List:
    """\
    Retrieve ETags of keys in a bucket with objects matching a pattern.

    :param bucket:
        Bucket name.
    :param key:
        Searchable object key.
    :param pattern:
        Compiled regular expression object.

    :return:
        list of ETags.
    """
    k = get_objects(bucket, key, pattern)
    et = [get_object_etag(bucket, i) for i in k]

    return et if et else ""


def retrieve_s3uri_etag(
    bucket: Union[str, List[str]] = None,
    key: Union[str, List[str]] = None,
    pattern: Union[str, List[str], Pattern] = None,
) -> List:
    """\

    Parameters
    ----------
    bucket
        S3URI Bucket.
    key
        S3URI Keys.
    pattern
        Match s3 objects to pattern.
    """
    try:
        assert bucket, "Missing Bucket name!"
        assert key, "Missing Key!"
    except AssertionError:
        raise

    if isinstance(bucket, str):
        bucket = [bucket]
    if isinstance(key, str):
        key = [key]
    if isinstance(pattern, list):
        pattern = re.compile("|".join(pattern))

    data = []
    kwargs = {"pattern": pattern} if pattern else {}
    for Bucket in bucket:
        for Key in key:
            S3URI_data = get_etags_from_s3uri(bucket=Bucket, key=Key, **kwargs,)
            for S3URI_etag, S3URI_key in S3URI_data:
                data.append([S3URI_etag, S3URI_key])

    return data


def check_hashes(
    hashes: List = None,
    mode: str = "etag",
    chunk_size: int = None,
    bucket: Union[str, List[str]] = None,
    key: Union[str, List[str]] = None,
    pattern: Union[str, List[str], Pattern] = None,
) -> None:
    """\
    Check hashes of files listed in the input file.

    Parameters
    ----------
    hashes
        Pairs of md5/etag hashes and file names.
    mode
        Choose between `'etag'`, or `'md5'`, hash digest, or `'s3uri'` to get remote
        ETags.
    chunk_size
        Chunk size in bytes.
    bucket
        S3URI Bucket.
    key
        S3URI Keys.
    pattern
        Match s3 objects to pattern.

    """
    if mode in ["etag", "md5"]:
        try:
            e, i, m, cs = np.insert(
                np.array(hashes), 2, np.array([mode, chunk_size]).reshape(2, 1), axis=1,
            ).T
            res = map(etag_compare, i, e, m, cs.astype(int))
        except ValueError:
            e, i, m = np.insert(np.array(hashes), 2, np.array(mode), axis=1).T
            res = map(etag_compare, i, e, m)
        for r, v, el in zip(res, e, i):
            print("Comparing {}s for {} ...".format(mode, el))
            val, a, et = list(r)
            if val:
                print("\t".join([v, el, "Ok!"]))
            else:
                print("\t".join([v, el, "-->", a, "NO MATCH!"]))

    elif mode == "s3uri":
        if not pattern:
            pattern = re.compile("|".join([i for e, i in hashes]))
        data = retrieve_s3uri_etag(bucket=bucket, key=key, pattern=pattern,)

        for e, i in hashes:
            S3URI_etag = [n for n, m in data if i in m]
            S3URI_etag = set(S3URI_etag)
            if S3URI_etag:
                for et in S3URI_etag:
                    if et == e:
                        print("\t".join([e, i, "Ok!"]))
                    elif et != e:
                        print("\t".join([e, i, "-->", et, "NO MATCH!"]))
            else:
                print("{} not found!".format(i))
    else:
        print("Mode '{}' not recognized!".format(mode))

    return
