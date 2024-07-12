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
# MAIN_DOMAIN = 'https://vanderbilt.kuali.co/'
UNIVERSITY = 'University of Utah'
base_url = 'https://app.coursedog.com/api/v1/cm/utah_peoplesoft/courses/search/%24filters'



def get_courses():
    def format_response(response):
        obj = {}
        for i in response:
            code = f'{i.get("code")}'
            obj[code] = {
                'course_code': code,
                'course_name': i.get("longName"),
                'course_description': i.get("description"),
            }
        return obj

    params = {
        'catalogId': 'A314x9JOdHcPlqQTk26R',
        'skip': '0',
        'limit': '20',
        'orderBy': 'code',
        'formatDependents': 'true',
        'effectiveDatesRange': '2024-04-01,2025-02-28',
        'columns': 'customFields.rawCourseId,customFields.crseOfferNbr,customFields.catalogAttributes,customFields.fJUUs,displayName,department,description,name,courseNumber,subjectCode,code,courseGroupId,career,college,longName,status,institution,institutionId,requirementDesignation,requirementGroup,credits'
    }

    # Headers
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,si;q=0.7',
        'content-type': 'application/json',
        'origin': 'https://catalog.utah.edu',
        'priority': 'u=1, i',
        'referer': 'https://catalog.utah.edu/',
        'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    }

    # Data payload
    data = {
        "condition": "and",
        "filters": [
            {
                "id": "status-course",
                "name": "status",
                "inputType": "select",
                "group": "course",
                "type": "is",
                "value": "Active"
            }
        ]
    }

    # Make the request
    response = requests.post(base_url, headers=headers, params=params, json=data)

    courses = {}
    data = response.json()
    courses = {**courses, **format_response(data.get('data'))}
    for page_number in range(20, data.get('listLength'), 20):
        print(f'{page_number}/{data.get("listLength")}')
        params['skip'] = page_number
        response = requests.post(base_url, headers=headers, params=params, json=data)
        courses = {**courses, **format_response(response.json().get('data'))}
    return courses

    return courses


def main():
    full_courses = get_courses()

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
