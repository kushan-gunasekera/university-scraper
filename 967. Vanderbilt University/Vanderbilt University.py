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
# MAIN_DOMAIN = 'https://vanderbilt.kuali.co/'
UNIVERSITY = 'Vanderbilt University'


def get_courses():
    # print(f'page_number: {page_number}')
    r = requests.get('https://vanderbilt.kuali.co/api/v1/catalog/courses/6480a5d766356a001ce54ecf?q=', headers=HEADERS)

    courses = {}
    for i in r.json():
        courses[i.get('__catalogCourseId')] = {
            'course_code': i.get('__catalogCourseId'),
            'course_name': i.get('title'),
            'course_description': i.get('subjectCode', {}).get('description'),
        }

    return courses


def main():
    full_courses = get_courses()

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
