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
MAIN_DOMAIN = 'https://catalog.utexas.edu'
UNIVERSITY = 'University of Texas, Austin'


def get_courses():
    # print(f'page_number: {page_number}')
    r = requests.get(f'{MAIN_DOMAIN}/general-information/coursesatoz/', headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    course_tags = soup.find('div', class_='az_sitemap').find_all('a')

    courses = []
    for tag in course_tags:
        href = tag.get('href')
        if not href or '#' in href:
            continue
        # if '#' in href:
        #     continue
        courses.append(href)

    return courses


def get_course(url):
    print(url)
    r = requests.get(f'{MAIN_DOMAIN}{url}', headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    course_tags = soup.find_all('h5')
    courses = {}
    if course_tags:
        for tag in course_tags:
            strong_tags = tag.text.split('. ')
            if len(strong_tags) >= 2:
                desc = ''
                try:
                    desc = tag.next_sibling.next_sibling.text.strip()
                except Exception as error:
                    print(error)
                    print(f'ERROR: {url}')
                course_code = strong_tags[0].strip().replace('\xa0', ' ')
                course_name = strong_tags[1].strip().replace('\xa0', ' ')
                courses[course_code] = {
                    'course_code': course_code,
                    'course_name': course_name,
                    'course_description': desc,
                }

    return courses


def main():
    full_courses = {}
    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_course, url) for url in get_courses()):
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
