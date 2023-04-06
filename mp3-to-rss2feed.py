#!/usr/bin/env python3

import sys
from os import stat, listdir, path
from xml.etree.ElementTree import Element, SubElement, tostring
import time
from datetime import datetime, timezone, timedelta
from dateutil import parser
import urllib.parse
from hashlib import md5
import mutagen
from mutagen.id3 import ID3,ID3NoHeaderError
from mutagen.oggopus import OggOpus,OggOpusHeaderError
import re

#import xml.dom.minidom

class Fileinfo:
  def __init__(self, filepath):
    filename = path.basename(filepath)

    self.title = path.splitext(filename)[0]
    self.author = None
    self.desc = None
    self.duration = mutagen.File(filepath).info.length	# duration in seconds
    self.chapters = []
    self.pubdate = datetime.fromtimestamp(stat(filepath).st_mtime,timezone.utc).astimezone()
    self.link = None
    self.size = stat(filepath).st_size
    self.url = URLBASE + "/" + urllib.parse.quote(filename)
    self.guid = md5(filename.encode()).hexdigest()
    self.mimetype = None

class FileinfoOpus(Fileinfo):
  def __init__(self, filepath):
    super().__init__(filepath)
    self.mimetype = 'audio/opus'
    try:
      meta = OggOpus(filepath).tags

      # simple best effort mapping
      tag_mappings = {
        'title': ['title'],
        'author': ['artist', 'performer'],
        'desc': ['comment', 'desc', 'lyrics']
      }
      for attr in tag_mappings:
        for tag in tag_mappings[attr]:
          try:
            setattr(self, attr, " - ".join(meta[tag]))
            break
          except KeyError:
            pass

      # chapters
      for key in meta.keys():
        chapterMatch = re.match('^(chapter\d+)$', key)
        if chapterMatch:
          chapterKey = chapterMatch.group(1)
          chapter = {}
          startMatch = re.match('^(\d{1,2}):(\d{1,2}):(\d{1,2})', meta[chapterKey][0])
          if startMatch:
            chapter = {}
            chapter['start'] = int(timedelta(hours=int(startMatch.group(1)), minutes=int(startMatch.group(2)), seconds = int(startMatch.group(3))).total_seconds())
            try:
              chapter['title'] = meta[chapterKey + "name"][0]
            except KeyError:
              chapter['title'] = chapterKey
            self.chapters.append(chapter)

      # pubdate
      try:
        self.pubdate = parser.isoparse(meta['date'][0])
      except (KeyError, ValueError):
        pass

    except OggOpusHeaderError:
      print("WARNING: %s has no OggOpus header, skipping" % filename, file=sys.stderr)
      pass

class FileinfoMp3(Fileinfo):
  def __init__(self, filepath):
    super().__init__(filepath)
    self.mimetype = 'audio/mpeg'
    try:
      ### read ID3 tag
      id3 = ID3(filepath)

      tagFields = {
        'TIT2': None,
        'TPE1': None, 'TPE2': None,
        'COMM': None,
        'TYER': None, 'TDAT': None, 'TIME': None, 
        'TDRC': None, 'TDRL': None, 'TDOR': None,
        'TLEN': None,
        'WOAS': None, 'WORS': None,
      }

      for field in tagFields:
        try:
          tagFields[field] = id3.getall(field)[0].text[0]
        except AttributeError:
          tagFields[field] = str(id3.getall(field)[0])
        except:
          tagFields[field] = None


      ### update fileinfo with info from ID3 frames
      # title
      if tagFields['TIT2']:
        self.title = tagFields['TIT2']

      # artist/author
      if tagFields['TPE1']:
        self.author = tagFields['TPE1']
      elif tagFields['TPE2']:
        self.author = tagFields['TPE2']

      # desc
      if tagFields['COMM']:
        self.desc = tagFields['COMM']

      # duration
      if tagFields['TLEN']:
        self.duration = round(int(tagFields['TLEN'])/1000)

      # chapters
      for cFrame in id3.getall('CHAP'):
        chapter = {}
        try:
          chapter['title'] = cFrame.sub_frames.getall('TIT2')[0].text[0]
        except IndexError:
          chapter['title'] = cFrame.element_id
          chapter['start'] = round(int(int(cFrame.start_time)/1000))	# start time in seconds
          self.chapters.append(chapter)

      # pubdate (ID3v2.3: TYER,TDAT,TIME ID3v2.4: TRDC/TDRL - start with 1.1.1970 and modify it with the availble frames)
      dt = datetime.fromtimestamp(0,timezone.utc).astimezone()
      if tagFields['TYER']:
        dt = dt.replace(year=tagFields['TYER'])
      if tagFields['TDAT']:
        dt = dt.replace(day=tagFields['TDAT'][0:2],month=tagFields['TDAT'][2:4])
      if tagFields['TIME']:
        dt = dt.replace(hour=tagFields['TIME'][0:2],minute=tagFields['TIME'][2:4])

      for x in 'TDRC','TDRL','TDOR':
        try:
          if tagFields[x]:
            dt=dt.replace(year=tagFields[x].year, month=tagFields[x].month, day=tagFields[x].day, hour=tagFields[x].hour, minute=tagFields[x].minute, second=tagFields[x].second)
            break;
        except:
          continue

      if dt != datetime.fromtimestamp(0,timezone.utc).astimezone():
        self.pubdate = dt

      # link
      if tagFields['WOAS']:
        self.link = tagFields['WOAS']
      elif tagFields['WORS']:
        self.link = tagFields['WORS']

    except ID3NoHeaderError:
      #print("WARNING: %s has no ID3 tag, skipping" % filename, file=sys.stderr)
      pass



if len(sys.argv) < 4 or len(sys.argv) > 5:
  print("Usage:", file=sys.stderr)
  print("%s <directory with MP3 files> <feed title> <URL to directory with MP3 files> [optional image url]\n" % sys.argv[0], file=sys.stderr)
  print("Example:", file=sys.stderr)
  print("%s /data/public/yoga-sessions-2017/ 'My Yoga Podcast 2017' https://example.com/yoga-sessions-2017/'\n" % sys.argv[0], file=sys.stderr)
  print("This creates the RSS2 feed XML file '/data/public/yoga-sessions-2017/podcast.xml' which contains all mp3 files from the directory /data/public/yoga-sessions-2017 with their medadata.", file=sys.stderr)
  print("If those mp3 files are also available via https://example.com/yoga-sessions-2017/ you can play them with your favourite podcast player using the created RSS2 feed file.\n", file=sys.stderr)
  sys.exit(1)


DIR = sys.argv[1]
FEEDTITLE = sys.argv[2]
URLBASE = sys.argv[3]
try:
  IMAGE = sys.argv[4]
except:
  IMAGE = None

mediafiles = []
for filename in listdir(DIR):
  filepath = path.join(DIR,filename)
  fileextension = path.splitext(filename)[1].lower()

  if fileextension == ".mp3":
    mediafiles.append(FileinfoMp3(filepath))
  elif fileextension == ".opus":
    mediafiles.append(FileinfoOpus(filepath))


### create feed
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
SubElement(channel,'lastBuildDate').text = datetime.now(timezone.utc).astimezone().strftime("%a, %d %b %Y %T %z")
SubElement(channel,'generator').text = "https://github.com/citronalco/mp3-to-rss2feed"
SubElement(channel,'title').text = FEEDTITLE
SubElement(channel,'description').text = FEEDTITLE
SubElement(channel,'itunes:summary').text = FEEDTITLE
SubElement(channel,'itunes:category', attrib={'text':'Music'})
SubElement(channel,'itunes:explicit').text = 'no'

if IMAGE is not None:
  SubElement(channel, "itunes:image", attrib={'href': IMAGE})
  image = SubElement(channel, "image")
  SubElement(image,'url').text = IMAGE
  SubElement(image,'title').text = FEEDTITLE
  SubElement(image,'link')


for fileinfo in sorted(mediafiles,key=lambda x: x.pubdate.timestamp(), reverse=True):
  item = SubElement(channel, "item")
  SubElement(item,'title').text = fileinfo.title
  SubElement(item,'author').text = fileinfo.author
  SubElement(item,'link').text = fileinfo.link
  SubElement(item,'description').text = fileinfo.desc
  SubElement(item,'itunes:summary').text = fileinfo.desc
  SubElement(item,'enclosure', attrib={
    'url': fileinfo.url,
    'type': fileinfo.mimetype,
    'length': str(fileinfo.size)
  })
  SubElement(item,'guid', attrib={'isPermaLink':'false'}).text = fileinfo.guid
  SubElement(item,'pubDate').text = fileinfo.pubdate.strftime("%a, %d %b %Y %T %z")
  SubElement(item,'itunes:duration').text = time.strftime("%H:%M:%S", time.gmtime(int(fileinfo.duration)))

  chapters = SubElement(item,'psc:chapters', attrib={ 'version': "1.2", 'xmlns:psc': 'http://podlove.org/simple-chapters' })
  for chapter in sorted(fileinfo.chapters, key=lambda x: x['start']):
    SubElement(chapters, 'psc:chapter', attrib={
      'start': time.strftime("%H:%M:%S",time.gmtime(chapter['start'])),
      'title': chapter['title']
    })


### save feed
file = open(path.join(DIR, 'podcast.xml'),"w")

file.write(tostring(root, encoding='UTF-8', method='xml').decode())	# xml in single line
#file.write(xml.dom.minidom.parseString(tostring(root, encoding='UTF-8', method='xml').decode()).toprettyxml())	# pretty-print, requires xml.dom.minidom
