# MP3-to-RSS2 Feed

Python 3 script to create a RSS2 feed for all MP3 files in a directory, suitable for all podcast players.

### Requirements
Python 3 with modules "mutagen" and "urllib3"
(On Debian/Ubuntu/Mint: `sudo apt install python3 python3-mutagen python3-urllib3`) 

### Usage
```./mp3-to-rss2feed.py <directory-with-mp3-files> <title-of-your-feed> <URL-to-mp3-files> [image-URL]```

The script examines all MP3 files in the <mp3 files directory> and reads their ID3 tags.
With the retrieved information the script builds a RSS2 podcast feed with your desired feed title, and saves it as `<directory-with-mp3-files>/podcast.xml`.

Optional: If an image URL is given, it will be used as the feed's cover image.

### Example ###
Your MP3 files are in directory "/data/mp3files/" and accessible via "https://example.net/mypodcast/".
You want to have a nice RSS2 feed for them, to be able to subscribe and listen to them with your favourite podcast client:

```./mp3-to-rss2feed.py "/data/mp3files/" "My Podcast" "https://example.net/mypodcast/" https://example.net/images/mypodcast.jpg```

Now you can subscribe in your podcast player to: https://example.net/mypodcast/podcast.xml

### Supported ID3 Tag frames
The script can make use of this frames:
- TIT2 (Title)
- COMM (Description)
- TLEN (Duration)
- CHAP (Chapters)
- TYER, TDAT, TIME, TRDC, TDRL (Publication Date)
- WOAS, WORS (Link)
