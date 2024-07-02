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
MAIN_DOMAIN = 'https://www.bu.edu'
UNIVERSITY = 'Boston University'


def get_courses(semester):
    print(f'semester: {semester}')
    r = requests.get(f'{MAIN_DOMAIN}/phpbin/course-search/search.php?page=w0&pagesize=-1&adv=1&nolog=&search_adv_all=&yearsem_adv={semester}&credits=*&pathway=&hub_match=all&pagesize=-1', headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    course_tags = soup.find_all('div', class_='coursearch-result-content')

    courses = {}
    for tag in course_tags:
        heading_tag = tag.find('div', 'coursearch-result-heading')
        description_tag = tag.find('div', 'coursearch-result-content-description')
        course_code = heading_tag.find('h6').text.strip()
        course_name = heading_tag.find('h2').text.strip()
        description = description_tag.text.strip()
        courses[course_code] = {
            'course_code': course_code,
            'course_name': course_name,
            'course_description': description,
        }
    return courses


def main():
    semesters = ['2024SPRG', '2024SUMM']
    full_courses = {}
    with ThreadPoolExecutor(max_workers=1) as executor:
        for i in as_completed(executor.submit(get_courses, semester) for semester in semesters):
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
