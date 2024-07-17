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
MAIN_DOMAIN = 'https://app.coursedog.com/api/v1/cm/byu/courses/search/%24filters?catalogId=uGrT9sX2clUBV30mw3yl&skip={skip}&limit={limit}&orderBy=catalogDisplayName%2CtranscriptDescription%2ClongName%2Cname&formatDependents=true&effectiveDatesRange=2023-09-05%2C2023-09-05&columns=customFields.rawCourseId%2CcustomFields.crseOfferNbr%2CcustomFields.catalogAttributes%2CdisplayName%2Cdepartment%2Cdescription%2Cname%2CcourseNumber%2CsubjectCode%2Ccode%2CcourseGroupId%2Ccareer%2Ccollege%2ClongName%2Cstatus%2Cinstitution%2CinstitutionId%2Ccomponents%2Ccredits%2Cdepartments%2Crequisites'
# BODY = {"condition":"and","filters":[{"id":"courseNumber-course","name":"courseNumber","inputType":"text","group":"course","type":"doesNotContain","value":"TR"},{"id":"subjectCode-course","name":"subjectCode","inputType":"subjectCodeSelect","group":"course","type":"isNot","value":"ADVR"},{"id":"subjectCode-course","name":"subjectCode","inputType":"subjectCodeSelect","group":"course","type":"isNot","value":"CONS"},{"id":"subjectCode-course","name":"subjectCode","inputType":"subjectCodeSelect","group":"course","type":"isNot","value":"COOP"},{"id":"subjectCode-course","name":"subjectCode","inputType":"subjectCodeSelect","group":"course","type":"isNot","value":"NSE"},{"id":"subjectCode-course","name":"subjectCode","inputType":"subjectCodeSelect","group":"course","type":"isNot","value":"PROF"},{"id":"subjectCode-course","name":"subjectCode","inputType":"subjectCodeSelect","group":"course","type":"isNot","value":"PROFSTAT"},{"id":"subjectCode-course","name":"subjectCode","inputType":"subjectCodeSelect","group":"course","type":"isNot","value":"SA"},{"id":"status-course","name":"status","inputType":"select","group":"course","type":"is","value":"Active"},{"id":"courseOfferingStatus-course","name":"courseOfferingStatus","inputType":"select","group":"course","type":"isNot","value":"Inactive","customField":True},{"id":"catalogPrint-course","name":"catalogPrint","inputType":"boolean","group":"course","type":"is","value":True},{"id":"courseApproved-course","name":"courseApproved","inputType":"select","group":"course","type":"is","value":"Approved"}]}
UNIVERSITY = 'Brigham Young University'


def get_courses():
    skip = 0
    limit = 1000
    courses = {}
    while True:
        print(skip)
        r = requests.post(MAIN_DOMAIN.format(skip=skip, limit=limit), headers=HEADERS)
        data = r.json().get('data', [])
        print(f"listLength: {r.json().get('listLength')}")
        if not data:
            break
        for i in data:
            courses[i['code']] = {
                'course_code': i['code'],
                'course_name': i['longName'],
                'course_description': i['description'],
            }
        skip += limit
    return courses


def main():
    # get_course('/courses/AIP.html')
    full_courses = get_courses()
    # full_courses = {}
    # with ThreadPoolExecutor(max_workers=100) as executor:
    #     for i in as_completed(executor.submit(get_course, course_url) for course_url in course_urls):
    #         full_courses = {**full_courses, **i.result()}

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