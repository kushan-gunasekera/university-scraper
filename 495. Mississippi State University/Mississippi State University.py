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

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
MAIN_DOMAIN = 'https://www.catalog.msstate.edu'
UNIVERSITY = 'Mississippi State University'


def get_courses(catalog_type):
    r = requests.get(f'{MAIN_DOMAIN}/{catalog_type}/azindex/', headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    course_tags = soup.find('div', class_='az_sitemap').find_all('a')

    courses = []
    for tag in course_tags:
        href = tag.get('href')
        if not href or (href and (href.startswith('#') or href.endswith('azindex/'))):
            continue
        courses.append(tag.get('href'))

    return courses


def get_course(url):
    print(f'get_course: {url}')
    courses = {}
    break_values = ('Prerequisite', 'Grade Mode', 'Repeat Rule')
    r = requests.get(f'{MAIN_DOMAIN}{url}', headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    search_urls = []
    for i in soup.find_all('a'):
        href = i.get('href')
        if href and href.startswith('/search/'):
            search_urls.append(i.get('href'))
    search_urls = list(set(search_urls))

    for i in search_urls:
        r = requests.get(f'{MAIN_DOMAIN}{i}', headers=HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')
        course_tags = soup.find('div', id='fssearchresults')
        if not course_tags:
            continue
        for j in course_tags.find_all('article'):
            courseblock = j.find('div', class_='courseblock')
            if not courseblock:
                continue
            h3_tag = j.find('h3')
            code, title, *_ = h3_tag.text.strip().replace('\xa0', ' ').split('  ')
            desc = None
            try:
                desc = j.find('p',  class_='courseblockdesc').text.strip().replace('\xa0', ' ')
            except:
                pass
            courses[code] = {
                'course_code': code,
                'course_name': title,
                'course_description': desc,
                # 'course_professor': professors,
            }

    return courses


def main():
    all_courses = []
    all_courses.extend(get_courses('graduate'))
    all_courses.extend(get_courses('undergraduate'))

    full_courses = {}
    with ThreadPoolExecutor(max_workers=1) as executor:
        for i in as_completed(executor.submit(get_course, url) for url in all_courses):
            full_courses = {**full_courses, **i.result()}

    with open(f'{UNIVERSITY}.json', 'w') as json_file:
        json.dump(full_courses, json_file, indent=4)

    header = [
        'course_code', 'course_name', 'course_description', 'course_professor'
    ]
    workbook = xlsxwriter.Workbook(f'{UNIVERSITY}.xlsx')
    worksheet = workbook.add_worksheet()
    for col, header_name in enumerate(header):
        worksheet.write(0, col, header_name)

    row = 1
    for value in full_courses.values():
        worksheet.write(row, 0, value.get('course_code'))
        worksheet.write(row, 1, value.get('course_name'))
        worksheet.write(row, 2, value.get('course_description'))
        worksheet.write(row, 3, value.get('course_professor'))
        row += 1

    workbook.close()


if __name__ == '__main__':
    main()
