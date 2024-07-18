# Adelphi University
import json
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures._base import as_completed

import requests
import xlsxwriter

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
MAIN_DOMAIN = 'https://course-app-api.planning.sis.uw.edu'
CAMPUS = 'bothell'
UNIVERSITY = 'University of Washington Bothell Campus'

all_codes = []
old_courses = {}
try:
    with open('University of Washington.json', 'r') as f:
        old_courses = json.load(f)
        all_codes = old_courses.keys()
except:
    pass


def get_programs():
    r = requests.get(f'{MAIN_DOMAIN}/api/subjectAreas/', headers=HEADERS)
    return [i.get('code') for i in r.json() if i.get('campus') == CAMPUS]


def get_course(code):
    # code = 'VIET'
    print(code)
    courses = {}
    HEADERS['Cookie'] = 'sessionId=61c1874194fff433a706d4a3943d8e4cacf6d6c73432cb03743cd82164b0fc38'
    HEADERS['X-Csrf-Token'] = '09152ab7f3d9523ee846978bda155833aa50dac6e9edccb130141bb967cdeae0beada3cea8618b92f3d885925b52894288cbcca7ab52ed831a7785109d5cc2ee3511743964670702fa2e8a4dc75b27bb99efc5438d4d6060b93b243fe6901006f2642dea38c166812571b268b18baf4b8b695b100696b076cd7a007d6602c1f2'
    data = {
        "username": "GUEST",
        "requestId": "cfbe1306-d198-4117-97ee-973ab4fb9692",
        "sectionSearch": False,
        "instructorSearch": False,
        "queryString": code,
        "consumerLevel": "UNDERGRADUATE",
        "campus": "seattle"
    }
    r = requests.post(f'{MAIN_DOMAIN}/api/courses/', headers=HEADERS, json=data)
    recourd_count = len(r.json())
    print(f'{code} has {recourd_count} rows')
    for count, i in enumerate(r.json(), 1):
        profs = []
        code = i.get('code')
        if code in all_codes:
            continue
        course_id = i.get('id').split(':')[0]
        desc_url = f'{MAIN_DOMAIN}/api/courses/{urllib.parse.quote(code)}/details?courseId={course_id}'

        print(f'[{count}/{recourd_count}] {code} - {desc_url}')
        res = requests.get(desc_url, headers=HEADERS)
        desc = res.json().get('courseSummaryDetails', {}).get('courseDescription')
        for j in res.json().get('courseOfferingInstitutionList', []):
            for k in j.get('courseOfferingTermList', []):
                for l in k.get('activityOfferingItemList', []):
                    profs.append(l.get('instructor'))
        profs = list(set('profs'))
        courses[code] = {
            'course_code': code,
            'course_name': i.get('title'),
            'course_description': desc,
            'course_professor': ', '.join(profs),
        }

    return courses


def main():
    full_courses = {}
    programs = get_programs()
    # print(len(urls))

    with ThreadPoolExecutor(max_workers=1) as executor:
        for i in as_completed(executor.submit(get_course, code) for code in programs):
            full_courses = {**full_courses, **i.result()}

    full_courses = {**full_courses, **old_courses}
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