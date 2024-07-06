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
MAIN_DOMAIN = 'https://courses.rice.edu'
UNIVERSITY = 'Rice University'


def get_courses():
    r = requests.get(f'{MAIN_DOMAIN}/courses/!SWKSCAT.cat?p_action=CATALIST&p_acyr_code=2025', headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    course_tags = soup.find('table', class_='table table-condensed').find_all('td', class_='cataCourse')

    courses = []
    for tag in course_tags:
        tag = tag.find('a')
        if not tag.get('href') or tag.get('href').startswith('#'):
            continue
        courses.append(tag['href'])
    return courses


def get_course(url):
    print(url)
    r = requests.get(f'{MAIN_DOMAIN}{url}', headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    h3_tags = soup.find('div', class_='col-lg-12 course').find('h3')
    course_code, course_name = h3_tags.text.strip().replace('\xa0', ' ').split(' - ', 1)
    desc = soup.find('div', class_='col-lg-12 course').find_all('div')[-1].get_text(strip=True).replace('Description:', '')
    return {
        course_code: {
            'course_code': course_code,
            'course_name': course_name,
            'course_description': desc,
        }
    }


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
