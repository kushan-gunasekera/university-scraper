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
MAIN_DOMAIN = 'https://e-catalogue.jhu.edu'
UNIVERSITY = 'Johns Hopkins University'


def get_course(character):
    print(character)
    # HEADERS['Referer'] = 'https://courses.yale.edu/?srcdb=201602&stat=A'
    data = {"other":{"srcdb":"2023"},"criteria":[{"field":"keyword","value":character}]}
    # HEADERS['Referer'] = f'{MAIN_DOMAIN}/?srcdb={url}&stat=A'
    r = requests.post(f'{MAIN_DOMAIN}/course-search/api/?page=fose&route=search&keyword={character}', headers=HEADERS, data=urllib.parse.quote_plus(json.dumps(data, separators=(',', ':'))))
    courses = {}
    results = r.json().get('results', [])
    if not results:
        print(f'No results | {character}')
        return courses

    print(f'results: {len(results)} | {character}')
    for result in results:
        courses[result['code']] = result['title']

    print(f'{len(courses)} courses in {character}')
    return courses


def main():
    # get_courses()
    # get_course('999999')
    # course_urls = get_courses()
    full_courses = {}
    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_course, character) for character in [chr(ord('a') + i) for i in range(26)]):
            full_courses = {**full_courses, **i.result()}

    with open(f'{UNIVERSITY}.json', 'w') as json_file:
        json.dump(full_courses, json_file, indent=4)

    header = ['course_code', 'course_name']
    workbook = xlsxwriter.Workbook(f'{UNIVERSITY}.xlsx')
    worksheet = workbook.add_worksheet()
    for col, header_name in enumerate(header):
        worksheet.write(0, col, header_name)

    row = 1
    for course_code, course_name in full_courses.items():
        worksheet.write(row, 0, course_code.split('|')[0])
        # worksheet.write(row, 0, course_code)
        worksheet.write(row, 1, course_name)
        row += 1

    workbook.close()


if __name__ == '__main__':
    main()
