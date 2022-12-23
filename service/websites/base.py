import logging
import time
from abc import abstractmethod, ABC

from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from exception.exception import UnsafeElementException
from model.vacancy import Vacancy
from variables import BaseVariables as Variables


class BaseScrappingService(ABC):
    def __init__(self, driver: WebDriver, wait: WebDriverWait, sleep=Variables.TIME_SLEEP_VALUE):
        self.driver = driver
        self.wait = wait
        self.sleep = sleep

    def get_vacancies(self) -> list[Vacancy]:
        self.set_website()
        logging.info('Website set')
        time.sleep(self.sleep)

        self.handle_cookies()
        logging.info('Cookies handled')
        time.sleep(self.sleep)

        self.login_to_website()
        logging.info('Logged in to website')
        time.sleep(self.sleep)

        self.apply_filters()
        logging.info('Filters Applied')
        time.sleep(self.sleep)
        logging.info('Navigation starting')
        return self.navigate_all_pages()

    @abstractmethod
    def set_website(self) -> None:
        pass

    @abstractmethod
    def login_to_website(self) -> None:
        pass

    @abstractmethod
    def handle_cookies(self) -> None:
        pass

    @abstractmethod
    def apply_filters(self) -> None:
        pass

    @abstractmethod
    def navigate_all_pages(self) -> list[Vacancy]:
        pass

    def find_safely(self, by: By, value) -> WebElement:
        retry_count = 0

        while True and retry_count < Variables.MAX_RETRY_COUNT:
            try:
                return self.wait.until(expected_conditions.presence_of_element_located((by, value)))
            except (TimeoutException, NoSuchElementException) as ex:
                if retry_count > Variables.MAX_RETRY_COUNT:
                    logging.warning("Couldn't find the element by", by, "of", value)
                    raise UnsafeElementException
                retry_count += 1
                logging.warning('Exception happened, retry count =', retry_count)
                self.driver.refresh()

    @abstractmethod
    def get_name(self) -> str:
        pass
