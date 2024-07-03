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
MAIN_DOMAIN = 'https://guide.berkeley.edu'
UNIVERSITY = 'University of CA Berkeley'


def get_courses():
    r = requests.get(f'{MAIN_DOMAIN}/courses/', headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    course_tags = soup.find('div', id='atozindex').find_all('a')

    courses = []
    for tag in course_tags:
        if not tag.get('href'):
            continue
        courses.append(tag['href'])
    return courses


def get_course(url):
    print(url)
    r = requests.get(f'{MAIN_DOMAIN}{url}', headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    course_tags = soup.find_all('div', class_='courseblock')
    # h3_tags = soup.find_all('h3', class_='courseblocktitle')
    courses = {}
    if not course_tags:
        return courses

    for tag in course_tags:
        h3_tag = tag.find('h3', class_='courseblocktitle')
        span_tags = h3_tag.find_all('span')

        course_code = span_tags[0].text.strip().replace('\xa0', ' ')
        course_name = span_tags[1].text.strip().replace('\xa0', ' ')

        span = tag.find('span', class_='descshow')
        text_after_br = ''
        if span:
            br_tag = span.find('br')
            if br_tag:
                # The text after the <br> tag
                text_after_br = br_tag.next_sibling.strip()
        courses[course_code] = {
            'course_code': course_code,
            'course_name': course_name,
            'course_description': text_after_br
        }
        try:
            courses[course_code]['course_professor'] = tag.find_all('div', class_='course-section')[-1].find_all('p')[-1].text.split(':')[-1].strip()
        except Exception as error:
            print(error)

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
        row += 1

    workbook.close()


if __name__ == '__main__':
    main()
