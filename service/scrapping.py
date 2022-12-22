from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from service.notification.mail import MailService
from repo.vacancy import VacanciesRepository
from service.websites.base import BaseScrappingService
from service.websites.harveynash import HarveyNashScrappingService
from service.websites.mijnfreelance import MijnFreelanceScrappingService
from variables import ScrappingVariables as Variables


def start_scrapping():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    service = Service('./webdriver/chromedriver')

    driver: WebDriver = webdriver.Chrome(service=service, chrome_options=options)

    wait = WebDriverWait(driver, Variables.WAIT_SECONDS)

    scrapping_services: list[BaseScrappingService] = [HarveyNashScrappingService(driver, wait),
                                                      MijnFreelanceScrappingService(driver, wait)]

    vacancies_repository = VacanciesRepository()
    content_html = Variables.MAIL_HEADER

    for service in scrapping_services:
        vacancies = service.get_vacancies()
        content_html = handle_mail_context(html_context=content_html, item_list=vacancies,
                                           service_name=service.get_name())
        vacancies_repository.insert_vacancies(vacancies)

    mail_service = MailService()
    mail_service.send_mail(Variables.MAIL_SUBJECT.format(datetime.today().strftime('%d-%m-%Y')),
                           content_mime='text/html', content_ctx=content_html)


def handle_mail_context(html_context: str, item_list: [], service_name: str) -> str:
    print(len(item_list), 'Vacancies found')
    html_context += Variables.MAIL_DETAIL.format(len(item_list), service_name)
    return html_context
