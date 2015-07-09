import requests
import logging
from urllib.parse import urljoin
import random

logger = logging.getLogger()

# Surpress warnings 'Unverified HTTPS request is being made"
requests.packages.urllib3.disable_warnings()


class API:

    session = requests.Session()

    def __init__(self, url, user=None, password=None):
        self.url = url
        if user and password:
            self.session.auth = (user, password)

    def request(self, method, endpoint, **kwargs):
        params = {}
        if kwargs is not None:
            for key, value in kwargs.items():
                params[key] = value

        full_url = urljoin(self.url, endpoint)
        logger.debug('{0} to {1}'.format(method, full_url))
        response = self.session.request(method, full_url, params=params)
        response.raise_for_status()
        content = response.json()
        logger.info('Got response from {}: {}'.format(self.url, content))
        return content

    def get(self, endpoint, **kwargs):
        return self.request('GET', endpoint, **kwargs)

    def post(self, endpoint, **kwargs):
        return self.request('POST', endpoint, **kwargs)


class TelegramAPI(API):

    def request(self, method, endpoint, **kwargs):
        content = super(TelegramAPI, self).request(method, endpoint, **kwargs)
        if not content['ok']:
            logger.error('API returned error: {}'.format(content['description']))
        return content['result']

    def get_updates(self, **kwargs):
        return self.get('getUpdates', **kwargs)

    def send_message(self, chat_id, text, **kwargs):
        return self.post('sendMessage', chat_id=chat_id, text=text, **kwargs)

    def send_photo(self, chat_id, photo, **kwargs):
        return self.post('sendPhoto', chat_id=chat_id, photo=photo, **kwargs)


class GoogleImagesAPI(API):

    def __init__(self):
        self.url = 'https://ajax.googleapis.com/ajax/services/search/'

    def request(self, method, endpoint, **kwargs):
        content = super(GoogleImagesAPI, self).request(method, endpoint, **kwargs)
        return content['responseData']['results']

    def images(self, query, results=8):
        assert 1 <= results <= 8
        return self.get('images', v='1.0', rsz=results, imgsz='small', q=query)

    def random_image(self, query, results=8):
        results = self.images(query, results)
        if results:
            return random.choice(results)
        else:
            return None
