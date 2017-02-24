import base64
import requests

from refreshbooks import exceptions

try:
    from refreshbooks.optional import oauth as os
    OAuthAuthorization = os.OAuthAuthorization
except ImportError:
    def OAuthAuthorization(consumer, token, sig_method=None):
        raise NotImplementedError('oauth support requires the "oauth" module.')


class Transport(object):
    def __init__(self, url, headers_factory):
        self.session = requests.session()
        self.url = url
        self.headers_factory = headers_factory

    def __call__(self, entity):
        resp = self.session.post(
            self.url,
            headers=self.headers_factory(),
            data=entity
        )
        if resp.status_code >= 400:
            raise exceptions.TransportException(resp.status_code, resp.content)

        return resp.content


class TokenAuthorization(object):
    """Generates HTTP BASIC authentication headers obeying FreshBooks'
    token-based auth scheme (token as username, password irrelevant).
    
        >>> auth = TokenAuthorization("monkey")
        >>> auth()
        {'Authorization': 'Basic bW9ua2V5Og=='}
    
    Prefer OAuthAuthorization, from refreshbooks.optional.oauth, for new
    development.
    """

    def __init__(self, token):
        try:
            token = token.encode('US-ASCII')
        except NameError:
            # token already byte string.
            pass
        # See RFC 2617.
        base64_user_pass = base64.b64encode(token + b':').decode('US-ASCII')

        self.headers = {
            'Authorization': 'Basic %s' % (base64_user_pass,)
        }

    def __call__(self):
        return self.headers


class UserAgentHeaders(object):
    def __init__(self, base_headers_factory, user_agent):
        self.base_headers_factory = base_headers_factory
        self.user_agent = user_agent

    def __call__(self):
        headers = self.base_headers_factory()
        headers['User-Agent'] = self.user_agent
        return headers


class KeepAliveHeaders(object):
    def __init__(self, base_headers_factory):
        self.base_headers_factory = base_headers_factory

    def __call__(self):
        headers = self.base_headers_factory()
        headers['Connection'] = 'Keep-Alive'
        return headers


HttpTransport = Transport
TransportException = exceptions.TransportException
