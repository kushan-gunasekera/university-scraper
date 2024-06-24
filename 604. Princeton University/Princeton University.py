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
MAIN_DOMAIN = 'https://{sub_domain}.princeton.edu'
UNIVERSITY = 'Princeton University'


def get_description(api_token, term, course_id):
    print(f'get_description --> {term} | {course_id}')
    domain = MAIN_DOMAIN.format(sub_domain='api')
    url = f'{domain}/registrar/course-offerings/1.0.5/course-details?term={term}&course_id={course_id}'
    HEADERS['Authorization'] = f'Bearer {api_token}'
    r = requests.get(url, headers=HEADERS)
    results = r.json().get('course_details', {}).get('course_detail', [])
    description = ''
    if results:
        detail = results[0]
        description = detail.get('description')
    return course_id, description


def get_course(api_token, term):
    print(f'get_course --> {term}')
    domain = MAIN_DOMAIN.format(sub_domain='api')
    HEADERS['Authorization'] = f'Bearer {api_token}'
    r = requests.get(f'{domain}/registrar/course-offerings/1.0.5/classes/{term}', headers=HEADERS)
    courses = {}
    results = r.json().get('classes', {}).get('class', [])
    if not results:
        print(f'No results | {term}')
        return courses

    print(f'results: {len(results)} | {term}')
    for result in results:
        courses[result['course_id']] = {
            'course_code': result['crosslistings'],
            'course_name': result['long_title'],
            'course_description': None
        }

    print(f'{len(courses)} courses in {term}')
    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_description, api_token, term, course_id) for course_id in courses.keys()):
            course_id, description = i.result()
            courses[course_id]['course_description'] = description

    return courses


def get_terms():
    domain = MAIN_DOMAIN.format(sub_domain='registrar')
    r = requests.get(f'{domain}/course-offerings', headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')

    script_tag = soup.find('script', {'type': 'application/json', 'data-drupal-selector': 'drupal-settings-json'})
    json_data = json.loads(script_tag.string)
    api_token = json_data["ps_registrar"]["apiToken"]
    terms = [i.get('code') for i in json_data["ps_registrar"]["terms"]]
    return api_token, terms


def main():
    api_token, terms = get_terms()
    full_courses = {}
    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_course, api_token, term) for term in terms):
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
