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
# MAIN_DOMAIN = 'https://ga.rice.edu'
UNIVERSITY = 'University of CA Santa Barbara'


def get_courses():
    url = 'https://app.coursedog.com/api/v1/cm/ucsb/courses/search/%24filters?catalogId=DAkOBLOSo6VpRHbQ1YCI&skip=0&limit=100000&orderBy=code&formatDependents=true&effectiveDatesRange=2024-04-01%2C2024-09-13&columns=customFields.rawCourseId%2CcustomFields.crseOfferNbr%2CcustomFields.catalogAttributes%2CcustomFields.advisorEnrollmentComments%2CdisplayName%2Cdepartment%2Cdescription%2Cname%2CcourseNumber%2CsubjectCode%2Ccode%2CcourseGroupId%2Ccareer%2Ccollege%2ClongName%2Cstatus%2Cinstitution%2CinstitutionId%2Ccredits%2Crequisites'
    r = requests.get(url, headers=HEADERS)

    courses = {}
    for i in r.json().get('data'):
        courses[i.get('courseGroupId')] = i.get('longName')
        courses[i.get('courseGroupId')] = {
            'course_code': i.get('courseGroupId'),
            'course_name': i.get('longName'),
            'course_description': i.get('description'),
        }
    return courses


def main():
    full_courses = get_courses()

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
