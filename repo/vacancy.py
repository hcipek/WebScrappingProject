from datetime import datetime
from typing import Union, Any, Mapping

from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.results import UpdateResult
from pymongo import MongoClient

from variables import MongoDBVariables as Variables


def get_set_on_insert(model) -> dict:
    _dict = model.__dict__
    _dict['creationDate'] = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    return _dict


class VacanciesRepository:
    def __init__(self):
        self.client: MongoClient = MongoClient(Variables.URL,
                                               username=Variables.USERNAME,
                                               password=Variables.PASSWORD,
                                               authSource=Variables.AUTH_SOURCE)
        self.database_name = Variables.Databases.VACANCIES
        self.collection_name = Variables.Collections.VACANCIES

    def get_database(self) -> Database[Union[Mapping[str, Any], Any]]:
        return self.client[self.database_name]

    def get_collection(self, collection_name) -> Collection[Union[Mapping[str, Any], Any]]:
        return self.get_database()[collection_name]

    def insert_vacancies(self, vacancies) -> list:
        vacancies_collection = self.get_collection(self.collection_name)

        result = [UpdateResult]

        for vacancy in vacancies:
            result.append(
                vacancies_collection.update_one(
                    filter={
                        'jobId': vacancy.jobId,
                    },
                    update={
                        '$setOnInsert': get_set_on_insert(vacancy),
                        '$set': {
                            'modificationDate': datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                        },
                    },
                    upsert=True,
                )
            )
        return result
