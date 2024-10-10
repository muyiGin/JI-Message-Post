from selenium import webdriver
from selenium.webdriver.firefox.service import Service

browser=webdriver.Firefox(service=Service("/snap/bin/firefox.geckodriver"))
