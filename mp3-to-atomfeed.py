#!/usr/bin/env python3

# Todo:
# - testen
# - Mehr id3-Tags verwenden
# - nicht auf TLEN verlassen
# - ID3-Chapters

import sys
from os import stat, listdir, path
from xml.etree.ElementTree import Element, SubElement, Comment, tostring, ElementTree
import time
from datetime import datetime, timezone
import urllib.parse
from hashlib import md5
from mutagen.id3 import ID3,ID3NoHeaderError,TRSN,TPE1,TALB,TRCK,TIT2,COMM,TYER,TDAT,TIME,TLEN,TDRL,CTOC,CHAP,CTOCFlags

if len(sys.argv) < 4 or len(sys.argv) > 5:
    print("Usage:", file=sys.stderr)
    print("%s <directory with MP3 files> <feed title> <URL to directory with MP3 files> [optional image url]\n" % sys.argv[0], file=sys.stderr)
    print("Example:", file=sys.stderr)
    print("%s /data/public/yoga-sessions-2017/ 'My Yoga Podcast 2017' https://example.com/yoga-sessions-2017/'\n" % sys.argv[0], file=sys.stderr)
    print("This creates the ATOM feed XML file '/data/public/yoga-sessions-2017/podcast.xml' which contains all mp3 files from the directory /data/public/yoga-sessions-2017 with their medadata.", file=sys.stderr)
    print("If those mp3 files are also available via https://example.com/yoga-sessions-2017/ you can play them with your favourite podcast player using the created ATOM feed file.\n", file=sys.stderr)
    sys.exit(1)


DIR = sys.argv[1]
FEEDTITLE = sys.argv[2]
URLBASE = sys.argv[3]
try:
    IMAGE=sys.argv[4]
except:
    IMAGE=None

LINK = URLBASE+"/podcast.xml";
NOW=datetime.now(timezone.utc).strftime("%a, %d %b %Y %T %z")


root = Element('rss', attrib={
    'version': '2.0',
    'xmlns:itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd',
    'xmlns:atom': 'http://www.w3.org/2005/Atom'
})

channel = SubElement(root,"channel")
channel.append(Element('link', text=LINK))
channel.append(Element('atom:link', attrib={
    'href': LINK+'/podcast.xml',
    'rel': 'self',
    'type': 'application/rss+xml'
}))
channel.append(Element('language', text='de'))
channel.append(Element('pubDate', text=NOW))
channel.append(Element('title', text=FEEDTITLE))
channel.append(Element('description', text=FEEDTITLE))
channel.append(Element('itunes:summary', text=FEEDTITLE))
if IMAGE is not None:
    image = SubElement(channel,"image")
    image.append(Element('url', text=IMAGE))



mediafiles = []
for filename in listdir(DIR):
    if not filename.lower().endswith(".mp3"):
        continue

    filepath = path.join(DIR,filename)
    fileinfo = {}

    print("FILEPATH "+filepath)

    fileinfo['name']=filename
    fileinfo['mtime']=datetime.fromtimestamp(stat(filepath).st_mtime)
    fileinfo['mdatetime']=datetime.fromtimestamp(stat(filepath).st_mtime,timezone.utc).strftime("%a, %d %b %Y %T %z")
    fileinfo['size']=stat(filepath).st_size
    fileinfo['url']=URLBASE+"/"+urllib.parse.quote(filename)
    fileinfo['guid']=md5(filename.encode()).hexdigest()

    # Read ID3 tags
    try:
        id3 = ID3(filepath)
    except ID3NoHeaderError:
        print("ERROR: %s has no ID3 tag, skipping" % filename, file=sys.stderr)
        continue

    tags = {
        'TRSN': None, 'TPE1': None, 'TALB': None, 'TRCK': None,
        'TIT2': None, 'COMM': None, 'TYER': None, 'TDAT': None,
        'TIME': None, 'TLEN': None 
    }


    # FIXME
    print(id3['COMM::XXX'])
    sys.exit(0)


    for t in tags:
        if t in id3.keys():
           tags[t] = id3[t].text[0]
#           tags[t] = id3[t][0]


    print(tags)
    sys.exit(0)

    fileinfo['desc']=tags['COMM']
    fileinfo['title']=tags['TIT2']
    fileinfo['duration']=tags['TLEN']
#    fileinfo['itunes-duration']=time.strftime("%H:%M:%S",time.gmtime(int(tags['TLEN']/1000)))

    mediafiles.append(fileinfo)

    print(fileinfo)
    sys.exit(0)

print(mediafiles)
sys.exit(0)

for mediafile in sorted(mediafiles, key=lambda x: x['mtime'], reverse=True):
    item = SubElement(channel, "item")
    item.append(Element('title', text=mediafile['title']))
    item.append(Element('description', text=mediafile['desc']))
    item.append(Element('itunes:summary', text=mediafile['desc']))
    item.append(Element('enclosure', attrib={
        'url': mediafile['url'],
        'type': "audio/mpeg",
        'length': mediafile['size']
    }))
    item.append(Element('guid', text=mediafile['guid']))
    item.append(Element('pubDate', text=mediafile['mdatetime']))
#    item.append(Element('itunes:duration', text=mediainfo['itunes-duration']))

print(tostring(root, encoding='utf8', method='xml').decode())
#ElementTree(root).write("test.xml",encoding="utf-8", xml_declaration=True)
