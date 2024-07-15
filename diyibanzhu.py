import config
from requests_manage import request
from file_downloader import FileDownloader
import re, json, html, os, time


class DiyibanzhuDownloader:

    def __init__(self, view_url):
        self.view_url = view_url

        if not os.path.exists(config.root_path):
            os.makedirs(config.root_path)

    
    def run(self):

        res = re.search(r'^https.*?://.+?/\d+/(\d+)/$', self.view_url)
        if not res:
            print('网址格式不正确')
        elif self.already_downloaded(res.group(1)):
            print('此小说爬取过，跳过此任务')
        elif self.already_failed(res.group(1)):
            print('此小说可能没有数据，跳过此任务')
        elif self.need_skip(res.group(1)):
            print('此小说被手动设定跳过')
        else:
            self.book_id = res.group(1)
            self.book_num = str(int(self.book_id) // 1000)

            res = request.get(self.view_url)
            if res:
                try:
                    view_html = res.text
                except UnicodeDecodeError:
                    view_html = res.content.decode('gbk', 'ignore')
                    
                if self.get_info(view_html):
                    if self.get_chapters_content(view_html):
                        self.create_book()

    
    def get_info(self, view_html):
        try:
            #print('正在获取小说信息......')
            res = re.search(r'\(第(\d+?)/(\d+?)页\)当前\d+?条/页', view_html)
            self.page_num = int(res.group(2))

            res = re.search(r'<h1>(.+?)</h1>', view_html)
            self.title = res.group(1)
            self.title = re.sub(r'[\/\\\*\?\|/:"<>\.]', '', self.title)
            #print('书名: {}'.format(self.title))

            res = re.search(r'<div class="mod book-intro">.*?<div class="bd">(.+?)</div>', view_html, re.S)
            self.introduction = res.group(1).replace('\n', '')

            res = re.search(r'<p class="info">(.+?)</p>', view_html, re.S)
            self.book_info = res.group(1)
            self.book_info = re.sub(r'<br\s*?/>', '', self.book_info)
            self.book_info = self.book_info.replace('\t', '')
            self.book_info = self.book_info.strip()

            return True

        except Exception as e:
            print('下载{} 失败： {}'.format(self.view_url, e))
            if re.search(r'本页没有章节，请.+?点击这里返回', view_html):
                self.download_failed(self.book_id)
                print('已写入FAILED.txt，下次下载会跳过本书')
            return False


    def get_chapters_content(self, html):
        page_urls = []
        for page_id in range(1, self.page_num+1):
            page_url = '{}/{}/{}_{}/'.format(config.root_url, self.book_num, self.book_id, page_id)
            page_urls.append(page_url)

        print('正在获取Chapter URL......')
        ff = FileDownloader(page_urls, True, 'get_chapter_urls')
        chapter_urls = ff.run()
        if not chapter_urls:
            print('获取Chapter URL失败！')
            return False

        self.chapters_title = {}
        for data in chapter_urls:
            chapter_id, chapter_url, chapter_name = data
            self.chapters_title[str(chapter_id).zfill(8)] = chapter_name
        
        print('\n正在获取Section URL......')
        gg = FileDownloader(chapter_urls, True, 'get_section_urls')
        section_urls = gg.run()
        if not section_urls:
            print('获取Section URL失败！')
            return False

        print('\n正在获取小说正文内容......')
        ii = FileDownloader(section_urls, True, 'get_section_data')
        self.chapters_content = ii.run()
        if not self.chapters_content:
            print('获取小说正文内容失败！')
            return False
        
        return True


    def create_book(self):
        file_path = os.path.join(config.root_path, self.title+'.txt')

        front = '书名：{}\n\n{}\n网址：{}\n\n简介：{}\n'.format(self.title, self.book_info, self.view_url, self.introduction)
        with open(file_path, 'w+', errors='ignore')as f:
            f.write(front)

        for chapter_id, chapter_content in self.chapters_content.items():
            chapter_title = self.chapters_title[chapter_id]
            chapter_id = int(chapter_id)
    
            if not re.search(r'^第\w+?[章节卷回篇]', chapter_title):
                chapter_title = '第{}节 {}'.format(chapter_id, chapter_title)
            with open(file_path, 'a+', errors='ignore') as f:
                f.write('\n\n'+chapter_title+'\n\n')

            with open(file_path, 'a+', errors='ignore')as f:
                f.write(chapter_content)

        self.download_success()

    
    def already_downloaded(self, book_id):
        if not os.path.exists('SAVED.txt'):
            return False
        with open(r'SAVED.txt')as f:
            ids = f.read()
        return book_id in ids.split('\n')

    
    def already_failed(self, book_id):
        if not os.path.exists('FAILED.txt'):
            return False
        with open(r'FAILED.txt')as f:
            ids = f.read()
        return book_id in ids.split('\n')


    def download_success(self):
        log_path = r'SAVED.txt'
        with open(log_path, 'a+')as f:
            f.write(self.book_id+'\n')


    def download_failed(self, book_id):
        log_path = r'FAILED.txt'
        with open(log_path, 'a+')as f:
            f.write(book_id+'\n')


    def need_skip(self, book_id):
        if not os.path.exists('SKIP.txt'):
            return False
        with open(r'SKIP.txt')as f:
            ids = f.read()
        return book_id in ids.split('\n')


def download_all_books():
    for book_id in range(1, 60000):
        print('\n-----------------------------------------------------------------')
        url = '{}/{}/{}/'.format(config.root_url, book_id//1000, book_id)
        print('爬取小说%d：(%s)' % (book_id, url))
        dd = DiyibanzhuDownloader(url)
        dd.run()
        print('\n-----------------------------------------------------------------\n')


if __name__ == '__main__':
    # url = 'https://www.33yydstxt426.com/0/74/'
    # dd = DiyibanzhuDownloader(url)
    # dd.run()

    download_all_books()
