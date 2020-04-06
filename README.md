# Compute ETags and MD5s
The tool provides methods to calculate ETags for Objects on AWS S3, and also md5s, on local objects. It also allows comparing ETags or md5s to check the integrity of files, both locally and on AWS S3, given a list of files and their calculated ETags.
## Installation
```pip install compETAG```
## Usage
The following example will compute ETags for local files with the same chunk size used by AWS on S3:

```compute_etags -i <file1> <file2> .... -m etag -s 8MB -o out.txt```

Chunk size can be set to any desired value:

```compute_etags -i <file1> <file2> .... -m etag -s 1GB```

With mode fixed at `md5`, the resulting calculation will be md5 hashes:

```compute_etags -i <file1> <file2> .... -m md5```

To retrieve ETags from objects on AWS S3, setting mode to `s3uri` will redirect the tool to AWS S3, provided a bucket/s, key/s, and pattern/s (optional):

```compute_etags -m s3uri -b <bucket1> <bucket2> .. -k <key1> <key2> .. -p <pattern1> <pattern2> .. ```

To check the integrity of local files or AWS S3 objects, the following will calculate or retrieve ETags or md5s on the list of files provided in a text file, and compare the results to the provided hashings. The input text file lists pairs of ETag/md5 hash and afile name, on each row. 

* Checking ETags of local files:

    ```compute_etags -c <input.txt> -m etags```
    
* Checking md5s of local files:

    ```compute_etags -c <input.txt> -m md5```
    
* Checking ETags of AWS S3 objects:

    ```compute_etags -c <input.txt> -m s3uri -b <bucket1> <bucket2> .. -k <key1> <key2> .. ```
