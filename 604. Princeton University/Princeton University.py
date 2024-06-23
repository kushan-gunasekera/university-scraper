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


def get_courses():
    domain = MAIN_DOMAIN.format(sub_domain='registrar')
    r = requests.get(f'{domain}/course-offerings?term=1244', headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    course_tags = soup.find('select', id='cs-term').find_all('option')

    courses = []
    for tag in course_tags:
        url = tag.get('value')
        # if not (url and url.startswith('/courses-az/')):
        #     continue
        courses.append(url)

    return list(set(courses))


def get_course(url):
    print(url)
    domain = MAIN_DOMAIN.format(sub_domain='api')
    # HEADERS['Referer'] = 'https://courses.yale.edu/?srcdb=201602&stat=A'
    # data = {"other":{"srcdb":url},"criteria":[{"field":"stat","value":"A"}]}
    HEADERS['Authorization'] = 'Bearer ZGRmM2M0MTAtMDU0OC0zOWE2LWExMzgtZjliZWZmZDZkNWQ3OnJlZ2lzdHJhcmFwaUBjYXJib24uc3VwZXI='
    r = requests.get(f'{domain}/registrar/course-offerings/1.0.5/classes/{url}', headers=HEADERS)
    courses = {}
    results = r.json().get('classes', {}).get('class', [])
    if not results:
        print(f'No results | {url}')
        return courses

    print(f'results: {len(results)} | {url}')
    for result in results:
        courses[result['crosslistings']] = result['long_title']

    print(f'{len(courses)} courses in {url}')
    return courses


def get_terms():
    domain = MAIN_DOMAIN.format(sub_domain='registrar')
    r = requests.get(f'{domain}/course-offerings', headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    term_tags = soup.find('select', id='cs-term')

    terms = []
    for tag in term_tags:
        url = tag.get('value')
        terms.append(url)

    return list(set(terms))


def main():
    # get_courses()
    # get_course('202403')
    # course_urls = get_courses()
    # course_urls = [1252, 1244, 1242, 1234, 1232, 1224, 1222]
    course_urls = get_terms()
    full_courses = {}
    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_course, course_url) for course_url in course_urls):
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
