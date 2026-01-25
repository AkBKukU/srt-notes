 
# Python System
import argparse
import datetime
import sys
import os
import json
from pprint import pprint
import asyncio
import signal
from multiprocessing import Process

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
            output.write("\n")



    def add(self,start=None,end=None,text=""):
        time = datetime.datetime.now()
        if start is None:
            start = time
        if end is None:
            end = time + datetime.timedelta(0,30)

        self.titles.append(Title(start=start,end=end,text=text))


    def update(self,start=None,text=""):
        for title in self.titles:
            if title.start == start:
                title.text = text


    def remove(self,start=None):
        pprint(self.titles)
        for i in range(len(self.titles)):
            print("matching: "+str(i))
            print("matching: "+str(start)+" - "+str(self.titles[i].start))
            if self.titles[i].start == start:
                self.titles.pop(i)
                return


    def debug(self):
        for title in self.titles:
            print(title.toString())


    def getText(self):
        for title in self.titles:
            print(title.text)


    def getTitles(self):
        return self.titles


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
        return f'{Title.datetimeToSrt(self.start)} --> {Title.datetimeToSrt(self.end)}\n{self.text}\n'

    def toJson(self):
        return {
            "start": Title.datetimeToSrt(self.start),
            "end": Title.datetimeToSrt(self.end),
            "text": self.text
            }

    def fromJson(self,data):
        self.start=Title.srtToDatetime(data["start"])
        self.end=Title.srtToDatetime(data["end"])
        self.text=data["text"]

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

        self.text=self.text[:-1]
