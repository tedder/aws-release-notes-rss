#!/usr/bin/python

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

