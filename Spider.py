# -*- coding: utf-8 -*-
# @Author : Huangcc

import requests
from lxml import etree
from collections import deque


class LinuxidcSpider:
    def __init__(self):
        self.url = 'https://linux.linuxidc.com/'
        self.queues = deque()
        self.session = requests.Session()
        self.queues.append((self.url, 'init url', 'folder.png', 'folder', '2018-01-01 00:00'))

    def get_all_files(self):
        while self.queues:
            url, name, _, _, _ = self.queues.popleft()
            print 'searching {} with url {}'.format(name, url)
            lines = self.get_files_from_url(url)
            print lines
            folder_lines = filter(lambda x: x[3] == 'folder', lines)
            file_lines = filter(lambda x: x[3] == 'file', lines)
            self.queues.extend(folder_lines)
            self.write_result_to_file(file_lines)

    @staticmethod
    def write_result_to_file(lines):
        with open('result.csv', 'a') as f:
            lines = [','.join(line)+'\n' for line in lines]
            f.writelines(lines)

    def get_files_from_url(self, url):
        print 'getting files...'
        results = list()
        try:
            resp = self.session.get(url, timeout=1)
            html = etree.HTML(resp.text)
            trs = html.xpath('//tr')
            for tr in trs:
                a = tr.xpath('td/div/a')
                div = tr.xpath('td/div')
                if len(a) == 1:
                    url = a[0].xpath('@href')[0]
                    url = url if url.startswith('http') else self.url + url
                    name = a[0].xpath('text()')[0].encode('utf-8')
                    image_src = div[0].xpath('img/@src')[0]
                    update_time = tr.xpath('td[last()]/text()')[0]
                    file_type = 'folder' if image_src.endswith('folder.png') else 'file'
                    results.append((url, name, image_src, file_type, update_time))
            print 'finishing getting files...'
        except requests.exceptions.ReadTimeout:
            print 'failed with url {}'.format(url)
        return results

if __name__ == '__main__':
    spider = LinuxidcSpider()
    spider.get_all_files()
