import logging
import base64

from datetime import datetime

from pyvirtualdisplay import Display

from selenium import webdriver
from selenium.common import ElementClickInterceptedException, NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from exception.exception import UnsafeElementException
from service.notification.mail import MailService
from repo.vacancy import VacanciesRepository
from service.websites.base import BaseScrappingService
from service.websites.harveynash import HarveyNashScrappingService
from service.websites.mijnfreelance import MijnFreelanceScrappingService
from variables import ScrappingVariables as Variables


def start_scrapping():
    # TODO: Display only required for VM's without actual display. Comment below 2 lines at local work
    display = Display()
    display.start()

    options = Options()

    service = Service(ChromeDriverManager().install())

    driver: WebDriver = webdriver.Chrome(service=service, chrome_options=options)

    wait = WebDriverWait(driver, Variables.WAIT_SECONDS)

    scrapping_services: list[BaseScrappingService] = [
        HarveyNashScrappingService(driver=driver, wait=wait),
        MijnFreelanceScrappingService(driver=driver, wait=wait)]

    vacancies_repository = VacanciesRepository()
    content_html = Variables.MAIL_HEADER

    for service in scrapping_services:
        try:
            vacancies = service.get_vacancies()
            content_html = handle_mail_context(html_context=content_html, item_list=vacancies,
                                               service_name=service.get_name())
            vacancies_repository.insert_vacancies(vacancies)
        except (ElementClickInterceptedException, NoSuchElementException, TimeoutException, UnsafeElementException):
            is_saved = driver.save_screenshot('error.png')
            logging.warning('Screenshot is saved =', is_saved)
            content_html = handle_error_context(html_context=content_html, screenshot_address='./error.png',
                                                service_name=service.get_name())
    # TODO : Comment this when you need to run it on locally
    display.stop()

    mail_service = MailService()
    mail_service.send_mail(Variables.MAIL_SUBJECT.format(datetime.today().strftime('%d-%m-%Y')),
                           content_mime='text/html', content_ctx=content_html)


def handle_mail_context(html_context: str, item_list: [], service_name: str) -> str:
    print(len(item_list), 'Vacancies found')
    html_context += Variables.MAIL_DETAIL.format(len(item_list), service_name)
    return html_context


def handle_error_context(html_context: str, screenshot_address: str, service_name: str):
    data_uri = base64.b64encode(open(screenshot_address, 'rb').read()).decode('utf-8')

    img_tag = '<img src="data:image/png;base64,{}">'.format(data_uri)

    html_context += img_tag + '\n'
    return html_context
