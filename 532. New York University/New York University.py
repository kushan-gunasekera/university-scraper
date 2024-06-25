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
MAIN_DOMAIN = 'https://bulletins.nyu.edu'
UNIVERSITY = 'New York University'


def get_description(code, crn, srcdb):
    print(f'get_description --> {code} | {crn} | {srcdb}')
    data = {
        "group": f"code:{code}",
        "key": f"crn:{crn}",
        "srcdb": srcdb,
        "matched": f"crn:{crn}"
    }
    r = requests.post(
        f'{MAIN_DOMAIN}/class-search/api/?page=fose&route=details',
        headers=HEADERS,
        data=urllib.parse.quote_plus(json.dumps(data, separators=(',', ':')))
    )
    return code, r.json().get('description')


def get_course(character, _type='course', srcdb=''):
    print(f'get_course --> {character} | {_type} | {srcdb}')
    data = {"other":{"srcdb":srcdb},"criteria":[{"field":"keyword","value":character}]}
    r = requests.post(f'{MAIN_DOMAIN}/{_type}-search/api/?page=fose&route=search&keyword={character}', headers=HEADERS, data=urllib.parse.quote_plus(json.dumps(data, separators=(',', ':'))))
    courses = {}
    results = r.json().get('results', [])
    if not results:
        print(f'No results | {character}')
        return courses

    print(f'results: {len(results)} | {character}')
    description_list = []
    for result in results:
        code = result['code']
        courses[code] = {
            'course_code': code,
            'course_name': result['title'],
        }
        description_list.append(
            [code, result['crn'], result['srcdb']]
        )

    print(f'{len(courses)} {_type} in {character}')
    with ThreadPoolExecutor(max_workers=10) as executor:
        for i in as_completed(executor.submit(get_description, code, crn, srcdb) for code, crn, srcdb in description_list):
            code, description = i.result()
            courses[code]['course_description'] = description
    return courses


def main():
    # get_courses()
    # get_course('999999')
    # course_urls = get_courses()
    full_courses = {}
    # with ThreadPoolExecutor(max_workers=1) as executor:
    #     for i in as_completed(executor.submit(get_course, character) for character in [chr(ord('a') + i) for i in range(26)]):
    #         full_courses = {**full_courses, **i.result()}
    # with ThreadPoolExecutor(max_workers=1) as executor:
    #     for i in as_completed(executor.submit(get_course, character, 'course', 1234) for character in [chr(ord('a') + i) for i in range(26)]):
    #         full_courses = {**full_courses, **i.result()}
    # with ThreadPoolExecutor(max_workers=1) as executor:
    #     for i in as_completed(executor.submit(get_course, character, 'course', 1232) for character in [chr(ord('a') + i) for i in range(26)]):
    #         full_courses = {**full_courses, **i.result()}
    with ThreadPoolExecutor(max_workers=1) as executor:
        for i in as_completed(executor.submit(get_course, character, 'class', 1248) for character in [chr(ord('a') + i) for i in range(26)]):
            full_courses = {**full_courses, **i.result()}
    with ThreadPoolExecutor(max_workers=1) as executor:
        for i in as_completed(executor.submit(get_course, character, 'class', 1246) for character in [chr(ord('a') + i) for i in range(26)]):
            full_courses = {**full_courses, **i.result()}
    with ThreadPoolExecutor(max_workers=1) as executor:
        for i in as_completed(executor.submit(get_course, character, 'class', 1244) for character in [chr(ord('a') + i) for i in range(26)]):
            full_courses = {**full_courses, **i.result()}
    # with ThreadPoolExecutor(max_workers=1) as executor:
    #     for i in as_completed(executor.submit(get_course, character, 'class', 1242) for character in [chr(ord('a') + i) for i in range(26)]):
    #         full_courses = {**full_courses, **i.result()}
    # with ThreadPoolExecutor(max_workers=1) as executor:
    #     for i in as_completed(executor.submit(get_course, character, 'class', 1238) for character in [chr(ord('a') + i) for i in range(26)]):
    #         full_courses = {**full_courses, **i.result()}

    with open(f'{UNIVERSITY}.json', 'w') as json_file:
        json.dump(full_courses, json_file, indent=4)

    header = [
        'course_code', 'course_name', 'course_description',
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
        row += 1

    workbook.close()



if __name__ == '__main__':
    main()
