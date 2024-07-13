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
MAIN_DOMAIN_1 = 'https://catalog.purdue.edu/content.php?catoid=4&catoid=4&navoid=1079&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
MAIN_DOMAIN_2 = 'https://catalog.purdue.edu/content.php?catoid=6&catoid=6&navoid=2099&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
MAIN_DOMAIN_3 = 'https://catalog.purdue.edu/content.php?catoid=7&catoid=7&navoid=2928&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
MAIN_DOMAIN_4 = 'https://catalog.purdue.edu/content.php?catoid=14&catoid=14&navoid=16894&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
MAIN_DOMAIN_5 = 'https://catalog.purdue.edu/content.php?catoid=15&catoid=15&navoid=19001&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
MAIN_DOMAIN_6 = 'https://catalog.purdue.edu/content.php?catoid=16&catoid=16&navoid=20086&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
UNIVERSITY = 'Perdue University'


def get_courses(domain, page_number):
    print(f'page_number: {page_number}')
    r = requests.get(domain.format(page_number=page_number), headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    course_tags = soup.find('table', class_='table_default').find_all('a')

    courses = {}
    for tag in course_tags:
        if not str(tag.get('href')).startswith('preview_course_nopop.php?'):
            continue
        text = tag.text.strip().replace('\xa0', ' ')
        tag_split = text.split(' - ', 1)
        if len(tag_split) == 2:
            code = tag_split[0]
            url = f'https://catalog.purdue.edu/{tag.get("href")}'
            print(f'{code} - {url}')
            res = requests.get(url, headers=HEADERS)
            soup = BeautifulSoup(res.content, 'html.parser')
            course_title = soup.find('h1', {'id': 'course_preview_title'})
            description = None
            if course_title:
                next_hr = course_title.find_next('hr')
                if next_hr:
                    for sibling in next_hr.next_siblings:
                        if not sibling.name and len(sibling) > 1:
                            description = sibling.strip()
                            description = re.sub(r'Credit Hours: \d+.\d+.', '', description).strip()
                            break
            courses[code] = {
                'course_code': code,
                'course_name': tag_split[1],
                'course_description': description,
            }
    return courses


def main():
    # get_courses(5)
    # for page_number in range(1, 52):
    #     get_courses(page_number)
    full_courses = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_1, page_number) for page_number in range(1, 73)):
            full_courses = {**full_courses, **i.result()}

    with ThreadPoolExecutor(max_workers=10) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_2, page_number) for page_number in range(1, 72)):
            full_courses = {**full_courses, **i.result()}

    with ThreadPoolExecutor(max_workers=10) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_3, page_number) for page_number in range(1, 73)):
            full_courses = {**full_courses, **i.result()}

    with ThreadPoolExecutor(max_workers=10) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_4, page_number) for page_number in range(1, 80)):
            full_courses = {**full_courses, **i.result()}

    with ThreadPoolExecutor(max_workers=10) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_5, page_number) for page_number in range(1, 82)):
            full_courses = {**full_courses, **i.result()}

    with ThreadPoolExecutor(max_workers=10) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_6, page_number) for page_number in range(1, 81)):
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
