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
from time import sleep

try:
    # External Modules
    from quart import Quart
    from quart import Response
    from quart import request
    from quart import send_file
    from quart import redirect
    from quart import make_response
    from quart import render_template
    from quart import send_from_directory
except Exception as e:
        print("Need to install Python module [flask]")
        sys.exit(1)

from srt import SRT, Title

from websocket_interface import WebSocketClients, WebSocketHandler

wsc = WebSocketClients()



args=None

def create_app(args):

    host_dir=os.path.realpath(__file__).replace(os.path.basename(__file__),"")
    app = Quart("SRT Notes")
    app.logger.disabled = True
    #log = logging.getLogger('werkzeug')
    #log.disabled = True

    # Static content
    app.static_folder=host_dir+"http/static"
    app.static_url_path='/static/'

    @app.websocket("/ws")
    @wsc.websocket_register()
    async def ws(wsh):
        await wsc.websocket_connect(wsh)
        return

    @app.route("/")
    async def index():
        """ Simple class function to send HTML to browser """
        return await render_template("base.html", data={"srt-name":args.srt})


    @app.route("/add", methods=("GET", "POST"))
    async def add_title():
        srt = SRT(args.srt)
        data = await ( request.get_json() )
        pprint(data)
        srt.add(text=data["text"])
        srt.save()

        await wsc.websocket_broadcast({
            "command":"add",
            "srt":srt.get().toJson()
        })
        return "sure"

    @app.route("/update", methods=("GET", "POST"))
    async def update_title():
        srt = SRT(args.srt)

        data = await ( request.get_json() )
        pprint(data)
        start=Title.srtToDatetime(data['start'])
        srt.update(start=start,text=data["text"])
        srt.save()

        try:
            await wsc.websocket_broadcast({
                "command":"update",
                "srt":srt.get(start).toJson()
            })
        except Exception as e:
             print(e)

        return "sure"

    @app.route("/remove", methods=("GET", "POST"))
    async def remove_title():
        srt = SRT(args.srt)
        data = await ( request.get_json() )
        pprint(data)
        start=Title.srtToDatetime(data['start'])
        srt.remove(start=start)
        srt.save()
        return "sure"

    @app.route("/srt.json")
    async def json():
        """ Simple class function to send HTML to browser """
        srt = SRT(args.srt)
        data=[]
        for title in srt.getTitles():
            data.append(title.toJson())
        pprint(data)
        return data


    return app

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



def process_web(args):
        app = create_app(args)
        """ Run Flask in a process thread that is non-blocking """
        print("Starting Flask")
        return Process(
                target=app.run,
                kwargs={
                "host":"0.0.0.0",
                "port":"5000",
                "debug":False,
                "use_reloader":False
                }
        )

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
        web_thread = process_web(args)
        web_thread.start()
        while web_thread.is_alive():
                sleep(1)
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
