import json
import logging

import math
import requests
from seleniumwire.utils import decode
import xlsxwriter
from seleniumwire import \
    webdriver  # Import from seleniumwire to capture network traffic
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from urllib.parse import parse_qs

logging.basicConfig(format='[%(asctime)s] %(levelname)s:%(message)s [%(filename)s/%(funcName)s:%(lineno)d:%(threadName)s]\n', level=logging.INFO)
MAIN_DOMAIN = 'https://courses.my.harvard.edu'
API_URL_1 = f'{MAIN_DOMAIN}/psc/courses/EMPLOYEE/EMPL/s/WEBLIB_IS_SCL.ISCRIPT1.FieldFormula.IScript_Search'
API_URL_2 = f'{MAIN_DOMAIN}/psc/courses/EMPLOYEE/EMPL/s/WEBLIB_IS_SCL.ISCRIPT1.FieldFormula.IScript_PreLboxAppends'
UNIVERSITY = 'Harvard University'


def decode_body(response):
    body = response.body
    headers = response.headers
    decode_string = decode(body, headers.get(
        'Content-Encoding', 'identity'
    )).decode("utf8")
    raw_string = fr'{decode_string}'
    return json.loads(raw_string)


def run():
    data = {}
    # Initialize the Chrome driver
    driver = webdriver.Chrome()  # Ensure chromedriver is in your PATH, or specify the path

    # Open the webpage
    driver.get(f'{MAIN_DOMAIN}/psp/courses/EMPLOYEE/EMPL/h/?tab=HU_CLASS_SEARCH&SearchReqJSON=%7B"ExcludeBracketed"%3Atrue%2C"PageNumber"%3A1%2C"PageSize"%3A""%2C"SortOrder"%3A%5B"IS_SCL_SUBJ_CAT"%5D%2C"Facets"%3A%5B%5D%2C"Category"%3A"HU_SCL_SCHEDULED_BRACKETED_COURSES"%2C"SearchPropertiesInResults"%3Atrue%2C"FacetsInResults"%3Atrue%2C"SaveRecent"%3Atrue%2C"TopN"%3A""%2C"CombineClassSections"%3Atrue%2C"SearchText"%3A"*"%2C"DeepLink"%3Afalse%7D')

    # Wait for the search button to be present
    wait = WebDriverWait(driver, 60)
    time.sleep(30)
    search_button = wait.until(
        EC.presence_of_element_located((By.ID, "IS_SCL_SearchBtn")))

    # Click the search button
    search_button.click()

    # Optionally, wait for the results to load
    time.sleep(5)  # Adjust sleep time as needed for the results to load

    # Extract the total hit count
    total_hit_count_element = wait.until(EC.presence_of_element_located((By.ID, "IS_SCL_TotalHitCount")))
    total_hit_count = int(total_hit_count_element.text)

    # Calculate the total number of pages (assuming 10 results per page)
    results_per_page = 25
    total_pages = math.ceil(total_hit_count / results_per_page)

    # Function to log network requests
    def log_requests():
        for request in driver.requests:
            if request.response and request.url.startswith((API_URL_1, API_URL_2)):
                body = decode_body(request.response)
                if not body:
                    continue
                if request.url == API_URL_1:
                    for i in body or {}:
                        if i.get('Key') != 'Results':
                            continue
                        results = i.get('ResultsCollection') or {}
                        for j in results:
                            # Parse the query string
                            parsed_query = parse_qs(j.get('Key'))

                            # Extract the values
                            subject = parsed_query.get('subject', [''])[0]
                            catnbr = parsed_query.get('catnbr', [''])[0].strip()
                            course_code = f'{subject} {catnbr}'
                            data[course_code] = {
                                'course_code': course_code,
                                'course_name': j.get('Name'),
                                'course_description': j.get('Description'),
                            }
                else:
                    # Parse the query string
                    parsed_query = parse_qs(body.get('Key'))

                    # Extract the values
                    subject = parsed_query.get('subject', [''])[0]
                    catnbr = parsed_query.get('catnbr', [''])[0].strip()
                    course_code = f'{subject} {catnbr}'
                    data[course_code] = {
                        'course_code': course_code,
                        'course_name': body.get('Name'),
                        'course_description': body.get('IS_SCL_DESCR'),
                    }

    # Function to click all rows on the current page
    def click_all_rows():
        rows = driver.find_elements(By.CLASS_NAME, "isSCL_ResultItem")
        for row in rows:
            try:
                # Check if the row contains "Multiple Sections"
                if "Multiple Sections" in row.text:
                    print("Skipping row with Multiple Sections")
                    continue

                row.click()
                # Optionally, wait for the modal or detail page to load
                time.sleep(2)  # Adjust sleep time as needed for modal loading

                # Find and click the close button
                close_button = wait.until(EC.presence_of_element_located((By.ID, "lbCloseWindowButton")))
                close_button.click()
                log_requests()

                # Optionally, wait for the modal to close
                # time.sleep(2)  # Adjust sleep time as needed for modal closing
            except Exception as e:
                print(f"2. Error clicking row: {e}")

    # Loop through pages 1 to 100
    for page_number in range(1, total_pages):
        try:
            # Log the network requests
            log_requests()
        except Exception as e:
            print(f"1. Error navigating to page {page_number}: {e}")
        try:
            # Click all rows on the current page
            click_all_rows()

            # Find the pagination button by its link text (page number)
            page_button = wait.until(EC.presence_of_element_located(
                (By.LINK_TEXT, str(page_number))))

            # Click the pagination button
            page_button.click()

            # Optionally, wait for the next page results to load
            time.sleep(5)  # Adjust sleep time as needed for the next page to load

        except Exception as e:
            print(f"Error navigating to page {page_number}: {e}")
            break

    # Close the browser
    driver.quit()

    return data


def main():
    full_courses = run()
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
