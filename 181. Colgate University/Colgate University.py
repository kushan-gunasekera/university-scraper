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
MAIN_DOMAIN = 'https://api.colgate.edu'
UNIVERSITY = 'Colgate University'


def get_terms():
    r = requests.get(f'{MAIN_DOMAIN}/v1/courses/search/terms', headers=HEADERS)
    return [i.get('TERM_CODE') for i in r.json()]


def get_courses(term):
    print(f'term: {term}')
    url = f'{MAIN_DOMAIN}/v1/courses/search?keyword=&termCode={term}&coreArea=&inquiryArea=&liberalArtsPracticeArea=&meetTimeMorning=&meetTimeAfternoon=&meetTimeEvening=&openCoursesOnly='
    r = requests.get(url, headers=HEADERS)
    courses = {}
    for i in r.json():
        code = i.get('DISPLAY_KEY')
        term_code = i.get('TERM_CODE')
        crn = i.get('CRN')
        url = f'{MAIN_DOMAIN}/v1/courses/{term_code}/{crn}'
        print(f'code: {code} | url: {url}')
        res = requests.get(url, headers=HEADERS)
        details = res.json() or []
        desc = None
        if details:
            if details[0]['DESCRIPTION']:
                soup = BeautifulSoup(details[0]['DESCRIPTION'], 'html.parser')
                original_text = soup.text
                a_tag = soup.find('a')
                if a_tag:
                    a_text = soup.find('a').text
                    desc = original_text.replace(a_text, '').strip().replace('\n', ' ')
                else:
                    desc = original_text
        courses[code] = {
            'course_code': code,
            'course_name': i.get('TITLE'),
            'course_description': desc,
            'course_professor': i.get('INSTRUCTOR1_NAME'),
        }
    return courses


def main():
    full_courses = {}
    terms = get_terms()

    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_courses, term) for term in terms):
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
