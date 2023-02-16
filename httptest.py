import requests

class HTTPClient():
    def __init__(self, url):
        self.url = url
        self.headers = {'User-Agent': 'Mozilla/5.0'}
    def call(self, param):
        Params={'id':''}
        Params['id']=param
        response = requests.get(self.url, params=Params, headers=self.headers)
        return response

# url = 'http://192.168.0.100:8088'
# params = {'id': '000000003'}
# headers = {'User-Agent': 'Mozilla/5.0'}

# response = requests.get(url, params=params, headers=headers)

# print(response.text)
HTTPclient=HTTPClient('http://192.168.0.100:8088')
ret=HTTPclient.call('000000004')
print(ret.text)