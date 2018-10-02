'''
This simple WebSocket server responds to text messages by reversing each
message string and sending it back.

It also handles ping/pong automatically and will correctly close down a
connection when the client requests it.

To use SSL/TLS: install the `trustme` package from PyPI and run the
`generate-cert.py` script in this directory.
'''
import argparse
import logging
import pathlib
import ssl
import sys

import trio
from trio_websocket import serve_websocket, ConnectionClosed


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
here = pathlib.Path(__file__).parent


def parse_args():
    ''' Parse command line arguments. '''
    parser = argparse.ArgumentParser(description='Example trio-websocket client')
    parser.add_argument('--ssl', action='store_true', help='Use SSL')
    parser.add_argument('host', help='Host interface to bind to (all)')
    parser.add_argument('port', type=int, help='Port to bind to')
    return parser.parse_args()


async def main(args):
    ''' Main entry point. '''
    logging.info('Starting websocket server…')
    if args.ssl:
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        try:
            ssl_context.load_cert_chain(here / 'fake.server.pem')
        except FileNotFoundError:
            logging.error('Did not find file "fake.server.pem". You need to run'
                ' generate-cert.py')
    else:
        ssl_context = None
    host = args.host if args.host == '' else None
    await serve_websocket(handler, host, args.port, ssl_context)


async def handler(websocket):
    ''' Reverse incoming websocket messages and send them back. '''
    logging.info('Handler starting (path=%s)' % websocket.path)
    while True:
        try:
            message = await websocket.get_message()
            await websocket.send_message(message[::-1])
        except ConnectionClosed:
            logging.info('Connection closed')
            break
    logging.info('Handler exiting')


if __name__ == '__main__':
    try:
        trio.run(main, parse_args())
    except KeyboardInterrupt:
        print()
