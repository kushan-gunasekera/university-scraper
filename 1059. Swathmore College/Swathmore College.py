# Adelphi University
import json
import math
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures._base import as_completed

import requests
import xlsxwriter
from bs4 import BeautifulSoup
import time

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
# MAIN_DOMAIN = 'https://vanderbilt.kuali.co/'
UNIVERSITY = 'Swathmore College'
uniqueSessionId = 'lp71a1720268299023'
cookie = 'JSESSIONID=0337D22D5FE75795630310300C4E1236; BIGipServerstudentregistration-pool=222509698.36895.0000'
HEADERS = {'Cookie': cookie}


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
        'cookie': 'JSESSIONID=C691E255058530BFF5BF5EBE4292B35A; BIGipServerstudentregistration-pool=222509698.36895.0000',
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
        response = response or []
        obj = {}
        for i in response:
            code = f'{i.get("subject")} {i.get("courseNumber")}'
            url = 'https://studentregistration.swarthmore.edu/StudentRegistrationSsb/ssb/searchResults'
            data = {
                'term': i.get('term'),
                'courseReferenceNumber': i.get('courseReferenceNumber')
            }

            desc = None
            profs = []
            if i.get('term') and i.get('courseReferenceNumber'):
                print(f"term: {i.get('term')} - courseReferenceNumber: {i.get('courseReferenceNumber')}| getCourseDescription")
                time.sleep(5)
                res = requests.post(f'{url}/getCourseDescription', headers=HEADERS, data=data)
                soup = BeautifulSoup(res.text, 'html.parser')
                desc = soup.text.strip().replace('Section information text:', '')

                time.sleep(5)
                print(f"term: {i.get('term')} - courseReferenceNumber: {i.get('courseReferenceNumber')}| getFacultyMeetingTimes")
                res = requests.post(f'{url}/getFacultyMeetingTimes', headers=HEADERS, data=data)
                for k in res.json().get('fmt', []):
                    for faculty in k.get('faculty', []):
                        profs.append(faculty.get('displayName'))
                profs = list(set(profs))

            obj[code] = {
                'course_code': code,
                'course_name': i.get("courseTitle"),
                'course_description': desc,
                'course_professor': ', '.join(profs),
            }
        return obj

    print(f'term: {term}')
    courses = {}
    results_per_page = 500
    url = 'https://studentregistration.swarthmore.edu/StudentRegistrationSsb/ssb/searchResults/searchResults'
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

    response = requests.get(url, headers=HEADERS, params=params)
    print(f'response.status_code: {response.status_code}')
    data = response.json()
    courses = {**courses, **format_response(data.get('data'))}
    total_pages = math.ceil(data.get('totalCount') / results_per_page)
    for page_number in range(1, total_pages + 1):
        print(f'term: {term} | {page_number}/{total_pages}')
        params['pageOffset'] = page_number
        time.sleep(10)
        response = requests.get(url, headers=HEADERS, params=params)
        print(f'response.status_code: {response.status_code}')
        courses = {**courses, **format_response(response.json().get('data'))}
    return courses


def main():
    full_courses = {}
    terms = get_terms()

    with ThreadPoolExecutor(max_workers=1) as executor:
        for i in as_completed(
                executor.submit(get_courses, term) for term in terms):
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
