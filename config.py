# 保存路径
root_path = r'D:\爬虫\第一版主'

# 下载线程数
thread_num = 32

# 第一版主的网址，最后不要以/结尾
root_url = 'https://www.33yydstxt226.com'

# 浏览器路径（用于绕过Cloudflare真人检测），必须是 Chromium 内核（如 Chrome 和 Edge）
# browser_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
browser_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'

proxies = {}
# proxies = {'http': 'http://127.0.0.1:8889/', 'https': 'http://127.0.0.1:8889/'}

# https://www.drissionpage.cn/ChromiumPage/browser_opt/#-set_proxy
# for drissionpage, 必须这个格式。不用则置None。
http_proxy = None#'127.0.0.1:8889'

# wget -e "http_proxy=http://127.0.0.1:8889/" http://baidu.com

email = {    
    'from': "",
    'to': '',
    'code': ''
}