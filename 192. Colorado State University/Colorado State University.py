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
MAIN_DOMAIN = 'https://catalog.colostate.edu'
UNIVERSITY = 'Colorado State University'


def get_courses():
    r = requests.get(f'{MAIN_DOMAIN}/general-catalog/courses-az/', headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    course_tags = soup.find('div', id='atozindex').find_all('a')

    courses = []
    for tag in course_tags:
        if not tag.get('href') or tag.get('href').startswith('#') or not tag.get('href').startswith('/general-catalog'):
            continue
        courses.append(tag['href'])
    return courses


def get_course(url):
    print(url)
    r = requests.get(f'{MAIN_DOMAIN}{url}', headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    div_tags = soup.find_all('div', class_='courseblock')
    courses = {}
    if not div_tags:
        return courses

    for tag in div_tags:
        desc = None
        try:
            desc = tag.find('p', 'courseblockdesc').find('strong').next_sibling.text.replace('\xa0', ' ').strip()
        except:
            pass
        try:
            strong_tags = tag.find('p', 'courseblocktitle').find('strong')
            course_code, course_name = strong_tags.text.strip().replace('\xa0', ' ').split('–', 1)
            courses[course_code.strip()] = {
                'course_code': course_code.strip(),
                'course_name': course_name.strip(),
                'course_description': desc,
            }
        except:
            pass
    return courses


def main():
    full_courses = {}
    urls = get_courses()

    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_course, url) for url in urls):
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
