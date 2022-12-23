import logging
import time

from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from model.vacancy import Vacancy
from variables import Attributes, Symbols, Tags, HarveyNashVariables as Variables
from service.websites.base import BaseScrappingService


def parse_element(element: WebElement) -> Vacancy:
    title_element = element.find_element(By.CSS_SELECTOR, Variables.VACANCIES_TITLE_ELEMENT_CSS_SELECTOR)
    location_element = element.find_element(By.CSS_SELECTOR, Variables.VACANCIES_LOCATION_ELEMENT_CSS_SELECTOR)
    location_name_element = location_element.find_element(By.CSS_SELECTOR,
                                                          Variables.VACANCIES_LOCATION_NAME_ELEMENT_CSS_SELECTOR)
    location = next(iter(str(location_name_element.text).split(Symbols.COMMA)), '').strip()

    link = str(title_element.get_attribute(Attributes.HREF))
    split_link = link.split(Symbols.HYPHEN)
    job_id = split_link.pop(split_link.index('jid') + 1)

    return Vacancy(title_element.accessible_name, location, link, job_id, Variables.WEBSITE_NAME)


class HarveyNashScrappingService(BaseScrappingService):
    def __init__(self, driver: WebDriver, wait: WebDriverWait, sleep=Variables.TIME_SLEEP_VALUE):
        super().__init__(driver, wait, sleep)

    def set_website(self) -> None:
        self.driver.get(Variables.TARGET_WEBSITE)

    def login_to_website(self) -> None:
        pass

    def handle_cookies(self) -> None:
        cookie_accept_element = object
        try:
            cookie_accept_element = self.wait.until(
                expected_conditions.presence_of_element_located((By.ID, Variables.COOKIE_ACCEPT_BUTTON_ID))
            )
        finally:
            cookie_accept_element.click()

    def apply_filters(self) -> None:
        job_filters = self.driver.find_element(By.ID, Variables.FILTER_MAIN_CONTAINER_ID)
        job_filter_options = job_filters.find_elements(By.TAG_NAME, Tags.DIV)

        for option in job_filter_options:
            if option.text == Variables.FILTER_SECTOR_OPTION_NAME:
                print(option.accessible_name)
                self.wait.until(
                    expected_conditions.element_to_be_clickable(option)
                )
                option.click()
                time.sleep(1)
                sector_option_display_ul = option.find_element(By.TAG_NAME, Tags.UL)
                sector_option_display_list = sector_option_display_ul.find_elements(By.TAG_NAME, Tags.LI)

                for sector_option in sector_option_display_list:
                    if Variables.FILTER_REQUIRED_OPTION_NAME in sector_option.text:
                        sector_option.click()
                        time.sleep(1)
                        break

                apply_button = sector_option_display_ul.find_element(By.CSS_SELECTOR,
                                                                     Variables.FILTER_APPLY_BUTTON_CSS_SELECTOR)
                apply_button.click()
                break

    def navigate_all_pages(self) -> list[Vacancy]:
        all_vacancies = []

        while True:
            time.sleep(Variables.TIME_SLEEP_VALUE)

            vacancies_container = self.find_safely(By.CSS_SELECTOR, Variables.VACANCIES_CONTAINER_CSS_SELECTOR)
            vacancies = vacancies_container.find_elements(By.CSS_SELECTOR, Variables.VACANCIES_ITEM_CSS_SELECTOR)

            for vacancy in vacancies:
                model = parse_element(vacancy)
                all_vacancies.append(model)

            try:
                logging.info('Checking pagination next button...')
                next_button = self.driver.find_element(By.CSS_SELECTOR, Variables.PAGINATION_NEXT_CSS_SELECTOR)
                logging.info('found')
            except NoSuchElementException:
                logging.warning('Pagination Next was not found.')
                break
            next_button.click()

        return all_vacancies

    def get_name(self):
        return Variables.WEBSITE_NAME
