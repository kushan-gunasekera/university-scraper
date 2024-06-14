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
MAIN_DOMAIN = 'https://api-us-west-1.prod.courseloop.com/publisher/browsepage-academic-items?'
query_values = [
    '7e561ea0db6fa0107f1572f5f39619b1',
    '32561ea0db6fa0107f1572f5f39619b4',
    '36561ea0db6fa0107f1572f5f39619b2',
    'ba569aa0db6fa0107f1572f5f396194e',
    '3a561ea0db6fa0107f1572f5f39619b0',
    'b2561ea0db6fa0107f1572f5f39619b3',
    'be569aa0db6fa0107f1572f5f396194c',
    'f2569aa0db6fa0107f1572f5f396194e',
    '7a561ea0db6fa0107f1572f5f39619b3',
    'fe561ea0db6fa0107f1572f5f39619b0',
    '3e569aa0db6fa0107f1572f5f396194d',
    'b6561ea0db6fa0107f1572f5f39619b1',
    '76569aa0db6fa0107f1572f5f396194d',
]
UNIVERSITY = 'University of CA Los Angeles (UCLA)'


def get_courses(query_value):
    courses = {}
    body = {
        "siteId": "ucla-prod",
        "contentType": "subject",
        "queryParams": [
            {
                "queryField": "parentAcademicOrg",
                "queryValue": query_value
            },
            {
                "queryField": "implementationYear",
                "queryValue": "2023"
            },
            {
                "queryField": "studyLevel",
                "queryValue": "ucla"
            }
        ],
        "limit": 100
    }
    offset = 0
    while True:
        print(f'{query_value} | {offset}')
        body['offset'] = offset
        r = requests.post(MAIN_DOMAIN, headers=HEADERS, json=body)
        data = r.json().get('data', []).get('data', [])
        if not data:
            break
        for i in data:
            courses[i.get('code')] = {
                'course_code': i.get('code'),
                'course_name': i.get('title'),
                'course_description': json.loads(i.get('data')).get('description'),
            }
        offset += 100
    return courses


def main():
    full_courses = {}
    with ThreadPoolExecutor(max_workers=50) as executor:
        for i in as_completed(executor.submit(get_courses, query_value) for query_value in query_values):
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
