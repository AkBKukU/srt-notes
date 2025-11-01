#!/usr/bin/env python3

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

class WebInterface(object):
    try:
        # External Modules
        from flask import Flask
        from flask import Response
        from flask import request
        from flask import send_file
        from flask import redirect
        from flask import make_response
        from flask import send_from_directory
    except Exception as e:
            print("Need to install Python module [flask]")
            sys.exit(1)
    """Web interface for managing rips

    """

    def __init__(self,ip,port,srt):

        self.host_dir=os.path.realpath(__file__).replace(os.path.basename(__file__),"")
        self.app = self.Flask("SRT Notes")
        self.app.logger.disabled = True
        #log = logging.getLogger('werkzeug')
        #log.disabled = True

        # Static content
        self.app.static_folder=self.host_dir+"http/static"
        self.app.static_url_path='/static/'

        # Define routes in class to use with flask
        self.app.add_url_rule('/','home', self.index)
        # Define routes in class to use with flask
        self.app.add_url_rule('/add','add_title', self.add_title,methods=["POST"])
        self.app.add_url_rule('/update','update_title', self.update_title,methods=["POST"])
        self.app.add_url_rule('/remove','remove_title', self.remove_title,methods=["POST"])
        self.app.add_url_rule('/srt.json','json', self.json)


        self.host = ip
        self.port = port
        self.srt = srt



    async def start(self):
        """ Run Flask in a process thread that is non-blocking """
        print("Starting Flask")
        self.web_thread = Process(target=self.app.run,
            kwargs={
                "host":self.host,
                "port":self.port,
                "debug":True,
                "use_reloader":False
                }
            )
        self.web_thread.start()

    def stop(self):
        """ Send SIGKILL and join thread to end Flask server """
        if hasattr(self, "web_thread") and self.web_thread is not None:
            self.web_thread.terminate()
            self.web_thread.join()
        if hasattr(self, "rip_thread"):
            self.rip_thread.terminate()
            self.rip_thread.join()


    def index(self):
        """ Simple class function to send HTML to browser """
        return f"""<!DOCTYPE html>
<html>
<head>
	<title> SRT Notes: {self.srt} </title>
	<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
	<meta name="HandheldFriendly" content="true" />
	<style>
body,html {{
	font-family: sans-serif;
	color: #ddd;
	background-color: #111;
}}
h1 {{
	color: #ddd;
	margin: 0px;
}}
h5 {{
	color: #ddd;
	margin: 0px;
	margin-top: 1em;
}}
.wide {{
    display: block;
	width: 100%;
}}
input[type="button"]  {{
	background-color: #444;
    box-sizing: border-box;
	color: #fff;
	border-top: solid 2px #555;
	border-bottom: solid 2px #333;
	border-right: solid 2px #353535;
	border-left: solid 2px #454545;
}}
input[type="button"]:active  {{
	background-color: #464;
    box-sizing: border-box;
	color: #fff;
	border-top: solid 2px #333;
	border-bottom: solid 2px #555;
	border-right: solid 2px #353535;
	border-left: solid 2px #454545;
}}
input[type="text"] {{
	background-color: #222;
    box-sizing: border-box;
	color: #fff;
	border: none;
}}
textarea {{
	background-color: #333;
    box-sizing: border-box;
	border: none;
	color: #fff;
	resize: vertical;
}}
a,
a:link,
a:visited
{{
	color: #bbf; text-decoration: none;
}}
a.remove
{{
	color: #522; text-decoration: none;
}}
	</style>
</head>
<body>
<h1>{self.srt}</h1>

<input type="text" class="wide" id="text" name="text" placeholder="Add note details here...">
<input class="wide" type="button" id="new_title" value="add" />

<div id=titles>

</div>
<a href="?alarm=1">Sound View</a>

<script type="text/javascript" src="/static/update.js"> </script>
</body>
</html>
"""


    def add_title(self):
        srt = SRT(self.srt)
        data = self.request.get_json()
        pprint(data)
        srt.add(text=data["text"])
        srt.save()
        return "sure"

    def update_title(self):
        srt = SRT(self.srt)
        data = self.request.get_json()
        pprint(data)
        start=Title.srtToDatetime(data['start'])
        srt.update(start=start,text=data["text"])
        srt.save()
        return "sure"

    def remove_title(self):
        srt = SRT(self.srt)
        data = self.request.get_json()
        pprint(data)
        start=Title.srtToDatetime(data['start'])
        srt.remove(start=start)
        srt.save()
        return "sure"

    def json(self):
        """ Simple class function to send HTML to browser """
        srt = SRT(self.srt)
        data=[]
        for title in srt.getTitles():
            data.append(title.toJson())
        return self.Response(json.dumps(data), mimetype='application/json')


# ------ Async Server Handler ------

global loop_state
global server
loop_state = True
server = None


async def asyncLoop():
    """ Blocking main loop to provide time for async tasks to run"""
    print('Blocking main loop')
    global loop_state
    while loop_state:
        await asyncio.sleep(1)


def exit_handler(sig, frame):
    """ Handle CTRL-C to gracefully end program and API connections """
    global loop_state
    print('You pressed Ctrl+C!')
    loop_state = False
    server.stop()


# ------ Async Server Handler ------



async def startWeb(ip,port,srt):

    # Internal Modules
    global server
    server = WebInterface(ip,port,srt)

    """ Start connections to async modules """

    # Setup CTRL-C signal to end programm
    signal.signal(signal.SIGINT, exit_handler)
    print('Press Ctrl+C to exit program')

    # Start async modules
    L = await asyncio.gather(
        server.start(),
        asyncLoop()
    )


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
        return f'{Title.datetimeToSrt(self.start)} --> {Title.datetimeToSrt(self.end)}\n{self.text}'

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
    parser.add_argument('-w', '--web', help="Start web server", action='store_true')
    parser.add_argument('-i', '--ip', help="Web server listening IP", default="0.0.0.0")
    parser.add_argument('-p', '--port', help="Web server listening IP", default="5001")
    parser.add_argument('message', help="", default=None, nargs=argparse.REMAINDER)
    args = parser.parse_args()



    # Run web server
    if args.web:
        asyncio.run(startWeb(args.ip,args.port,args.srt))
        sys.exit(0)


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
