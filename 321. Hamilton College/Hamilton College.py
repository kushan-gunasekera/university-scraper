# Adelphi University
import itertools
import re
import json
import math
import random
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures._base import as_completed

import requests
import xlsxwriter
from bs4 import BeautifulSoup
from lxml import html
import urllib.parse

HEADERS = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8,si;q=0.7',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'Origin': 'https://catalog.haverford.edu',
    'Referer': 'https://catalog.haverford.edu/course-search/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
}

MAIN_DOMAIN = 'https://hamilton.smartcatalogiq.com'
UNIVERSITY = 'Hamilton College  '


def get_description(code, url_path):
    print(f'code: {code} | url: {url_path}')
    url = f'{MAIN_DOMAIN}{url_path}'.lower()
    headers = {
        # 'Referer': url_path,
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    }
    r = requests.get(url, headers=headers)
    try:
        soup = BeautifulSoup(r.content, 'html.parser')
        desc = soup.find('div', class_='desc').text.strip()
        return {'course_code': code, 'description': desc}
    except Exception as e:
        print(f'ERROR code: {code} | url: {url_path} ')
        return {'course_code': code, 'description': ''}


def get_course(url_path):
    print(url_path)
    courses = {}
    descriptions = []
    url = f'{MAIN_DOMAIN}{url_path}'.lower()

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8,si;q=0.7',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Referer': 'https://hamilton.smartcatalogiq.com/current/College-Catalogue/AcademicPrograms/Africana-Studies/AFRST-Africana-Studies-Courses',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"'
    }
    try:
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.content, 'html.parser')
        tr_tags = soup.find('table', id='primaryTable').find_all('tr')
        for tr in tr_tags:
            code_a = tr.find('td', class_='coursetitle').find('a')
            code = code_a.text
            title = tr.find('td', class_='coursename').text
            courses[code] = {
                'course_code': code,
                'course_name': title
            }
            descriptions.append([code, code_a.get('href')])

        with ThreadPoolExecutor(max_workers=10) as executor:
            for i in as_completed(executor.submit(get_description, code, url) for code, url in descriptions):
                result = i.result()
                courses[result.get('course_code')]['course_description'] = result.get('description')

        print(f'{len(courses)} courses in {url_path}')
    except Exception as e:
        print('*' * 50)
        print(f'ERROR: {url} | {e}')
        print('*' * 50)
    return courses


def get_course_urls():
    def rec(i):
        paths = []
        if i.get('Name').endswith('Courses'):
            paths.append(i.get('Path'))
        children = i.get('Children', [])
        for j in children:
            paths.extend(rec(j))
        return paths
    url = f'{MAIN_DOMAIN}/Institutions/Hamilton-College/json/current/College-Catalogue.json'

    r = requests.get(url)
    return rec(r.json())


def main():
    course_urls = get_course_urls()
    full_courses = {}
    with ThreadPoolExecutor(max_workers=1) as executor:
        for i in as_completed(executor.submit(get_course, url) for url in course_urls):
            full_courses = {**full_courses, **i.result()}

    with open(f'{UNIVERSITY}.json', 'w') as json_file:
        json.dump(full_courses, json_file, indent=4)

    header = ['course_code', 'course_name', 'course_description']
    workbook = xlsxwriter.Workbook(f'{UNIVERSITY}.xlsx')
    worksheet = workbook.add_worksheet()
    for col, header_name in enumerate(header):
        worksheet.write(0, col, header_name)

    row = 1
    for value in full_courses.values():
        worksheet.write(row, 0, value.get('course_code'))
        worksheet.write(row, 1, value.get('course_name'))
        worksheet.write(row, 2, value.get('course_description'))
        row += 1

    workbook.close()


if __name__ == '__main__':
    main()
