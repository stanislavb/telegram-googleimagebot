#!/usr/bin/env python3
import argparse
import logging
import time
import requests
from contextlib import closing
from api import TelegramAPI, GoogleImagesAPI


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
boturl = 'https://api.telegram.org/bot'


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--offset', '-o')
    parser.add_argument('--limit', '-l')
    parser.add_argument('--timeout', '-t')
    parser.add_argument('--wait', '-w')
    parser.add_argument('token')
    args = parser.parse_args()

    logger.info('Secret bot URL: {0}{1}/'.format(boturl, args.token))
    telegramapi = TelegramAPI(url='{0}{1}/'.format(boturl, args.token))
    googleapi = GoogleImagesAPI()

    offset = args.offset if args.offset else 0
    wait = args.wait if args.wait else 15
    while True:
        logger.info('Waiting {} seconds'.format(wait))
        time.sleep(wait)
        updates = telegramapi.get_updates(
            offset=offset,
            limit=args.limit,
            timeout=args.timeout)
        for update in updates:
            if 'message' in update:
                message = update['message']
                chat_id = message['chat']['id']
                if 'text' in message:
                    text = message['text'].split(maxsplit=1)
                    if len(text) == 2 and text[0] == '/image':
                        url = googleapi.random_image_url(query=text[1])
                        logger.info('Searched for {}, found {}'.format(text[1], url))
                        telegramapi.send_message(chat_id, text=url)
            if update['update_id'] >= offset:
                offset = update['update_id'] + 1
