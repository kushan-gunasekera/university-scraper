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
MAIN_DOMAIN_1 = 'https://catalog.claremontmckenna.edu/content.php?catoid=3&catoid=3&navoid=63&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
MAIN_DOMAIN_2 = 'https://catalog.claremontmckenna.edu/content.php?catoid=4&catoid=4&navoid=88&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
MAIN_DOMAIN_3 = 'https://catalog.claremontmckenna.edu/content.php?catoid=5&catoid=5&navoid=115&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
MAIN_DOMAIN_4 = 'https://catalog.claremontmckenna.edu/content.php?catoid=6&catoid=6&navoid=142&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
MAIN_DOMAIN_5 = 'https://catalog.claremontmckenna.edu/content.php?catoid=10&catoid=10&navoid=334&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
MAIN_DOMAIN_6 = 'https://catalog.claremontmckenna.edu/content.php?catoid=14&catoid=14&navoid=1101&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
MAIN_DOMAIN_7 = 'https://catalog.claremontmckenna.edu/content.php?catoid=17&catoid=17&navoid=1492&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
MAIN_DOMAIN_8 = 'https://catalog.claremontmckenna.edu/content.php?catoid=21&catoid=21&navoid=2247&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
MAIN_DOMAIN_9 = 'https://catalog.claremontmckenna.edu/content.php?catoid=23&catoid=23&navoid=2923&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
MAIN_DOMAIN_10 = 'https://catalog.claremontmckenna.edu/content.php?catoid=25&catoid=25&navoid=3588&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
MAIN_DOMAIN_11 = 'https://catalog.claremontmckenna.edu/content.php?catoid=29&catoid=29&navoid=4499&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
MAIN_DOMAIN_12 = 'https://catalog.claremontmckenna.edu/content.php?catoid=31&catoid=31&navoid=5147&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
MAIN_DOMAIN_13 = 'https://catalog.claremontmckenna.edu/content.php?catoid=36&catoid=36&navoid=7329&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
UNIVERSITY = 'Claremont McKenna College'


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
            url = f'https://catalog.claremontmckenna.edu/{tag.get("href")}'
            print(f'{code} - {url}')
            res = requests.get(url, headers=HEADERS)
            soup = BeautifulSoup(res.content, 'html.parser')
            course_title = soup.find('h1', {'id': 'course_preview_title'})
            description = None
            if course_title:
                # Extract the description by traversing siblings after the title
                description_parts = []
                for sibling in course_title.next_siblings:
                    if sibling.name == 'br' and sibling.find_next_sibling().name == 'br':
                        break
                    if isinstance(sibling, str):
                        description_parts.append(sibling.strip())
                description = ' '.join(description_parts).strip()
            courses[code] = {
                'course_code': code,
                'course_name': tag_split[1],
                'course_description': description,
            }
    return courses


def main():
    full_courses = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_1, page_number) for page_number in range(1, 10)):
            full_courses = {**full_courses, **i.result()}

    with ThreadPoolExecutor(max_workers=10) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_2, page_number) for page_number in range(1, 10)):
            full_courses = {**full_courses, **i.result()}

    with ThreadPoolExecutor(max_workers=10) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_3, page_number) for page_number in range(1, 11)):
            full_courses = {**full_courses, **i.result()}

    with ThreadPoolExecutor(max_workers=10) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_4, page_number) for page_number in range(1, 11)):
            full_courses = {**full_courses, **i.result()}

    with ThreadPoolExecutor(max_workers=10) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_5, page_number) for page_number in range(1, 11)):
            full_courses = {**full_courses, **i.result()}

    with ThreadPoolExecutor(max_workers=10) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_6, page_number) for page_number in range(1, 12)):
            full_courses = {**full_courses, **i.result()}

    with ThreadPoolExecutor(max_workers=10) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_7, page_number) for page_number in range(1, 11)):
            full_courses = {**full_courses, **i.result()}

    with ThreadPoolExecutor(max_workers=10) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_8, page_number) for page_number in range(1, 12)):
            full_courses = {**full_courses, **i.result()}

    with ThreadPoolExecutor(max_workers=10) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_9, page_number) for page_number in range(1, 11)):
            full_courses = {**full_courses, **i.result()}

    with ThreadPoolExecutor(max_workers=10) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_10, page_number) for page_number in range(1, 11)):
            full_courses = {**full_courses, **i.result()}

    with ThreadPoolExecutor(max_workers=10) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_11, page_number) for page_number in range(1, 12)):
            full_courses = {**full_courses, **i.result()}

    with ThreadPoolExecutor(max_workers=10) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_12, page_number) for page_number in range(1, 12)):
            full_courses = {**full_courses, **i.result()}

    with ThreadPoolExecutor(max_workers=10) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_13, page_number) for page_number in range(1, 12)):
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
