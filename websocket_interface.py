import json
from pprint import pprint

import asyncio
import signal
import uuid

from quart import Blueprint
from quart import flash
from quart import g
from quart import redirect
from quart import render_template
from quart import request
from quart import websocket
from quart import session
from quart import url_for

# For copying function metadata through decorators
from functools import wraps

class WebSocketHandler(object):
    """
    Interface class for handling websockets with UUIDs for client identification
    """


    def __init__(self,ws):
        """
        Store websocket and create UUID

        :param ws: Current websocket instance
        """

        self.ws = ws
        self.uuid = uuid.uuid1()
        self.subs = []

    async def updateClient(self):
        """
        Updates client with new uuid

        :return: returns nothing
        """
        await self.sendEvent("new_uuid", self.uuid)

    async def sendEvent(self, event, data):
        """
        Sends a dictionary as a packaged event to websocket client

        :param event: event name as string
        :param data: dict of data to send as payload
        :return: returns nothing
        """
        await self.ws.send(json.dumps(
            {
                "uuid":self.uuid.hex,
                "event":event,
                "data":data
                }
                ,default=str
            ))


    async def sendSub(self, sub, data):
        """
        Sends a dictionary as a packaged event to websocket client

        :param event: event name as string
        :param data: dict of data to send as payload
        :return: returns nothing
        """
        await self.ws.send(json.dumps(
            {
                "uuid":self.uuid.hex,
                "event":"sub",
                "sub": sub,
                "data":data
                }
                ,default=str
            ))

    async def websocket_receiver(self):
        """
        Called when new websocket data is received. Calls self.receive() with dict formated data

        :return: returns nothing
        """
        while True:
            data = json.loads( await self.ws.receive() )
            await self.receive(data)

    async def receive(self,data):
        """
        Overloadable function for user to handle data received

        :param data: dict of data received as payload
        :return: returns nothing
        """
        pprint(data)
        return

    def wsClose(self):
        self.ws.close(100)



class WebSocketClients(object):
    """
    Manages multiple websocket client connections to a single endpoint.

    Handles forced disconnection of clients on program exit.
    """

    def __init__(self):
        """
        Creates management variables for clients.
        """

        self.websocket_clients = {}
        self.websocket_subscriptions = {}
        self.websocket_alive = True


    def exit_handler(self, sig, frame):
        """
        Handle CTRL-C to gracefully end program and API connections

        :param sig: Some signal thing
        :param frame: Where you put pictures, idk
        :return: returns nothing
        """
        print('You pressed Ctrl+C!:Websocket')
        self.websocket_alive = False


    async def websocket_connect(self,wsh):
        """
        Looping segement that breaks out websocket receiver task

        :param wsh: Instance of WebSocketHandler object
        :return: returns nothing
        """

        try:
            # Break out websocket listener to avoid blocking loop
            consumer = asyncio.create_task(wsh.websocket_receiver())

            # Register program end signal
            signal.signal(signal.SIGINT, self.exit_handler)

            # Loop until program is ended
            while self.websocket_alive:

                await asyncio.sleep(1)
            # End recieving task
            consumer.cancel()

            # Close out tasks
            await asyncio.gather(consumer)

        except asyncio.CancelledError:
            # Handle disconnection here
            print("Oh noes!")
            raise


    async def websocket_broadcast(self,data):
        """
        Send data payload to all connected clients

        :param data: payload to send
        :return: returns nothing
        """
        for key, client in self.websocket_clients.items():
            await client.sendEvent("broadcast",data)


    async def websocket_subscribe(self,sub,uuid):
        """
        Subscribe a UUID to receive data when a subscription is called

        :param sub: id of subscription
        :param uuid: uuid for websocket connection
        :return: returns nothing
        """
        if sub not in self.websocket_subscriptions:
            self.websocket_subscriptions[sub]=[]

        self.websocket_subscriptions[sub].append(uuid)


    async def websocket_unsubscribe(self,sub,uuid):
        """
        Unsubscribe a UUID from subscription

        :param sub: id of subscription
        :param uuid: uuid for websocket connection
        :return: returns nothing
        """
        if sub not in self.websocket_subscriptions:
            return

        self.websocket_subscriptions[sub].remove(uuid)


    async def websocket_unsubscribe_all(self,uuid):
        """
        Unsubscribe a UUID from all subscriptions

        :param uuid: uuid for websocket connection
        :return: returns nothing
        """
        for sub in self.websocket_clients[uuid].subs:
            self.websocket_unsubscribe(sub,uuid)


    async def call_sub(self,sub,data):
        """
        Subscribe a UUID to receive data when a subscription is called

        :param data: payload to send
        :return: returns nothing
        """
        print(f"Calling [{sub}] with [{dir(data)}]")
        if sub not in self.websocket_subscriptions:
            print(f"[{sub}] Does not exist")
            return False

        for uuid in self.websocket_subscriptions[sub]:
            await self.websocket_clients[uuid].sendSub(sub,data)


    def websocket_register(self, ws_class = WebSocketHandler):
        """
        Decorator for registering new websocket connections

        :param ws_class: WebSocketHandler or child class to use for websocket connections
        :return: returns nothing
        """
        # Decorator function to receive fucntion pointer for argument handling
        def decorator(func):
            # Wrap doc to new function
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Create instance of handler
                wsh = ws_class(websocket._get_current_object())
                # Send client uuid
                await wsh.updateClient()
                # Store client connection
                self.websocket_clients[wsh.uuid]=wsh

                print("Client added")

                try:
                    # Call main function
                    return await func(wsh)
                finally:
                    # Remove websocket client from all subs
                    await self.websocket_unsubscribe_all(wsh.uuid)

                    # Remove websocket client on disconnection
                    del self.websocket_clients[wsh.uuid]
                    print("Client removed")

            return wrapper
        return decorator
