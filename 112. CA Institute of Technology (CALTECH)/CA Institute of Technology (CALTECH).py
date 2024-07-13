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
MAIN_DOMAIN = 'https://www.catalog.caltech.edu'
UNIVERSITY = 'CA Institute of Technology (CALTECH)'


def get_courses():
    r = requests.get(f'{MAIN_DOMAIN}/current/2023-24/', headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    course_tags = soup.find_all('li', class_='sidebar-menu-block__level-2__item d-flex flex-column menu-item')[4].find('ul').find_all('li')

    courses = []
    for tag in course_tags:
        a_tag = tag.find('a')
        if not a_tag.get('href'):
            continue
        courses.append(a_tag['href'])
    return courses


def get_course(url):
    print(url)
    r = requests.get(f'{MAIN_DOMAIN}{url}', headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    div_tags = soup.find_all('div', class_='course-description2')
    courses = {}
    if not div_tags:
        return courses

    for tag in div_tags:
        code = tag.find('div', class_='course-description2__label').text.strip()
        title = tag.find('h2', class_='course-description2__title').text.strip()
        desc = None
        try:
            desc = tag.find('div', class_='course-description2__description course-description2__general-text').text.strip()
        except:
            pass
        instructors = None
        try:
            instructors = tag.find('div', class_='course-description2__instructors course-description2__general-text').text
            instructors = instructors.replace('Instructors:', '').strip()
        except:
            pass
        courses[code] = {
            'course_code': code,
            'course_name': title,
            'course_description': desc,
            'course_professor': instructors,
        }
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
