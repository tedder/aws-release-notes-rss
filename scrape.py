#!/usr/bin/env python3
# coding: utf-8

# MIT license
# (see: http://www.opensource.org/licenses/mit-license.php)
#
# Copyright (c) 2014 Ted Timmons, ted@timmons.me
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import boto3
import requests
import PyRSS2Gen
import datetime
from io import StringIO
import sys
from dateutil.parser import parse

def item_to_rss(item):
    link = "https://aws.amazon.com/"+item["id"].replace("#","/")+"/"
    desc = item['additionalFields'].get('description', '')
    if not desc:
      item['additionalFields'].get('content', '')
    return PyRSS2Gen.RSSItem(
        author = item["author"],
        title = item["name"],
        link = link,
        guid = link,
        description = desc,
        pubDate = parse(item["dateUpdated"])
    )

request = requests.get("https://aws.amazon.com/api/dirs/releasenotes/items?order_by=DateCreated&sort_ascending=false&limit=25&locale=en_US")

if request.status_code == 500:
    sys.exit(0)

rss = PyRSS2Gen.RSS2(
    title = "Amazon AWS Release Notes scraped feed",
    link = "https://aws.amazon.com/releasenotes/",
    ttl = 6*60, # in minutes!
    docs = "https://github.com/tedder/aws-release-notes-rss",
    description = "new code and features from AWS",
    lastBuildDate = datetime.datetime.now(),
    items = map(item_to_rss, request.json()["items"])
)

rssfile = StringIO()
rss.write_xml(rssfile)


s3 = boto3.client("s3")
if "tedder" in map(lambda b: b["Name"], s3.list_buckets()["Buckets"]):
    s3.put_object(Bucket="tedder", Key="rss/aws-release-notes.xml", Body=rssfile.getvalue(), ContentType="application/rss+xml", ContentEncoding=request.encoding, CacheControl="max-age=21600,public", ACL="public-read")
else:
    print(rssfile.getvalue())
