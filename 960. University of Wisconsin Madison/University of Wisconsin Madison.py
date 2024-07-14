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
import urllib.parse

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
MAIN_DOMAIN = 'https://public.enroll.wisc.edu'
UNIVERSITY = 'University of Wisconsin Madison'


def get_courses():
    data = {"selectedTerm":"0000","queryString":"*","filters":[],"pageSize":1000,"sortOrder":"SCORE"}
    page = 1
    courses = {}
    while True:
        data['page'] = page
        r = requests.post(f'{MAIN_DOMAIN}/api/search/v1', headers=HEADERS, json=data)
        if r.status_code != 200:
            print(f'{r.status_code} for {page}')
            break
        results = r.json().get('hits', [])
        if not results:
            print(f'No results | {page}')
            return courses

        print(f'results: {len(results)} | {page}')
        for result in results:
            courses[result['courseDesignation']] = {
                'course_code': result['courseDesignation'],
                'course_name': result['title'],
                'course_description': result.get('description')
            }
        page += 1

    print(f'{len(courses)} courses')
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
