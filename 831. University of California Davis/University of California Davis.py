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
MAIN_DOMAIN = 'https://catalog.ucdavis.edu'
UNIVERSITY = 'University of California Davis'


def get_description(code, key, srcdb):
    print(f'code: {code} | key: {key} | srcdb: {srcdb}')
    data = {
        "group": f"key:{key}",
        "key": f"key:{key}",
        "srcdb": srcdb,
        "matched": f"key:{key}"
    }
    r = requests.post(f'{MAIN_DOMAIN}/course-search/api/?page=fose&route=details', headers=HEADERS, data=urllib.parse.quote_plus(json.dumps(data, separators=(',', ':'))))
    try:
        description_tag = r.json().get('description')
        soup = BeautifulSoup(description_tag, 'html.parser')
        desc = soup.text.replace('Course Description:', '').strip()
        return {'course_code': code, 'description': desc}
    except Exception as e:
        print(f'ERROR code: {code} | key: {key} | srcdb: {srcdb} | error: {e}')
        return {'course_code': code, 'description': ''}


def get_course(character):
    print(character)
    data = {"other":{"srcdb":""},"criteria":[{"field":"keyword","value":character}]}
    r = requests.post(f'{MAIN_DOMAIN}/course-search/api/?page=fose&route=search&keyword={character}', headers=HEADERS, data=urllib.parse.quote_plus(json.dumps(data, separators=(',', ':'))))
    courses = {}
    results = r.json().get('results', [])
    if not results:
        print(f'No results | {character}')
        return courses

    print(f'results: {len(results)} | {character}')
    descriptions = []
    for result in results:
        code = result['code']
        courses[code] = {
            'course_code': code,
            'course_name': result['title']
        }
        descriptions.append([code, result['key'], result['srcdb']])

    with ThreadPoolExecutor(max_workers=10) as executor:
        for i in as_completed(executor.submit(get_description, code, key, srcdb) for code, key, srcdb in descriptions):
            result = i.result()
            courses[result.get('course_code')]['course_description'] = result.get('description')

    print(f'{len(courses)} courses in {character}')
    return courses


def main():
    full_courses = {}
    with ThreadPoolExecutor(max_workers=1) as executor:
        for i in as_completed(executor.submit(get_course, character) for character in [chr(ord('a') + i) for i in range(26)]):
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
