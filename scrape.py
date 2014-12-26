#!/usr/bin/python

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

import boto
import requests
from lxml import html
import lxml
import PyRSS2Gen
import datetime
import StringIO
import sys
from dateutil.parser import parse

LINK = "https://aws.amazon.com/releasenotes/"
page = requests.get(LINK)
try:
  tree = html.fromstring(page.text)
except lxml.etree.XMLSyntaxError:
  if page.status_code == 500:
    sys.exit(0)
  print "page failed. %s" % page.status_code

rssitems = []

#items = tree.xpath('//itemsTable/div[@class="item"]')
items = tree.xpath('//div[@id="itemsTable"]/div[@class="item"]')

for item in items:
  title = item.xpath('normalize-space(div[@class="title"]/a/text())')
  itemlink = item.xpath('normalize-space(div[@class="title"]/a/@href)')
  desc = item.xpath('normalize-space(div[@class="desc"]/text())')
  modDate = item.xpath('normalize-space(div[@class="lastMod"]/text())')
  # strip off the initial text, the parser doesn't grok it.
  parsedDate = parse(modDate.replace('Last Modified: ', ''))
  rssitems.append(PyRSS2Gen.RSSItem(
    title = title,
    link = itemlink,
    guid = itemlink,
    description = desc,
    pubDate = parsedDate
  ))


rss = PyRSS2Gen.RSS2(
  title = "Amazon AWS Release Notes scraped feed",
  link = LINK,
  ttl = 3600, # cache 6hrs
  docs = "https://github.com/tedder/aws-release-notes-rss",
  description = "new code and features from AWS",
  lastBuildDate = datetime.datetime.now(),
  items = rssitems
)

rssfile = StringIO.StringIO()
rss.write_xml(rssfile)

s3bucket = boto.connect_s3().get_bucket('tedder')
s3key =  s3bucket.new_key('rss/aws-release-notes.xml')
s3key.set_metadata('Content-Type', 'application/rss+xml')
s3key.set_contents_from_string(rssfile.getvalue(), replace=True, reduced_redundancy=True, headers={'Cache-Control':'public, max-age=3600'}, policy="public-read")

