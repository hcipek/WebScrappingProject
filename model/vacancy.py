from datetime import datetime

from model.base import Base


class Vacancy(Base):
    def __init__(self, title, location, link, job_id, website):
        super().__init__()
        self.title = title
        self.location = location
        self.link = link
        self.jobId = job_id
        self.website = website
        self.hasDetails = False
        self.date = datetime.today().strftime('%Y-%m-%d')
