# MP3-to-RSS2 Feed

Python 3 script to create a RSS2 feed for all MP3 files in a given directory, suitable for the usual podcast players.

### Requirements
Python 3 with modules "mutagen" and "urllib3"
(On Debian/Ubuntu/Mint: `sudo apt install python3 python3-mutagen python3-urllib3`) 

### Usage
```./mp3-to-rss2feed.py <mp3 files directory> <feed title> <mp3 files url> [image url]```

The script saves the feed file as "podcast.xml" in the MP3 files' directory.
"podcast.xml" contains all MP3 files from the MP3 files' directory, sorted from newest to oldest.
Titles, descriptions and chapters etc. required to build the RSS2 feed are read from the MP3 files' ID3 tags.

If an image URL is given, this will be used as the feed's cover image.

### Example ###
Your MP3 files are in directory "/data/mp3files/" and accessible via "https://example.net/podcast/".
Now you want to have a nice RSS2 feed for it, to be able to subscribe and listen to them with your favourite podcast client:

```./mp3-to-rss2feed.py "/data/mp3files/" "My Podcast" "https://example.net/mypodcast/" https://example.net/images/podcast.jpg```

Now you can subscribe in your podcast player to: https://example.net/mypodcast/podcast.xml
