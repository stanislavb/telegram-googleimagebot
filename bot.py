#!/usr/bin/env python3
import argparse
import logging
import time
from api import TelegramAPI, GoogleImagesAPI


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


class TelegramBot:
    gimage_api = GoogleImagesAPI()

    def __init__(self, token):
        boturl = 'https://api.telegram.org/bot'
        logger.info('Secret bot URL: {0}{1}/'.format(boturl, token))
        self.api = TelegramAPI(url='{0}{1}/'.format(boturl, token))

        # Make this bot self-aware
        myself = self.api.get_me()
        self.id = myself['id']
        self.first_name = myself['first_name']
        self.username = myself['username']

        # Define valid commands
        self.commands = {
            'image': self.image
        }

    def image(self, text):
        if text is None:
            return 'Need an argument for image search. Try "/image cute cats"'
        image = self.gimage_api.random_image(query=text)
        if image is None:
            found = "nothing"
        else:
            found = image['url']
        returntext = ('Searched for {}, found {}'.format(text[1], found))
        return returntext

    def command(self, command, text):
        logger.info('Parsing command {} with data: {}'.format(command, text))

        # Check if command has been adressed to a specific bot
        split_command = command.split('@')
        if len(split_command) > 1 and split_command[1] != self.username:
            # Not for us
            return None

        clean_command = split_command[0].lstrip('/')
        if clean_command in self.commands:
            return self.commands[clean_command](text)
        return None

    def handle_message(self, message):
        if 'text' in message:
            text = message['text'].split(maxsplit=1)
            command_args = text[1] if len(text) == 2 else None
            return self.command(text[0], command_args)
        return None

    def respond(self, message):
        chat_id = message['chat']['id']
        returntext = self.handle_message(message)
        if returntext:
            try:
                self.api.send_message(chat_id, text=returntext)
            except:
                logger.exception("Failed to send message.")
        return returntext


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--offset', '-o')
    parser.add_argument('--limit', '-l')
    parser.add_argument('--timeout', '-t')
    parser.add_argument('--wait', '-w')
    parser.add_argument('token')
    args = parser.parse_args()

    bot = TelegramBot(token=args.token)
    offset = args.offset if args.offset else 0
    wait = args.wait if args.wait else 15
    while True:
        logger.info('Waiting {} seconds'.format(wait))
        time.sleep(wait)
        try:
            updates = bot.api.get_updates(
                offset=offset,
                limit=args.limit,
                timeout=args.timeout)
        except:
            logger.exception("Failed to get updates.")
        for update in updates:
            if 'message' in update:
                bot.respond(update['message'])
            if update['update_id'] >= offset:
                offset = update['update_id'] + 1
