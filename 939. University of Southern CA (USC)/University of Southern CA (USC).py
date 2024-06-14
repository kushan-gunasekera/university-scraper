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
MAIN_DOMAIN = 'https://catalogue.usc.edu'
UNIVERSITY = 'University of Southern CA (USC)'


def get_description(page_number, course_code, url):
    print(f'{page_number} | {course_code} | {url}')
    description = ''
    r = requests.get(f'{MAIN_DOMAIN}/{url}', headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    desc = soup.find('td', class_='block_content')
    if not desc:
        return {'course_code': course_code, 'description': description}
    title = soup.find('h1', id='course_preview_title')
    desc = desc.text.replace('\n', '').replace('\xa0', ' ')
    if not title:
        return {'course_code': course_code, 'description': desc}
    title = title.text.strip()
    desc = desc.split(title)[-1].strip()
    return {'course_code': course_code, 'description': desc}


def get_courses(domain, page_number):
    print(f'page_number: {page_number}')
    r = requests.get(domain.format(page_number=page_number), headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    course_tags = soup.find_all('table', class_='table_default')[6].find_all('a')

    courses = {}
    descriptions = []
    for tag in course_tags:
        text = tag.text.strip().split(' ', 2)
        if len(text) == 3 and text[0].isupper():
            course_code = f'{text[0]} {text[1]}'
            courses[course_code] = {
                'course_code': course_code,
                'course_name': text[2],
            }
            descriptions.append([course_code, tag['href']])
        else:
            print(tag.text)

    with ThreadPoolExecutor(max_workers=3) as executor:
        for i in as_completed(executor.submit(get_description, page_number, c_code, path) for c_code, path in descriptions):
            result = i.result()
            courses[result.get('course_code')]['course_description'] = result.get('description')

    if len(courses) != 100:
        print(f'page_number: {page_number} | count: {len(courses)}')
    return courses


def main():
    full_courses = {}
    domain = 'https://catalogue.usc.edu/content.php?catoid=18&catoid=18&navoid=7395&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
    with ThreadPoolExecutor(max_workers=3) as executor:
        for i in as_completed(executor.submit(get_courses, domain, page_number) for page_number in range(1, 128)):
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
