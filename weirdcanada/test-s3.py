"""
Takes a list of filenames via standard input and uploads them to Amazon S3.

Requires S3.py:
    http://developer.amazonwebservices.com/connect/entry.jspa?externalID=134&categoryID=47

Usage:
    cd /directory/with/media/files/
    find | grep -v ".svn" | python /path/to/update_s3.py

Before you use this, change the AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY and
BUCKET_NAME variables at the top of the file.

You can run this multiple times on the same files -- it'll just override the
files that were in your S3 account previously.
"""

import mimetypes
import os.path
import sys
import S3 # Get this from Amazon

AWS_ACCESS_KEY_ID = 'AKIAJBNFKV6LNNYTHVHQ'
AWS_SECRET_ACCESS_KEY = 'WmilE1dvTv678FMbA98wFI3OvkIyf5JuwsENGisR'
BUCKET_NAME = 'weird_canada'

def update_s3():
    print 'entering connection'
    conn = S3.AWSAuthConnection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    print 'connected'
    filename = 'burnt.jpg'
    print "Uploading %s" % filename
    filedata = open(filename, 'rb').read()
    content_type = mimetypes.guess_type(filename)[0]
    if not content_type:
        content_type = 'text/plain'
    conn.put(BUCKET_NAME, filename, S3.S3Object(filedata),
        {'x-amz-acl': 'public-read', 'Content-Type': content_type})

if __name__ == "__main__":
    update_s3()
