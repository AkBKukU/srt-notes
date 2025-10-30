#!/usr/bin/env python3

# Python System
import argparse
import datetime
import sys
import os
import json
from pprint import pprint

class SRT(object):
    """Class to add time based notes as SRT

    """

    def __init__(self,filename=None):
        """Constructor to setup basic data and config defaults

        """
        self.titles=[]
        self.filename=filename
        if self.filename is not None:
            self.load()

    def load(self,filename=None):
        self.titles=[]

        if filename is None:
            if self.filename is not None:
                filename = self.filename
            else:
                print("Must provide SRT file to load")
                sys.exit(1)

        if os.path.exists(filename):
            with open(filename, newline='') as srtfile:
                title=""
                for line in srtfile:
                    if title != "":
                        title+=line

                    if "-->" in line:
                        title+=line

                    if line == "\n" and title != "":
                        self.titles.append(Title(string=title))
                        title=""


    def save(self,filename=None):

        if filename is None:
            if self.filename is not None:
                filename = self.filename
            else:
                print("Must provide SRT file to save")
                os.exit(1)

        i=1
        with open(filename, 'w', encoding="utf-8") as output:
            for title in self.titles:
                output.write(str(i)+"\n")
                output.write(title.toString())
                output.write("\n")
                i+=1



    def add(self,start=None,end=None,text=""):
        time = datetime.datetime.now()
        if start is None:
            start = time
        if end is None:
            end = time + datetime.timedelta(0,30)

        self.titles.append(Title(start=start,end=end,text=text))

    def debug(self):
        for title in self.titles:
            print(title.toString())

    def getText(self):
        for title in self.titles:
            print(title.text)

class Title(object):
    def __init__(self,start=None,end=None,text="",string=None):
        self.start=start
        self.end=end
        self.text=text
        if string is not None:
            self.fromString(string)

    def srtToDatetime(srt_time):
        return datetime.datetime.strptime(srt_time,"%H:%M:%S,%f")

    def datetimeToSrt(dt):
        return str(dt.time()).replace(".",",")[:12]

    def toString(self):
        return f'{Title.datetimeToSrt(self.start)} --> {Title.datetimeToSrt(self.end)}\n{self.text}'

    def fromString(self,string):
        self.start=None
        self.end=None
        self.text=""

        lines=string.split("\n")
        for line in lines:
            if self.start is not None:
                if line != "":
                    self.text+=line+"\n"
            if "-->" in line:
                start, end = line.split(" --> ")
                self.start=Title.srtToDatetime(start)
                self.end=Title.srtToDatetime(end)


def main():
    """ Execute as a CLI and process parameters

    """
    # Setup CLI arguments
    parser = argparse.ArgumentParser(
                    prog="srt-notes",
                    description='Note taking tool for video editing output',
                    epilog='')
    parser.add_argument('-s', '--srt', help="SRT file for converted data", default=f"{str(datetime.datetime.now().date())}.srt")
    parser.add_argument('-t', '--text', help="Return text from SRT file", action='store_true')
    parser.add_argument('message', help="", default=None, nargs=argparse.REMAINDER)
    args = parser.parse_args()

    srt = SRT(args.srt)

    if args.text:
        srt.getText()
        sys.exit(0)


    if args.message is not None:
        srt.add(text="\n".join(args.message))

    #srt.debug()
    srt.save()

if __name__ == "__main__":
    main()
