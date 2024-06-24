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
MAIN_DOMAIN = 'https://dartmouth.smartcatalogiq.com'
UNIVERSITY = 'Dartmouth College'


def get_courses():
    r = requests.get(f'{MAIN_DOMAIN}/Institutions/Dartmouth/json/Current/orc.json', headers=HEADERS)
    return r.json()


def get_h1(url):
    r = requests.get(f'{MAIN_DOMAIN}{url}'.lower(), headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    h1_tag = soup.find('h1')
    return h1_tag.text.strip()


def get_description(course_code, url):
    print(f'get_description --> {course_code} | {url}')
    description = ''
    r = requests.get(f'{MAIN_DOMAIN}{url}'.lower(), headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    description_tags = soup.find('div', class_='desc')
    if description_tags:
        description = description_tags.text.replace('\n', '')
    return description


def get_course(count, url):
    print(f'{count} --> {url}')
    r = requests.get(f'{MAIN_DOMAIN}{url}'.lower(), headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    course_tags = soup.find('ul', class_='sc-child-item-links')
    courses = {}
    if not course_tags:
        return courses

    a_tags = course_tags.find_all('a')
    if not a_tags:
        return courses

    descriptions = []
    for tag in a_tags:
        parts = tag.text.replace('\xa0', ' ').split(' ', 2)
        if len(parts) != 3:
            parts = get_h1(tag.get('href')).replace('\xa0', ' ').split(' ', 2)
        course_code = f'{parts[0].strip()} {parts[1].strip()}'
        course_name = parts[2].strip()
        courses[course_code] = {
            'course_code': course_code,
            'course_name': course_name,
        }
        descriptions.append([course_code, tag.get('href')])

    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_description, code, url) for code, url in descriptions):
            code, description = i.result()
            courses[code]['course_description'] = description
    return courses


def get_paths(data):
    paths = []
    if "Path" in data:
        paths.append(data["Path"])
    if "Children" in data:
        for child in data["Children"]:
            paths.extend(get_paths(child))
    return paths


def main():
    get_course(0, '/Current/orc/Departments-Programs-Undergraduate/African-and-African-American-Studies/AAAS-African-and-African-American-Studies')
    paths = get_paths(get_courses())
    full_courses = {}
    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_course, count, path) for count, path in enumerate(paths)):
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
