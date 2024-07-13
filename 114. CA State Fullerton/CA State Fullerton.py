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
MAIN_DOMAIN = 'https://catalog.fullerton.edu/content.php?catoid=91&catoid=91&navoid=13418&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
UNIVERSITY = 'CA State Fullerton'


def get_courses(page_number):
    print(f'page_number: {page_number}')
    r = requests.get(MAIN_DOMAIN.format(page_number=page_number), headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    course_tags = soup.find('table', class_='table_default').find_all('a')

    courses = {}
    for tag in course_tags:
        text = tag.text.strip().replace('\xa0', ' ')
        tag_split = text.split(' - ', 1)
        path = tag.get('href')
        if len(tag_split) == 2 and path.startswith('preview_course_nopop.php'):
            code = tag_split[0]
            url = f'https://catalog.fullerton.edu/{path}'
            print(f'{code} - {url}')
            res = requests.get(url, headers=HEADERS)
            soup = BeautifulSoup(res.content, 'html.parser')
            course_title = soup.find('h1', {'id': 'course_preview_title'})
            description = None
            if course_title:
                next_hr = course_title.find_next('hr')
                if next_hr:
                    # Extract text between the first <hr> and the next <br> or <hr> tag
                    description_parts = []
                    for sibling in next_hr.next_siblings:
                        if sibling.name == 'br' or sibling.name == 'hr':
                            break
                        if isinstance(sibling, str):
                            description_parts.append(sibling.strip())
                    description = ' '.join(description_parts)

            courses[code] = {
                'course_code': code,
                'course_name': tag_split[1],
                'course_description': description,
            }

    return courses


def main():
    full_courses = {}
    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_courses, page_number) for page_number in range(1, 40)):
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
