# Adelphi University
import itertools
import json
import math
import random
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures._base import as_completed

import requests
import xlsxwriter
from bs4 import BeautifulSoup
from lxml import html

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
MAIN_DOMAIN = 'https://services.bc.edu'
UNIVERSITY = 'Boston College'


def get_course(term, school_or_institute):
    print(f'term: {term} | school_or_institute: {school_or_institute}')
    courses = {}
    # URL to make the GET request
    url = f'{MAIN_DOMAIN}/PublicCourseInfoSched/courseinfoschedResults!displayInput.action'

    # Query parameters for the GET request
    params = {
        'authenticated': 'false',
        'keyword': '',
        'presentTerm': '2024SPRG',
        'registrationTerm': '2024FALL',
        'termsString': '2024SPRG,2024SUMM,2024FALL',
        'selectedTerm': term,
        'selectedSort': '',
        'selectedSchool': school_or_institute,
        'selectedSubject': '0_All',
        'selectedNumberRange': '',
        'selectedLevel': '',
        'selectedMeetingDay': '',
        'selectedMeetingTime': '',
        'selectedCourseStatus': '',
        'selectedCourseCredit': '',
        'canvasSearchLink': '',
        'personResponse': 'zddn252cG6jFsd8HulRrdrz5sn',
        'googleSiteKey': '6LdV2EYUAAAAACy8ROcSlHHznHJ64bn87jvDqwaf'
    }

    # Headers for the request
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8,si;q=0.7',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie': 'ZNPCQ003-32373700=d51d8bde; TS0172a859=013fbfbcae81ba0a58bee11cd191d86a0590502d12cd61c2ee709db5a451ca67e3e43a3b8eae6ea45af1d49b240a915268d6020b00a5b322f48e7ac4504277c12783018d4b; BIGipServer~portal~wpsprod=3809126280.36895.0000; BIGipServer~portal~wpsprod_apache=3792349064.20480.0000; TS01ab1b05=013fbfbcae16581f9504cece7995d8f48ec778670001bf7681c61127f04416c4c3927f89e6eec82986a50f02f268f20a4c11039d7af4bdc6f0fbbfdeb0ea087e94e7451438; TS01e1f339=013fbfbcae83edfbe9428a8f0fe1a75021326345bbb596125f2832222a27a79a9e4e308b3448e623924a4d21369e3bf6bf05fa2c5c17d2b87a44288f5e1fcc0631fceb13f48686a508e9703399577079d69b991693a1622a3b6614c0695a396de8b93d7603',
        'Referer': 'https://services.bc.edu/PublicCourseInfoSched/courseinfoschedResults',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"'
    }

    # Make the GET request
    response = requests.get(url, headers=headers, params=params)
    soup = BeautifulSoup(response.content, 'html.parser')

    for i in soup.find_all('tr', class_='course'):
        name_split = i.find('strong', class_='course-name').text.split('(')
        code = name_split[1][:-1].strip()
        title = name_split[0].strip()
        desc = i.find_next_sibling().find('p').text.replace('Description:', '').strip()
        courses[code] = {
            'course_code': code,
            'course_name': title,
            'course_description': desc,
        }
    return courses


def get_departments_and_semesters():
    url = f'{MAIN_DOMAIN}/PublicCourseInfoSched/courseinfoschedResults'

    # Headers for the request
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8,si;q=0.7',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': 'ZNPCQ003-32373700=d51d8bde; TS0172a859=013fbfbcae81ba0a58bee11cd191d86a0590502d12cd61c2ee709db5a451ca67e3e43a3b8eae6ea45af1d49b240a915268d6020b00a5b322f48e7ac4504277c12783018d4b; BIGipServer~portal~wpsprod=3809126280.36895.0000; BIGipServer~portal~wpsprod_apache=3792349064.20480.0000; TS01ab1b05=013fbfbcae16581f9504cece7995d8f48ec778670001bf7681c61127f04416c4c3927f89e6eec82986a50f02f268f20a4c11039d7af4bdc6f0fbbfdeb0ea087e94e7451438; TS01e1f339=013fbfbcaed0b9880cbb87360dd374ca39cd0a3444a0a79cc08f74499e24adb649e0a1945f3f9c04f3b312247d52639861155b4a69474ec07bfc8eb67428ca51a95e225189028f95b05f0bb4e9dbc698e8b393df8f42b7809fc267968577f3c911616f95b7',
        'Origin': 'https://services.bc.edu',
        'Referer': 'https://services.bc.edu/PublicCourseInfoSched/courseinfoschedResults!displayInput.action?authenticated=false&keyword=&presentTerm=2024SPRG&registrationTerm=2024FALL&termsString=2024SPRG%2C2024SUMM%2C2024FALL&selectedTerm=2024SUMM&selectedSort=&selectedSchool=6_CSOM&selectedSubject=0_All&selectedNumberRange=&selectedLevel=&selectedMeetingDay=&selectedMeetingTime=&selectedCourseStatus=&selectedCourseCredit=&canvasSearchLink=&personResponse=Rdsnd5ucd6prjH2Wu5R6d5zdsc&googleSiteKey=6LdV2EYUAAAAACy8ROcSlHHznHJ64bn87jvDqwaf',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"'
    }

    # Data for the request
    data = {
        'presentTerm': '2024SPRG',
        'authenticated': 'false',
        'publicInterval': '14400000',
        'personResponse': 'Rdsnd5ucd6prjH2Wu5R6d5zdsc',
        'googleSiteKey': '6LdV2EYUAAAAACy8ROcSlHHznHJ64bn87jvDqwaf',
        'registrationTerm': '2024FALL',
        'termsString': '2024SPRG,2024SUMM,2024FALL',
        'selectedSort': '',
        'selectedTerm': '2024SUMM',
        'selectedSchool': '6_CSOM',
        'selectedSubject': '0_All',
        'selectedNumberRange': 'All',
        'selectedLevel': '',
        'selectedMeetingDay': 'All',
        'selectedMeetingTime': 'All',
        'selectedCourseStatus': 'All',
        'selectedCourseCredit': 'All',
        'resultSetSize': '73',
        'method:startOver': 'Start Over',
        '2024SUMM': '2024SUMM',
        '6_CSOM': '6_CSOM',
        '0_All': '0_All',
        'All': 'All',
        'All': 'All',
        'All': 'All',
        'keyword': ''
    }

    # Make the POST request
    r = requests.post(url, headers=headers, data=data)
    soup = BeautifulSoup(r.content, 'html.parser')

    terms_input = soup.find('input', {'name': 'termsString'})
    term_values = []
    if terms_input and 'value' in terms_input.attrs:
        term_values = terms_input['value'].split(',')

    school_or_institute_values = []
    for i in soup.find('select', {'id': 'courseinfoschedHome_selectedSchool'}).find_all('option'):
        school_or_institute_values.append(i.get('value'))

    return list(itertools.product(term_values, school_or_institute_values))


def main():
    full_courses = {}
    departments_and_semester = get_departments_and_semesters()
    print(f'all combinations: {len(departments_and_semester)}')

    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_course, *details) for details in departments_and_semester):
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
