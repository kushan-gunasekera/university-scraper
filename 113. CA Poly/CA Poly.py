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
MAIN_DOMAIN = 'https://catalog.calpoly.edu'
UNIVERSITY = 'CA Poly'


def get_courses():
    # print(f'page_number: {page_number}')
    r = requests.get(f'{MAIN_DOMAIN}/coursesaz/', headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    course_tags = soup.find('table').find_all('a')

    courses = []
    for tag in course_tags:
        courses.append(tag.get('href'))

    return courses


def get_course(url):
    courses = {}
    if not url:
        return courses
    print(url)
    r = requests.get(f'{MAIN_DOMAIN}{url}', headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    course_tags = soup.find_all('strong')
    if not course_tags:
        print(f'No courses | {url}')
        return courses

    text = None
    try:
        for tag in course_tags:
            text = tag.text
            parts = text.split(".", 1)

            if len(parts) != 2:
                continue

            course_code = parts[0].strip()
            course_name = parts[1].strip()
            courses[f'{course_code}|{url}'] = course_name
    except Exception as error:
        print(f'{text} | {url}')
        raise Exception(error)

    print(f'{len(courses)} | {url}')
    return courses


def main():
    full_courses = {}
    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_course, url) for url in get_courses()):
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
