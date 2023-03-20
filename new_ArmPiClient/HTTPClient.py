import requests
#HTTP client
class HTTPClient():
    def __init__(self, url):
        self.url = url
        self.headers = {'User-Agent': 'Mozilla/5.0'}
    def get(self, param):
        Params={'value':param}
        response = requests.get(self.url, params=Params, headers=self.headers)
        return response
    
    def post(self, param):
        Params={'value':param}
        response = requests.post(self.url, params=Params, headers=self.headers)
        return response