#!/usr/bin/perl

use strict;
use warnings;
use File::Find::Rule;
use MP3::Info;
use MP3::Tag;
use URI::Escape;
use POSIX;
use XML::Writer;
use utf8;
use Unicode::String qw(utf8 latin1);
use Digest::MD5;
use File::Basename;

if (@ARGV lt 3 or @ARGV gt 4) {
    print "USAGE:\n";
    print $0." <directory with MP3 files> <feed title> <URL to directory with MP3 files> [optional image url]\n\n";
    print "Example:\n";
    print $0.' /data/public/yoga-sessions-2017/ "My Yoga Podcast 2017" https://example.com/yoga-sessions-2017/'."\n\n";
    print 'This creates the ATOM feed XML file "/data/public/yoga-sessions-2017/podcast.xml" which contains all mp3 files from the directory /data/public/yoga-sessions-2017 with their medadata.\n';
    print 'If those mp3 files are also available via https://example.com/yoga-sessions-2017/ you can play them with your favourite podcast player using the created ATOM feed file.'."\n\n";
    exit;
}

my $DIR=$ARGV[0];
my $FEEDTITLE=$ARGV[1];
my $URLBASE=$ARGV[2];

my $LINK=$URLBASE."/podcast.xml";
my $NOW=POSIX::strftime("%a, %d %b %Y %T %z",localtime);

open my $RSS, '>', $DIR."/podcast.xml" or die($!);
my $xml=XML::Writer->new(OUTPUT=>$RSS,DATA_MODE=>1,DATA_INDENT=>1);

$xml->xmlDecl('utf-8');
$xml->startTag('rss','version'=>'2.0','xmlns:itunes'=>"http://www.itunes.com/dtds/podcast-1.0.dtd",'xmlns:atom'=>"http://www.w3.org/2005/Atom");
$xml->startTag('channel');
$xml->dataElement('link'=>$URLBASE);
$xml->emptyTag('atom:link', 'href'=>$LINK, 'rel'=>'self', 'type'=>'application/rss+xml');
$xml->dataElement('language'=>'de');
$xml->dataElement('pubDate'=>$NOW);
$xml->dataElement('title'=>$FEEDTITLE);
$xml->dataElement('description'=>$FEEDTITLE);
$xml->dataElement('itunes:summary'=>$FEEDTITLE);

# optional cover image
if ($ARGV[3]) {
    $xml->startTag('image');
    $xml->dataElement('url'=>$ARGV[3]);
    $xml->endTag('image');
}

my @files;
foreach (File::Find::Rule->file()->name('*.mp3')->in($DIR)) {
    my %fileinfo;
    $fileinfo{'name'}=$_;
    $fileinfo{'mtime'}=(stat($fileinfo{'name'}))[10] or die($!);
    $fileinfo{'mdatetime'}=POSIX::strftime("%a, %d %b %Y %T %z",localtime((stat($fileinfo{'name'}))[10]));
    $fileinfo{'size'}=(stat($fileinfo{'name'}))[7] or die($!);
    $fileinfo{'url'}=$URLBASE."/".uri_escape(File::Spec->abs2rel($fileinfo{'name'},$DIR));
    $fileinfo{'guid'}=Digest::MD5::md5_hex(basename($fileinfo{'name'}));
    my $mp3=MP3::Tag->new($fileinfo{'name'}) or die($!);
    $mp3->get_tags;
    $fileinfo{'desc'}=latin1($mp3->comment())->utf8;
    $fileinfo{'title'}=latin1($mp3->title())->utf8;
    $fileinfo{'duration'}=$mp3->total_millisecs_int();
    $fileinfo{'itunes-duration'}=POSIX::strftime("%H:%M:%S",gmtime(int($mp3->total_millisecs_int()/1000)));
    push(@files,\%fileinfo);
}

foreach my $file (reverse(sort { $a->{'mtime'} cmp $b->{'mtime'} } @files )) {
    $xml->startTag('item');
    $xml->dataElement('title'=>$file->{'title'});
    $xml->dataElement('description'=>$file->{'desc'});
    $xml->dataElement('itunes:summary'=>$file->{'desc'});
    $xml->emptyTag('enclosure','url'=>$file->{'url'}, 'type'=>'audio/mpeg', 'length'=>$file->{'size'});
    $xml->dataElement('guid'=>$file->{'guid'});
    $xml->dataElement('pubDate'=>$file->{'mdatetime'});
    $xml->dataElement('itunes:duration'=>$file->{'itunes-duration'});
    $xml->endTag('item');
}
$xml->endTag('channel');
$xml->endTag('rss');

close $RSS;
