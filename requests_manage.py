import threading, time
import requests
import config
from cloudflare_bypass import CloudflareBypass, is_bypassed
import utils


class RequestManager:

    def __init__(self, timeout = 20, retry_num = 5):
        self.timeout = timeout
        self.retry_num = retry_num
        self.lock = threading.Lock()
        self.last_bypassed = 0
        self.headers = {}
        self.bypass_cloudflare()
        self.session = requests.Session()


    def bypass_cloudflare(self):
        self.lock.acquire()
        now = int(time.time())
        if now - self.last_bypassed > 60:
            utils.send_email('try to bypass cloudflare', '')
            print('\n***************** bypass cloudflare *****************')
            cf = CloudflareBypass(config.browser_path, config.root_url)
            user_agent, cookie = cf.bypass()
            self.headers = {
                'user-agent': user_agent,
                'cookie': cookie,
            }
            print(f'user-agent: {user_agent}\ncookie: {cookie}')
            print('***************** bypass cloudflare *****************\n')
            self.last_bypassed = int(time.time())
        else:
            print(f'距离上次bypass cloudflare不超过60s，忽略此次bypass')
        self.lock.release()


    def get(self, url):
        success = False

        for i in range(self.retry_num):
            try:
                if i != 0:
                    print('第{}次重连 {}'.format(i+1, url))

                if config.proxies != {}:
                    res = self.session.get(url, headers=self.headers, timeout=self.timeout, proxies=config.proxies)
                else:
                    res = self.session.get(url, headers=self.headers, timeout=self.timeout)

                if len(res.content) > 0:

                    # with open('test.html', 'wb')as f:
                    #     f.write(res.content)

                    if not is_bypassed(res.text):
                        self.bypass_cloudflare()

                    elif '&#20026;&#38450;&#27490;&#24694;&#24847;&#35775;&#38382;&#44;&#35831;&#36755;&#20837;【1234】' in res.text:
                        data = {'action': '1', 'v': '1234'}
                        resp = self.post(url, data)
                        if resp and resp.text == 'success':
                            print('post 1234 success')

                    # 被风控时的404页面不是真的404，只是前端把正文内容隐藏了而已。
                    else:
                        success = True
                        break

            except Exception as e:
                pass
                #print(e)

        if success:
            return res
        else:
            return False


    def post(self, url, data):
        success = False
        for i in range(self.retry_num):
            try:
                if i != 0:
                    print('第{}次重连 {}'.format(i+1, url))
                if config.proxies != {}:
                    res = self.session.post(url, headers=self.headers, data=data, proxies=config.proxies)
                else:
                    res = self.session.post(url, headers=self.headers, data=data)
                if res.status_code == 200:
                    success = True
                    break
            except Exception as e:
                pass
        if success:
            return res
        else:
            return False


request = RequestManager()