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
import xmltodict

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
MAIN_DOMAIN = 'https://catalog.barnard.edu'
UNIVERSITY = 'Barnard College'


def get_course():
    data = {"department":"","term":"","level":"","held":"","begin":"","end":"","pl":"0","ph":"10","keywords":"","college":"BC"}
    criteria = urllib.parse.quote_plus(json.dumps(data, separators=(',', ':')))
    r = requests.get(f'{MAIN_DOMAIN}/ribbit/index.cgi?page=shared-scopo-search.rjs&criteria={criteria}', headers=HEADERS)
    courses = {}
    for i in xmltodict.parse(r.content).get('results').get('result'):
        code = i['code']
        title = i['title']
        print(f'code: {code} | title: {title}')
        soup = BeautifulSoup(i['description'], 'html.parser')
        desc = soup.find('p', 'courseblockdesc').text
        instructors = []
        if len(soup.find_all('tr')) > 2:
            for j in soup.find_all('tr')[2:]:
                try:
                    instructors.append(j.find_all('td')[3].text)
                except:
                    pass
        courses[code] = {
            'course_code': code,
            'course_name': title,
            'course_description': desc,
            'course_professor': ', '.join(list(set(instructors))),
        }

    return courses


def main():
    full_courses = get_course()

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
