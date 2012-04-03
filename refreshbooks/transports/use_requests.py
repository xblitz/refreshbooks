import requests

class Transport(object):
    def __init__(self, url, headers_factory):
        self.client = requests
        self.url = url
        self.headers_factory = headers_factory
    
    def __call__(self, entity):
        
        resp = self.client.post(
            self.url,
            headers=self.headers_factory(),
            data=entity
        )
        if resp.status_code >= 400:
            raise TransportException(resp.status, content)
        
        return resp.content
