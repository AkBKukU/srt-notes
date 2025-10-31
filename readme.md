# SRT Notes

Time based note taking that exports notes as SRT file for integrating into video editing software.

Time will be taken from system clock, in edit the relative positions will be more important than the exact times.

## Script Help

	$ ./srt-notes.py -h
	usage: srt-notes [-h] [-s SRT] [-t] [-w] [-i IP] [-p PORT] ...

	Note taking tool for video editing output

	positional arguments:
	message

	options:
	-h, --help       show this help message and exit
	-s, --srt SRT    SRT file for converted data
	-t, --text       Return text from SRT file
	-w, --web        Start web server
	-i, --ip IP      Web server listening IP
	-p, --port PORT  Web server listening IP



## Web
A multithreaded web interface that can both read and write to the SRT. You can embed the web interface in OBS and have it emmit sound onto a secondary audio track when another web client adds a new time to the SRT. Existing entries can also be edited after submission to add additional lines or to submit time critical blank entries and add a description later.
