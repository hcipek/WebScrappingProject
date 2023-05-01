import time

import logging

from selenium.common import NoSuchElementException, TimeoutException, ElementClickInterceptedException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from model.vacancy import Vacancy
from variables import Attributes, Symbols, Tags, MijnFreelanceVariables as Variables
from service.websites.base import BaseScrappingService


def wait_for_loading_popup(wait: WebDriverWait):
    logging.info('waiting for loading popup started')
    try:
        # Wait A little for page to refresh
        wait.until(
            expected_conditions.visibility_of_element_located((By.ID, Variables.LOADING_POPUP_ID))
        )
        wait.until(
            expected_conditions.invisibility_of_element_located(
                (By.ID, Variables.LOADING_POPUP_ID))
        )
    except TimeoutException:
        logging.critical('there was a problem with finding loading popup')
        logging.warning('this could be normal issue as well. Needs further inspection')
    finally:
        logging.info('waiting for loading popup ended')


def parse_element(vacancy: WebElement) -> Vacancy:
    main_div_box = vacancy.find_element(By.CSS_SELECTOR, Variables.VACANCIES_ITEM_CSS_SELECTOR)
    link_element = main_div_box.find_element(By.TAG_NAME, Tags.A)
    details_link = link_element.get_attribute(Attributes.HREF)
    title = link_element.find_element(By.CSS_SELECTOR, Variables.VACANCIES_PARSE_TITLE_SPAN_CSS_SELECTOR) \
        .get_attribute(Attributes.TITLE)
    location = link_element.find_element(By.CSS_SELECTOR, Variables.VACANCIES_PARSE_LOCATION_SPAN_CSS_SELECTOR) \
        .get_attribute(Attributes.TITLE)
    job_id = details_link.split(Symbols.SLASH)[-1].split(Symbols.HYPHEN)[0]

    return Vacancy(title, location, details_link, job_id, Variables.WEBSITE_NAME)


class MijnFreelanceScrappingService(BaseScrappingService):
    def __init__(self, driver: WebDriver, wait: WebDriverWait, sleep=5):
        super().__init__(driver, wait, sleep)

    def set_website(self) -> None:
        self.driver.get(Variables.TARGET_WEBSITE)

    def login_to_website(self) -> None:
        login_form = self.find_safely(By.CSS_SELECTOR, Variables.LOGIN_FORM_UL_ELEMENT_CSS_SELECTOR)
        self.find_safely(By.CSS_SELECTOR, Variables.LOGIN_EMAIL_CSS_SELECTOR)
        self.find_safely(By.CSS_SELECTOR, Variables.LOGIN_PASSWORD_CSS_SELECTOR)
        self.find_safely(By.CSS_SELECTOR, Variables.LOGIN_REMEMBER_ME_CSS_SELECTOR)
        self.find_safely(By.CSS_SELECTOR, Variables.LOGIN_BUTTON_CSS_SELECTOR)

        email_input = login_form.find_element(By.CSS_SELECTOR, Variables.LOGIN_EMAIL_CSS_SELECTOR) \
            .find_element(By.TAG_NAME, Tags.INPUT)
        email_input.click()
        email_input.send_keys(Variables.AUTH_USERNAME)
        password_input = login_form.find_element(By.CSS_SELECTOR, Variables.LOGIN_PASSWORD_CSS_SELECTOR) \
            .find_element(By.TAG_NAME, Tags.INPUT)
        password_input.click()
        password_input.send_keys(Variables.AUTH_PASSWORD)

        login_button = self.driver.find_element(By.CSS_SELECTOR, Variables.LOGIN_BUTTON_CSS_SELECTOR)
        self.wait.until(
            expected_conditions.element_to_be_clickable(login_button)
        )
        login_button.click()

    def handle_cookies(self) -> None:
        logging.info('handle cookies started')
        cookie_root = self.wait.until(
            expected_conditions.presence_of_element_located(
                (By.ID, Variables.COOKIE_CONTAINER_ROOT_ID))
        )
        all_cookie_buttons = cookie_root.find_elements(By.TAG_NAME, Tags.BUTTON)

        for button in all_cookie_buttons:
            if button.get_attribute(Variables.COOKIE_ACTION_ATTRIBUTE_NAME) == Variables.COOKIE_ACTION_ATTRIBUTE_VALUE:
                self.wait.until(
                    expected_conditions.element_to_be_clickable(button)
                )
                button.click()
                logging.info('handle cookies finished')
                break

    def apply_filters(self) -> None:
        logging.info('apply filters started')
        # First Find Filter Area and Click the Dropdown List
        filter_form = self.driver.find_element(By.ID, Variables.FILTER_FORM_CONTAINER_ID)

        pick_match_filter = filter_form.find_element(By.CLASS_NAME, Variables.FILTER_CHOOSE_MAIN_CONTAINER_CLASS_NAME)

        dropdown = pick_match_filter.find_element(By.CLASS_NAME, Variables.FILTER_CHOOSE_CLASS_NAME)
        self.wait.until(
            expected_conditions.element_to_be_clickable(dropdown)
        )
        dropdown.click()
        # Then Click Nieuw... filter option on the list
        dropdown_ul = dropdown.find_element(By.TAG_NAME, Tags.UL)

        dropdown_list = dropdown_ul.find_elements(By.TAG_NAME, Tags.LI)

        for element in dropdown_list:
            if element.text == Variables.FILTER_NIEUW_NAME:
                self.wait.until(
                    expected_conditions.element_to_be_clickable(element)
                )
                element.click()
                break

        wait_for_loading_popup(self.wait)
        # Make sure that page back to normal
        expertisegebieden_filter = self.wait.until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, Variables.FILTER_EXPERTISEGEBIEDEN_MAIN_CSS_SELECTOR))
        )
        # Open Expertisegebieden Option
        self.wait.until(
            expected_conditions.element_to_be_clickable(expertisegebieden_filter)
        )
        expertisegebieden_filter.click()

        expertisegebieden_form_element = self.wait.until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, Variables.FILTER_EXPERTISEGEBIEDEN_FORM_CSS_SELECTOR))
        )

        form_options_base = expertisegebieden_form_element \
            .find_element(By.CSS_SELECTOR, Variables.FILTER_EXPERTISEGEBIEDEN_FORM_OPTIONS_CSS_SELECTOR)
        form_options_list = form_options_base \
            .find_elements(By.CSS_SELECTOR, Variables.FILTER_EXPERTISEGEBIEDEN_FORM_OPTION_GROUP_CSS_SELECTOR)

        for option_group in form_options_list:
            h3_element = option_group.find_element(By.TAG_NAME, Tags.H3)

            if h3_element.accessible_name == Variables.FILTER_EXPERTISEGEBIEDEN_REQUIRED_OPTION_NAME:
                self.wait.until(
                    expected_conditions.element_to_be_clickable(h3_element)
                )
                h3_element.click()

                wait_for_loading_popup(self.wait)
                break
        # Close Expertisegebieden Option
        self.wait.until(
            expected_conditions.element_to_be_clickable(expertisegebieden_filter)
        )
        expertisegebieden_filter.click()
        # For Less Time Consumption
        if Variables.FILTER_SINCE_LAST_LOGIN_ACTIVE:
            self.select_since_last_login()
        logging.info('apply filters ended')

    def select_since_last_login(self) -> None:
        logging.info('since last login started')
        time.sleep(Variables.TIME_SLEEP_VALUE)

        since_button = self.driver.find_element(By.CSS_SELECTOR, Variables.FILTER_SINCE_CSS_SELECTOR)
        self.wait.until(
            expected_conditions.element_to_be_clickable(since_button)
        )
        since_button.click()
        time.sleep(1)

        option_list = since_button.find_elements(By.TAG_NAME, Tags.OPTION)

        for option in option_list:
            if option.get_attribute(Variables.FILTER_SINCE_OPTION_ATTRIBUTE_NAME) == \
                    Variables.FILTER_SINCE_OPTION_ATTRIBUTE_VALUE:
                self.wait.until(
                    expected_conditions.element_to_be_clickable(option)
                )
                option.click()

                wait_for_loading_popup(self.wait)
                logging.info('since last login finished')
                break

    def navigate_all_pages(self) -> list[Vacancy]:
        logging.info('navigate all pages started')
        all_vacancies = []

        while True:
            # Navigate
            time.sleep(Variables.TIME_SLEEP_VALUE)

            vacancies_container = self.find_safely(By.CSS_SELECTOR, Variables.VACANCIES_CONTAINER_CSS_SELECTOR)
            # There could be possibly no new elements since last login
            try:
                vacancies = vacancies_container.find_elements(By.TAG_NAME, Tags.LI)
            except AttributeError:
                return all_vacancies

            for vacancy in vacancies:
                model = parse_element(vacancy)
                all_vacancies.append(model)

            try:
                logging.info('Checking pagination next button...')
                next_button: WebElement = self.driver. \
                    find_element(By.CSS_SELECTOR, Variables.PAGINATION_NEXT_CSS_SELECTOR)
                logging.info('found: %s', next_button.get_attribute(Attributes.HREF))
            except NoSuchElementException:
                logging.warning('Pagination Next was not found.')
                break
            self.wait.until(
                expected_conditions.element_to_be_clickable(next_button)
            )
            next_button.click()

        logging.info('navigate all pages ended')
        return all_vacancies

    def get_name(self):
        return Variables.WEBSITE_NAME
