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
MAIN_DOMAIN = 'http://catalog.csulb.edu'
UNIVERSITY = 'CA State Long Beach'


def get_description(page_number, course_code, url):
    print(f'{page_number} | {course_code} | {url}')
    description = ''
    url = f'{MAIN_DOMAIN}/{url}'
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    desc = soup.find('td', class_='block_content')
    if not desc:
        return {'course_code': course_code, 'description': description}
    try:
        description = desc.find('p').text.replace(soup.find('h1').text, '').split(')', 1)[-1].strip()
        return {'course_code': course_code, 'description': description}
    except Exception as error:
        print(f'ERROR: {url} | {error}')
        return {'course_code': course_code, 'description': description}


def get_courses(domain, page_number=None):
    # print(f'page_number: {page_number}')
    if not page_number:
        r = requests.get(domain, headers=HEADERS)
    else:
        r = requests.get(domain.format(page_number=page_number), headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    course_tags = soup.find('table', class_='table_default').find_all('a')

    courses = {}
    descriptions = []
    for tag in course_tags:
        text = tag.text.strip().replace('\xa0', ' ')
        # print(str(tag.text))
        # print(str(tag.text).split(' - '))
        tag_split = text.split(' - ', 1)
        # print(f'{len(tag_split)} | {text}')

        desc = None

        if len(tag_split) == 2:
            courses[tag_split[0]] = {
                'course_code': tag_split[0],
                'course_name': tag_split[1],
                'course_description': desc,
            }
            descriptions.append([tag_split[0], tag['href']])
        # else:
        #     tag_split
    # print(f'{len(course_tags)} | {len(courses)} | {page_number} | {domain}')
    with ThreadPoolExecutor(max_workers=1) as executor:
        for i in as_completed(executor.submit(get_description, page_number, c_code, path) for c_code, path in descriptions):
            result = i.result()
            courses[result.get('course_code')]['course_description'] = result.get('description')
    return courses


def main():
    # get_courses(5)
    # for page_number in range(1, 52):
    #     get_courses(page_number)
    full_courses = {}

    # domain = ''
    # full_courses = {**full_courses, **get_courses(domain)}
    #
    # domain = ''
    # full_courses = {**full_courses, **get_courses(domain)}

    domain = 'http://catalog.csulb.edu/content.php?catoid=1&catoid=1&navoid=23&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_courses, domain, page_number) for page_number in range(1, 58)):
            full_courses = {**full_courses, **i.result()}

    domain = 'http://catalog.csulb.edu/content.php?catoid=2&catoid=2&navoid=37&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_courses, domain, page_number) for page_number in range(1, 59)):
            full_courses = {**full_courses, **i.result()}

    domain = 'http://catalog.csulb.edu/content.php?catoid=3&catoid=3&navoid=152&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_courses, domain, page_number) for page_number in range(1, 59)):
            full_courses = {**full_courses, **i.result()}

    domain = 'http://catalog.csulb.edu/content.php?catoid=5&catoid=5&navoid=374&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_courses, domain, page_number) for page_number in range(1, 59)):
            full_courses = {**full_courses, **i.result()}

    domain = 'http://catalog.csulb.edu/content.php?catoid=6&catoid=6&navoid=642&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_courses, domain, page_number) for page_number in range(1, 59)):
            full_courses = {**full_courses, **i.result()}

    domain = 'http://catalog.csulb.edu/content.php?catoid=7&catoid=7&navoid=773&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_courses, domain, page_number) for page_number in range(1, 59)):
            full_courses = {**full_courses, **i.result()}

    domain = 'http://catalog.csulb.edu/content.php?catoid=8&catoid=8&navoid=903&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_courses, domain, page_number) for page_number in range(1, 61)):
            full_courses = {**full_courses, **i.result()}

    domain = 'http://catalog.csulb.edu/content.php?catoid=10&catoid=10&navoid=1156&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_courses, domain, page_number) for page_number in range(1, 61)):
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
