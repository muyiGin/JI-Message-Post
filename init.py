from selenium import webdriver
from selenium.webdriver.firefox.service import Service
# geckodriver的路径
geckodriver_PATH="/snap/bin/firefox.geckodriver"
browser=webdriver.Firefox(service=Service(geckodriver_PATH))
# 账号/密码/登陆方式
JI_USERNAME = ""
JI_PASSWD = ""
DEFAULT_LOGIN_MODE=1 #0:QR CODE 1:Password
