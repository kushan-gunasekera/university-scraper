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
MAIN_DOMAIN_1 = 'https://catalog.wm.edu/content.php?catoid=2&catoid=2&navoid=14&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
MAIN_DOMAIN_2 = 'https://catalog.wm.edu/content.php?catoid=1&catoid=1&navoid=6&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
MAIN_DOMAIN_3 = 'https://catalog.wm.edu/content.php?catoid=6&catoid=6&navoid=882&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
MAIN_DOMAIN_4 = 'https://catalog.wm.edu/content.php?catoid=5&catoid=5&navoid=686&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
MAIN_DOMAIN_5 = 'https://catalog.wm.edu/content.php?catoid=8&catoid=8&navoid=1293&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
MAIN_DOMAIN_6 = 'https://catalog.wm.edu/content.php?catoid=7&catoid=7&navoid=1098&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
MAIN_DOMAIN_7 = 'https://catalog.wm.edu/content.php?catoid=11&catoid=11&navoid=2065&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
MAIN_DOMAIN_8 = 'https://catalog.wm.edu/content.php?catoid=12&catoid=12&navoid=2255&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
MAIN_DOMAIN_9 = 'https://catalog.wm.edu/content.php?catoid=14&catoid=14&navoid=2576&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
MAIN_DOMAIN_10 = 'https://catalog.wm.edu/content.php?catoid=13&catoid=13&navoid=2386&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
MAIN_DOMAIN_11 = 'https://catalog.wm.edu/content.php?catoid=16&catoid=16&navoid=2841&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
MAIN_DOMAIN_12 = 'https://catalog.wm.edu/content.php?catoid=15&catoid=15&navoid=2652&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
MAIN_DOMAIN_13 = 'https://catalog.wm.edu/content.php?catoid=18&catoid=18&navoid=3204&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
MAIN_DOMAIN_14 = 'https://catalog.wm.edu/content.php?catoid=17&catoid=17&navoid=3043&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
MAIN_DOMAIN_15 = 'https://catalog.wm.edu/content.php?catoid=20&catoid=20&navoid=3461&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
MAIN_DOMAIN_16 = 'https://catalog.wm.edu/content.php?catoid=19&catoid=19&navoid=3302&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
MAIN_DOMAIN_17 = 'https://catalog.wm.edu/content.php?catoid=23&catoid=23&navoid=3799&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
MAIN_DOMAIN_18 = 'https://catalog.wm.edu/content.php?catoid=22&catoid=22&navoid=3646&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
MAIN_DOMAIN_19 = 'https://catalog.wm.edu/content.php?catoid=25&catoid=25&navoid=4064&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
MAIN_DOMAIN_20 = 'https://catalog.wm.edu/content.php?catoid=24&catoid=24&navoid=3902&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
MAIN_DOMAIN_21 = 'https://catalog.wm.edu/content.php?catoid=27&catoid=27&navoid=4321&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
MAIN_DOMAIN_22 = 'https://catalog.wm.edu/content.php?catoid=26&catoid=26&navoid=4161&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
MAIN_DOMAIN_23 = 'https://catalog.wm.edu/content.php?catoid=29&catoid=29&navoid=4590&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
MAIN_DOMAIN_24 = 'https://catalog.wm.edu/content.php?catoid=28&catoid=28&navoid=4434&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
UNIVERSITY = 'William & Mary'


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
            courses[tag_split[0]] = tag_split[1]
    return courses


def main():
    # get_courses(5)
    # for page_number in range(1, 52):
    #     get_courses(page_number)
    full_courses = {}
    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_1, page_number) for page_number in range(1, 13)):
            full_courses = {**full_courses, **i.result()}

    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_2, page_number) for page_number in range(1, 21)):
            full_courses = {**full_courses, **i.result()}

    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_3, page_number) for page_number in range(1, 13)):
            full_courses = {**full_courses, **i.result()}

    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_4, page_number) for page_number in range(1, 22)):
            full_courses = {**full_courses, **i.result()}

    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_5, page_number) for page_number in range(1, 14)):
            full_courses = {**full_courses, **i.result()}

    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_6, page_number) for page_number in range(1, 22)):
            full_courses = {**full_courses, **i.result()}

    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_7, page_number) for page_number in range(1, 14)):
            full_courses = {**full_courses, **i.result()}

    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_8, page_number) for page_number in range(1, 23)):
            full_courses = {**full_courses, **i.result()}

    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_9, page_number) for page_number in range(1, 14)):
            full_courses = {**full_courses, **i.result()}

    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_10, page_number) for page_number in range(1, 23)):
            full_courses = {**full_courses, **i.result()}

    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_11, page_number) for page_number in range(1, 13)):
            full_courses = {**full_courses, **i.result()}

    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_12, page_number) for page_number in range(1, 24)):
            full_courses = {**full_courses, **i.result()}

    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_13, page_number) for page_number in range(1, 13)):
            full_courses = {**full_courses, **i.result()}

    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_14, page_number) for page_number in range(1, 25)):
            full_courses = {**full_courses, **i.result()}

    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_15, page_number) for page_number in range(1, 12)):
            full_courses = {**full_courses, **i.result()}

    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_16, page_number) for page_number in range(1, 25)):
            full_courses = {**full_courses, **i.result()}

    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_17, page_number) for page_number in range(1, 13)):
            full_courses = {**full_courses, **i.result()}

    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_18, page_number) for page_number in range(1, 25)):
            full_courses = {**full_courses, **i.result()}

    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_19, page_number) for page_number in range(1, 13)):
            full_courses = {**full_courses, **i.result()}

    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_20, page_number) for page_number in range(1, 26)):
            full_courses = {**full_courses, **i.result()}

    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_21, page_number) for page_number in range(1, 13)):
            full_courses = {**full_courses, **i.result()}

    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_22, page_number) for page_number in range(1, 27)):
            full_courses = {**full_courses, **i.result()}

    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_23, page_number) for page_number in range(1, 13)):
            full_courses = {**full_courses, **i.result()}

    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_24, page_number) for page_number in range(1, 27)):
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
