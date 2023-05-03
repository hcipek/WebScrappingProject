### How to Run at VM's like GCP CE or AWS EC2

Install Python 3

Install xvfb

Install Chrome
- ```wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb```
- ```sudo dpkg -i google-chrome-stable_current_amd64.deb```
- If you see any errors during the installation, execute ```sudo apt-get install -f```

Install Pip
- Install selenium(with sudo)
- Install pyvirtualdisplay(with sudo)
- Install webdriver_manager(with sudo)
- Install sendgrid(with sudo)
- Install pymongo(with sudo)
- Install google-cloud-logging(with sudo)
If you run into any issue please execute 
```
sudo apt update
sudo apt upgrade
```
