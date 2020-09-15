#!/usr/bin/env python3

import sys
from os import stat, listdir, path
from xml.etree.ElementTree import Element, SubElement, tostring
import time
from datetime import datetime, timezone
import urllib.parse
from hashlib import md5
import mutagen
from mutagen.id3 import ID3,ID3NoHeaderError
#import xml.dom.minidom

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
    IMAGE = sys.argv[4]
except:
    IMAGE = None

NOW = datetime.now(timezone.utc).astimezone().strftime("%a, %d %b %Y %T %z")

mediafiles = []
for filename in listdir(DIR):
    if not filename.lower().endswith(".mp3"):
        continue

    filepath = path.join(DIR,filename)
    fileinfo = {}

    fileinfo['name'] = filename
    fileinfo['pubdate'] = datetime.fromtimestamp(stat(filepath).st_mtime,timezone.utc).astimezone()
    fileinfo['size'] = stat(filepath).st_size
    fileinfo['url'] = URLBASE+"/"+urllib.parse.quote(filename)
    fileinfo['guid'] = md5(filename.encode()).hexdigest()
    fileinfo['duration'] = mutagen.File(filepath).info.length	# duration in seconds
    fileinfo['chapters'] = []

    # Read ID3 tags
    try:
        id3 = ID3(filepath)
    except ID3NoHeaderError:
        print("ERROR: %s has no ID3 tag, skipping" % filename, file=sys.stderr)
        continue

    tags = {
        'TPE1': None, 'TALB': None, 'TRCK': None,
        'TIT2': None, 'COMM': None,
        'TYER': None, 'TDAT': None, 'TIME': None, 
        'TDRC': None, 'TDRL': None, 'TDOR': None,
        'TLEN': None,
    }

    for t in tags:
       try:
           tags[t] = id3.getall(t)[0].text[0]
       except:
           tags[t] = None

    # map ID3 tags to feed items
    fileinfo['desc'] = tags['COMM']
    fileinfo['title'] = tags['TIT2']

    # handling for TLEN
    if tags['TLEN']:
        fileinfo['duration'] = round(int(tags['TLEN'])/1000)

    # handling for Chapter tag
    for cFrame in id3.getall('CHAP'):
        chapter = {}
        chapter['title'] = cFrame.sub_frames.getall('TIT2')[0].text[0] or cFrame.element_id
        chapter['start'] = round(int(int(cFrame.start_time)/1000))	# start time in seconds
        fileinfo['chapters'].append(chapter)

    # handling for publishing date (ID3v2.3: TYER,TDAT,TIME ID3v2.4: TRDC/TDRL)
    dt = datetime.fromtimestamp(0,timezone.utc).astimezone()
    if tags['TYER']:
        dt = dt.replace(year=tags['TYER'])
    if tags['TDAT']:
        dt = dt.replace(day=tags['TDAT'][0:2],month=tags['TDAT'][2:4])
    if tags['TIME']:
        d = dt.replace(hour=tags['TIME'][0:2],minute=tags['TIME'][2:4])

    for x in 'TDRC','TDRL','TDOR':
        try:
            if tags[x]:
                dt=dt.replace(year=tags[x].year, month=tags[x].month, day=tags[x].day, hour=tags[x].hour, minute=tags[x].minute, second=tags[x].second)
                break;
        except:
            continue

    if dt != datetime.fromtimestamp(0,timezone.utc).astimezone():
        fileinfo['pubdate'] = dt


    mediafiles.append(fileinfo)


root = Element('rss', attrib={
    'version': '2.0',
    'xmlns:itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd',
    'xmlns:atom': 'http://www.w3.org/2005/Atom',
})

channel = SubElement(root,"channel")

SubElement(channel,'link').text = URLBASE+"/podcast.xml"
SubElement(channel,'atom:link', attrib={
    'href': URLBASE+"/podcast.xml",
    'rel': 'self',
    'type': 'application/rss+xml'
})
SubElement(channel,"language").text = "de"
SubElement(channel,'pubDate').text = NOW
SubElement(channel,'title').text = FEEDTITLE
SubElement(channel,'description').text = FEEDTITLE
SubElement(channel,'itunes:summary').text = FEEDTITLE
SubElement(channel,'itunes:category', attrib={'text':'Music'})
SubElement(channel,'itunes:explicit').text = 'no'

if IMAGE is not None:
    image = SubElement(channel, "itunes:image", attrib={'href': IMAGE})


for mediafile in sorted(mediafiles,key=lambda x: x['pubdate'].timestamp(), reverse=True):
    item = SubElement(channel, "item")
    SubElement(item,'title').text = mediafile['title']
    SubElement(item,'description').text = mediafile['desc']
    SubElement(item,'itunes:summary').text = mediafile['desc']
    SubElement(item,'enclosure', attrib={
        'url': mediafile['url'],
        'type': 'audio/mpeg',
        'length': str(mediafile['size'])
    })
    SubElement(item,'guid', attrib={'isPermaLink':'false'}).text = mediafile['guid']
    SubElement(item,'pubDate').text = mediafile['pubdate'].strftime("%a, %d %b %Y %T %z")
    SubElement(item,'itunes:duration').text = time.strftime("%H:%M:%S", time.gmtime(int(fileinfo['duration'])))

    chapters = SubElement(item,'psc:chapters', attrib={ 'version': "1.2", 'xmlns:psc': 'http://podlove.org/simple-chapters' })
    for chapter in sorted(mediafile['chapters'], key=lambda x: x['start']):
        SubElement(chapters, 'psc:chapter', attrib={
            'start': time.strftime("%H:%M:%S",time.gmtime(chapter['start'])),
            'title': chapter['title'] })

file = open(path.join(DIR, 'podcast.xml'),"w")

file.write(tostring(root, encoding='UTF-8', method='xml').decode())	# xml in single line
#file.write(xml.dom.minidom.parseString(tostring(root, encoding='UTF-8', method='xml').decode()).toprettyxml())	# pretty-print, requires xml.dom.minidom
