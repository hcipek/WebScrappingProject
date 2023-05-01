### How to Run at VM's like GCP CE or AWS EC2

Install Python 3
Install xvfb
Install Chrome
Install Pip
- Install selenium
- Install pyvirtualdisplay
- Install webdriver_manager
- Install sendgrid
- Install pymongo
- Install google-cloud-logging

### Issue on GCP

I dont understand the reason but somehow python lose its permission access to 'output.log' file. After I remove the log file manually, it turned back to normal. I ran the script back to back to see is it going to happen again but it seems like a normal. Mayber after 3 months, log file became so big and it no longer allowed the python to append it anything new, I don't know actually.
