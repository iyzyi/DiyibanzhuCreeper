import os.path
import config
from requests_manage import request
from progress_bar import ProgressBar
from threading import Thread, Lock
from os import path, makedirs
import re
from html import unescape
from bs4 import BeautifulSoup
from Crypto.Cipher import AES
import hashlib, base64
import subprocess, functools
subprocess.Popen = functools.partial(subprocess.Popen, encoding="utf-8")
# 不加上两行会导致execjs返回值出现编码错误
import execjs


class FileDownloader:
    
    def __init__(self, urls_list, use_progress_bar, type):
        self.urls_list = urls_list
        self.use_progress_bar = use_progress_bar
        self.type = type
        self.thread_list = []
        self.lock = Lock()
        self.success = True

        self.img_word = {}
        with open('./utils/img标签/变形字体库v2.txt', 'r', encoding='utf-8')as f:
            data = f.read()
        for line in data.split('\n'):
            word, name = line.split(' ')
            self.img_word[name] = word

        self.i_word = {}
        with open('./utils/i标签/字体反爬库.txt', 'r', encoding='utf-8')as f:
            data = f.read()
        for line in data.split('\n'):
            if line != '':
                uni, word = line.split('\t')
                self.i_word[uni] = word

        with open(r'./utils/js混淆/a.js')as f:
            self.a_js = f.read()


        # type = get_chapter_urls 时用到的变量
        self.temp1 = {}
        self.chapter_urls = []
        self.chapter_num = 1
        
        # type = get_section_urls 时用到的变量
        self.temp2 = {}
        self.section_urls = []

        # type = get_section_data 时用到的变量
        self.sections_data = []
        self.chapters_data = {}
        self.chapters_content = {}
        self.chapters_title = {}


        # 进度条
        if use_progress_bar:
            self.progress_bar = ProgressBar(len(self.urls_list), fmt=ProgressBar.IYZYI)
        

    def run(self):
        for i in range(config.thread_num):
            t = Thread(target = FileDownloader.thread_func, args=(self,))
            t.setDaemon(True)               #设置守护进程
            t.start()
            self.thread_list.append(t)

        for t in self.thread_list:
            t.join()                        #阻塞主进程，进行完所有线程后再运行主进程

        return self.merge_result()


    def thread_func(self):
        while True:
            args = None
            self.lock.acquire()
            if len(self.urls_list) > 0:
                args = self.urls_list.pop()
            else:
                self.lock.release()
                break
            self.lock.release()

            if args:
                self.func(args)

            # 绘制进度条
            self.lock.acquire()
            if self.use_progress_bar:
                self.progress_bar.current += 1
                self.progress_bar()
            self.lock.release()


    def func(self, args):
        if self.type == 'get_chapter_urls':
            self.get_chapter_urls(args)

        if self.type == 'get_section_urls':
            self.get_section_urls(args)

        if self.type == 'get_section_data':
            self.get_section_data(args)


    def get_chapter_urls(self, list_url):
        res = request.get(list_url)
        if res:
            try:
                page_html = res.text
            except UnicodeDecodeError:
                page_html = res.content.decode('gbk', 'ignore')
                
            res = re.findall(r'<div class="mod block update chapter-list">.+?<ul class="list">(.+?)</ul>', page_html, re.S)
            if res:
                lis = res[1]
                res = re.finditer(r'<li><a href="(.+?)">(.+?)</a></li>', lis)
                tmp = []
                for li in res:
                    url, name = li.group(1), li.group(2)
                    tmp.append((url, name))
                page_id = re.search(r'^https?://.+?/\d+?/\d+?_(\d+?)/$', list_url).group(1).zfill(8)
                self.temp1[page_id] = tmp
        else:
            self.success = False

    
    def get_section_urls(self, args):
        chapter_id, chapter_url, chapter_name = args
        res = request.get(chapter_url)
        if res:
            try:
                section_html = res.text
            except UnicodeDecodeError:
                section_html = res.content.decode('gbk', 'ignore')

            soup = BeautifulSoup(section_html, 'lxml')
            res = soup.select('.page-content .chapterPages')
            if len(res) == 0:       # e.g https://7yydstxt426.com/0/15/196.html or https://7yydstxt426.com/0/20/333.html
                section_num = 1
            else:
                iter = re.finditer(r'【(\d+?)】', res[0].text)
                temp = []
                for item in iter:
                    temp.append(int(item.group(1)))
                section_num = max(temp)

            res = re.search('^(.+?)/(\d+?)\.html', chapter_url)
            left_url, book_id = res.group(1), res.group(2)
            tmp = []
            for section_id in range(1, section_num+1):
                section_url = '{}/{}_{}.html'.format(left_url, book_id, section_id)
                tmp.append((section_id, section_url))
            self.temp2[chapter_id] = tmp
        else:
            self.success = False
                

    def get_section_data(self, args):
        chapter_id, section_id, section_url = args
        res = request.get(section_url)
        if res:
            try:
                section_html = res.text
            except UnicodeDecodeError:
                section_html = res.content.decode('gbk', 'ignore')    

            section_content = ''
            soup = BeautifulSoup(section_html, 'lxml')

            # 大多数情况
            res1 = soup.select('.page-content .neirong div')
            section_content = res1[0].contents

            # 一般是每一节的第4页
            res = re.search(r"\$\.post\('',{'j':'1'},function\(e\)", section_html)
            if res:
                section_content_part2 = self.get_page4_content(section_url)
                if section_content_part2 == False:
                    self.success = False
                    return
                section_content += section_content_part2

            else:
                # 一般是每一节的第5页
                res = re.search(r"var ns='(.+?)'", section_html)
                if res:
                    try:
                        section_content = self.get_page5_content(section_html, section_url)
                    except Exception as e:
                        # e.g https://7yydstxt426.com/0/74/1061_5.html
                        # 如果行数太少，浏览器都会执行"换行操作"失败
                        # 形如ns: MjEsMjE=，即ns特别短的这种情况，不用担心，因为数据都在res2里面
                        print(f'模拟执行js失败, url: {section_url}, ns: {res.group(1)}')
                        with open(r'LOG.txt', 'a+')as f:
                            f.write('模拟执行js失败，请检查提取的内容是否正确: ' + section_url + '\n')

                        res2 = soup.select('.page-content .neirong #chapter div:nth-of-type(1)')
                        section_content = res2[0].contents

                else:
                    # 一般是每一节的第2页
                    res = re.search(r'''var chapter = secret\(\s*?["']{1}(.+?)["']{1},\s*["']{1}(.+?)["']{1},.+?\);''', section_html, re.S)
                    if res:
                        cipher = res.group(1).strip()
                        code = res.group(2).strip()
                        section_content = self.get_page2_content(cipher, code)

            self.sections_data.append((chapter_id, section_id, section_url, section_content))

        else:
            self.success = False
       

    def merge_result(self):
        if not self.success:
            return None

        if self.type == 'get_chapter_urls':
            for page_id in sorted(self.temp1.keys()):
                for relative_url, chapter_name in self.temp1[page_id]:
                    chapter_url = config.root_url + relative_url
                    self.chapter_urls.append((self.chapter_num, chapter_url, chapter_name))
                    self.chapter_num += 1       
            return self.chapter_urls         


        if self.type == 'get_section_urls':
            for chapter_id in sorted(self.temp2.keys()):
                data = self.temp2[chapter_id]
                for section_id, section_url in data:
                    self.section_urls.append((int(chapter_id), int(section_id), section_url))
            return self.section_urls


        if self.type == 'get_section_data':
            chapter_num = max([info[0] for info in self.sections_data])
            for _chapter_id in range(1, chapter_num+1):
                tmp = []
                for chapter_id, section_id, section_url, section_content in self.sections_data:
                    if chapter_id == _chapter_id:
                        tmp.append((section_id, section_content))
                self.chapters_data[str(_chapter_id).zfill(8)] = tmp
            
            for chapter_id in self.chapters_data.keys():
                sections_data = self.chapters_data[chapter_id]
                key = str(chapter_id).zfill(8)
                for section_id, section_content in sorted(sections_data, key = lambda x:x[0]):
                    # # for debug
                    # if not os.path.exists('test'):
                    #     os.makedirs('test')
                    # with open(rf'test/{chapter_id}_{section_id}.txt', 'w', errors='ignore')as f:
                    #     f.write(self.format_content(section_content))

                    if key not in self.chapters_content.keys():
                        self.chapters_content[key] = section_content
                    else:
                        self.chapters_content[key] += section_content
                if key in self.chapters_content.keys():
                    self.chapters_content[key] = self.format_content(self.chapters_content[key])
            
            return self.chapters_content

    
    def format_content(self, content_list):
        content = ''
        for item in content_list:
            if item.name == 'img':
                if item.attrs.__contains__('src'):
                    link = item.attrs['src']
                    res = re.search(r'/toimg/data/(.+?.png)', link)
                    if res:
                        try:
                            img_name = res.group(1)
                            content += self.img_word[img_name]
                        except:
                            print('img标签{}/{}没有对应变形字！'.format(config.root_url, link))
                            raise
            
            elif item.name == 'br':
                content += '\n'
            
            # 一般出现在每一节的第3页
            elif item.name == 'i':
                i_uniword = repr(item.contents[0])[1:-1]
                res = re.match(r'\\u[a-fA-f0-9]{4}', i_uniword)
                if res:                    
                    try:
                        content += self.i_word[i_uniword]
                    except:
                        print('i标签{}没有对应反爬字！'.format(i_uniword))
                        raise
                else:
                    content += item.text.strip().replace('<br/>', '\n')

            else:
                temp = item.text.strip()
                content += temp

        content = re.sub(r'(?<=[^。！？…”」((?<=\*2,})\*)((?<=\+{2,})\+)((?<=\-{2,})\-)((?<=\-{2,})＊)])\n','',content)    #\n前不为。！？以及3个*或+或-或＊以上的字符（即分割线）时删掉这个\n
        content = re.sub(r'\n','\n\n    ',content)    #段落间添加空行,并首行缩进
        content = '    ' + content
        
        return content

    def get_page2_content(self, ciphertext, code):
        m = hashlib.md5()
        m.update(code.encode())
        temp = m.hexdigest()
        iv, key = temp[:16].encode(), temp[16:].encode()

        cipher = base64.b64decode(ciphertext.encode())
        aes = AES.new(key, AES.MODE_CBC, iv)
        plain = aes.decrypt(cipher)
        plain = plain[:-plain[-1]].decode()

        plain = '<div>' + plain + '</div>'

        soup = BeautifulSoup(plain, 'lxml')
        res = soup.select('div')
        return res[0].contents


    def get_page4_content(self, section_url):
        data = {'j': '1'}
        res = request.post(section_url, data)
        if res == False:
            return False
        
        content = '<div>' + res.text + '</div>'
        soup = BeautifulSoup(content, 'lxml')
        res = soup.select('div')
        return res[0].contents
    

    def get_page5_content(self, section_html, section_url):
        full_a_js = '''
        const jsdom = require("jsdom");
        const { JSDOM } = jsdom;
        const dom = new JSDOM(`%s`);
        window = dom.window;
        document = window.document;
        XMLHttpRequest = window.XMLHttpRequest;
        %s
        function get_data(ns) {
            _ii_rr(ns);
            return dom.window.document.querySelector("#ad").innerHTML;
        }
        ''' % (section_html.replace('\n', '').replace('`', '\\`'), self.a_js)

        res = re.search(r"var ns='(.+?)'", section_html)
        if res:
            ns = res.group(1)
            
            ctx = execjs.compile(full_a_js) 
            content = ctx.call("get_data", ns)

            content = re.sub(r'<div.+?>', '', content)
            content = re.sub(r'</div>', '', content)

            content = '<div>' + content + '</div>'
            soup = BeautifulSoup(content, 'lxml')
            res = soup.select('div')
            return res[0].contents
        else:
            raise
