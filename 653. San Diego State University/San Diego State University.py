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
MAIN_DOMAIN = 'https://catalog.sdsu.edu'
SUB_DOMAIN = 'https://catalog.sdsu.edu/content.php?catoid=9&catoid=9&navoid=776&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
UNIVERSITY = 'San Diego State University'


def get_description(page_number, course_code, url):
    print(f'{page_number} | {course_code} | {url}')
    description = ''
    r = requests.get(f'{MAIN_DOMAIN}/{url}', headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    desc = soup.find('td', class_='block_content')
    if not desc:
        return {'course_code': course_code, 'description': description}
    desc = desc.find_all('p')
    if not desc:
        return {'course_code': course_code, 'description': description}
    return {'course_code': course_code, 'description': desc[0].text}


def get_courses(page_number):
    print(f'page_number: {page_number}')
    r = requests.get(SUB_DOMAIN.format(page_number=page_number), headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    course_tags = soup.find('table', class_='table_default').find_all('a')

    courses = {}
    descriptions = []
    for tag in course_tags:
        text = tag.text.strip().replace('\xa0', ' ')
        tag_split = text.split(' - ', 1)
        if len(tag_split) == 2:
            course_code = tag_split[0]
            courses[course_code] = {
                'course_code': course_code,
                'course_name': tag_split[1],
            }
            descriptions.append([course_code, tag['href']])
    with ThreadPoolExecutor(max_workers=10) as executor:
        for i in as_completed(executor.submit(get_description, page_number, c_code, path) for c_code, path in descriptions):
            result = i.result()
            courses[result.get('course_code')]['course_description'] = result.get('description')
    return courses


def main():
    full_courses = {}
    with ThreadPoolExecutor(max_workers=5) as executor:
        for i in as_completed(executor.submit(get_courses, page_number) for page_number in range(1, 52)):
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
