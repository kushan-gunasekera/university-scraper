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
MAIN_DOMAIN = 'https://llucatalog.llu.edu'
UNIVERSITY = 'Loma Linda University'


def get_courses():
    r = requests.get(f'{MAIN_DOMAIN}/courses/', headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    course_tags = soup.find_all('a')

    courses = []
    for tag in course_tags:
        url = tag.get('href')
        if not (url and url.startswith('/courses/')):
            continue
        courses.append(url)

    return list(set(courses))


def get_course(url):
    print(url)
    r = requests.get(f'{MAIN_DOMAIN}{url}', headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    course_tags = soup.find_all('div', class_='courseblock')
    # course_tags = soup.find('strong')
    courses = {}
    if not course_tags:
        return courses

    text = None
    try:
        for course_tag in course_tags:
            strong_tags = course_tag.find_all('strong')
            if not strong_tags:
                continue

            course_code, course_name, *_ = strong_tags[0].text.split('. ')
            course_code = course_code.strip().replace('\xa0', ' ')
            courses[course_code] = {
                'course_code': course_code,
                'course_name': course_name.strip().replace('\xa0', ' ')
            }
            desc = course_tag.find('p', class_='courseblockdesc')
            if desc:
                desc = re.sub(r"(Prerequisite:).*", '', desc.text)
                courses[course_code]['course_description'] = desc.strip().replace('\xa0', ' ')

    except Exception as e:
        print(url)
        print(text)
        print(e)
        print()

    return courses


def main():
    # get_course('/courses/span/')
    # return None
    course_urls = get_courses()
    full_courses = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        for i in as_completed(executor.submit(get_course, course_url) for course_url in course_urls):
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
