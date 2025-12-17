# MP3-to-RSS2 Feed

Python 3 script to create a RSS2 feed for all MP3 files in a directory, suitable for all podcast players.

### Requirements
Python 3 with modules "mutagen" and "urllib3"
(On Debian/Ubuntu/Mint: `sudo apt install python3 python3-mutagen python3-urllib3`) 

### Usage
```
usage: mp3-to-rss2feed.py [-h] [-p] directory title url [imageUrl]

Create a RSS 2.0 compliant podcast feed from MP3 files in a directory

positional arguments:
  directory      Directory containing the mp3 files
  title          Title of your feed/podcast
  url            URL to the directory containing the mp3 files
  imageUrl       URL to an image for your feed/podcast (Optional)

options:
  -h, --help     show this help message and exit
  -p, --private  Marks the feed as private (default: False)

Example:
    mp3-to-rss2feed.py /data/public/yoga-sessions-2025/ 'My Yoga Podcast 2025' https://example.com/yoga-sessions-2025/

    This creates the RSS2 feed XML file '/data/public/yoga-sessions-2017/podcast.xml' which contains all mp3 files from the directory /data/public/yoga-sessions-2017 with their medadata.
    If those mp3 files are also available via https://example.com/yoga-sessions-2017/ you can play them with your favourite podcast player using the created RSS2 feed file.
```

The script examines all MP3 files in the given directory and reads their ID3 tags.
With the retrieved information this script builds a RSS2 podcast feed with your desired feed title, and saves it as `<directory-with-mp3-files>/podcast.xml`.

Optional: If an image URL is given, it will be used as the feed's cover image.

`--private` prevents the entire podcast from appearing on the iTunes Store podcast directory (and hopefully other aggregators)

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
