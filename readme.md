# SRT Notes

Time based note taking that exports notes as SRT file for integrating into video editing software.

Time will be taken from system clock, in edit the relative positions will be more important than the exact times.

## Script Help

	$ ./srt-notes.py -h
	usage: srt-notes [-h] [-s SRT] [-t] ...

	Note taking tool for video editing output

	positional arguments:
	message

	options:
	-h, --help         show this help message and exit
	-s SRT, --srt SRT  SRT file for converted data
	-t, --text         Return text from SRT file


## Roadmap


### Web
A multithreaded web interface that can both read and write to the SRT. The goal being to embed the web interface in OBS and have it emmit sound onto a secondary audio track when another web client adds a new time to the SRT. Should also allow submitting no text to trigger sound and then editing text content later. This allows for critcal timing to be maintained and adding context later.
