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
UNIVERSITY = 'Swathmore College'
uniqueSessionId = 'lp71a1720268299023'
cookie = 'JSESSIONID=097E12DF16946D2ACA4A417C4B22984F; BIGipServerstudentregistration-pool=222509698.36895.0000'


def get_terms():
    url = 'https://studentregistration.swarthmore.edu/StudentRegistrationSsb/ssb/courseSearch/getTerms'
    params = {
        'searchTerm': '',
        'offset': '1',
        'max': '1000',
        '_': '1720253866905'
    }

    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,si;q=0.7',
        'cookie': 'JSESSIONID=37138D00BB78CE76B17410E89B085EBC; GCLB=CO283tryrdfQahAD',
        'priority': 'u=1, i',
        'referer': 'https://bn-reg.uis.georgetown.edu/StudentRegistrationSsb/ssb/term/termSelection?mode=courseSearch',
        'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
        'x-synchronizer-token': '1e9f5ca7-b488-4497-b4ce-0eadd0f6090b'
    }

    response = requests.get(url, params=params, headers=headers)
    return [i.get('code') for i in response.json()]


def get_courses(term):
    def format_response(response):
        obj = {}
        for i in response:
            code = f'{i.get("subject")} {i.get("courseNumber")}'
            obj[code] = {
                'course_code': code,
                'course_name': i.get("courseTitle"),
                'course_description': i.get("courseDescription"),
            }
        return obj

    courses = {}
    results_per_page = 500
    url = 'https://studentregistration.swarthmore.edu/StudentRegistrationSsb/ssb/courseSearchResults/courseSearchResults'
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,si;q=0.7',
        'cookie': cookie,
        'priority': 'u=1, i',
        'referer': 'https://bn-reg.uis.georgetown.edu/StudentRegistrationSsb/ssb/courseSearch/courseSearch',
        'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
        'x-synchronizer-token': '94484524-de90-499c-bcf5-19600794f3e6'
    }
    params = {
        'txt_term': term,
        'startDatepicker': '',
        'endDatepicker': '',
        'uniqueSessionId': uniqueSessionId,
        'pageOffset': 0,
        'pageMaxSize': results_per_page,
        'sortColumn': 'subjectDescription',
        'sortDirection': 'asc'
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    courses = {**courses, **format_response(data.get('data'))}
    total_pages = math.ceil(data.get('totalCount') / results_per_page)
    for page_number in range(1, total_pages + 1):
        print(f'term: {term} | {page_number}/{total_pages}')
        params['pageOffset'] = page_number
        response = requests.get(url, headers=headers, params=params)
        courses = {**courses, **format_response(response.json().get('data'))}
    return courses


def main():
    full_courses = {}
    terms = get_terms()

    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_courses, term) for term in terms):
            full_courses = {**full_courses, **i.result()}

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
