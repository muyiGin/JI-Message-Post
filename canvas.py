from bs4 import BeautifulSoup as bs
from urllib.parse import ParseResultBytes
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from init import browser
import time
import re
import os
from datetime import datetime

CANVAS_URL = "https://jicanvas.com"
_SJTU_LOGIN="https://jicanvas.com/login/openid_connect"
USERNAME = "muyi.gin@sjtu.edu.cn"
PASSWD = "Bao20041102"

def fail(reason):
    print(f"{reason}")
    browser.quit()
    exit(0)
def browser_get(url):
    browser.get(url)
    time.sleep(3)

def login():
    browser_get(_SJTU_LOGIN)
    try:
        WebDriverWait(browser,30,0.5).until(
                lambda browser:browser.find_element(By.ID,"dashboard")
                )
        return
    except Exception as e:
        fail("跳转登录失败。")

def login_check():
    for _ in range(2):
        try:
            if "login" in browser.current_url:
                print("需要登录。")
                login()
            if browser.find_element(By.ID,"dashboard"):
                print("成功登录。")
                return
        except NoSuchElementException:
            continue
    fail("登录失败。")

def check_announcement_buttom_exist(card):
    try:
        announcements=card.find_element(By.CLASS_NAME,"ic-DashboardCard__action.announcements")
        if announcements:
            return announcements
    except:
        return False

def unread_counts():
    unread_dirs={}
    try:
        time.sleep(3)
        dashboard_box = browser.find_element(By.CLASS_NAME, "ic-DashboardCard__box__container")
        dashboard_cards=dashboard_box.find_elements(By.CLASS_NAME,"ic-DashboardCard")
        for card in dashboard_cards:
            course_name = card.get_attribute("aria-label")
            announcements=check_announcement_buttom_exist(card)
            if announcements:
                _tmp1=announcements.find_element(By.CLASS_NAME,"ic-DashboardCard__action-layout")
                try:
                    unreads=_tmp1.find_element(By.CLASS_NAME,"ic-DashboardCard__action-badge")
                    counts=unreads.find_element(By.CLASS_NAME,"unread_count").text
                    print(f"{course_name} 的未读消息数:{counts}")
                    href=announcements.get_attribute("href")
                    unread_dirs[href]=counts
                except:
                    continue
        return unread_dirs
    except:
        fail("获取课程列表失败。")

def get_today():
    today=datetime.now().strftime('%Y-%m-%d')
    return today

def dump_content(url):
    browser_get(url)
    _wrapper=browser.find_element(By.ID,"content")
    _tag=_wrapper.find_element(By.TAG_NAME,"h1")
    _span=_tag.find_element(By.XPATH,"..")
    content=_span.get_attribute("outerHTML")
    today=get_today()
    filename=f"{today}.txt"
    with open(filename,'a',encoding='utf-8') as file:
        file.write("此通知链接为："+url+content+"\n")

def get_unread_contents(unread_urls):
    for url in unread_urls:
        browser_get(url)
        _lists=browser.find_element(By.ID,"content")
        _mesgs=_lists.find_elements(By.CLASS_NAME,"ic-item-row.ic-announcement-row")
        for m in _mesgs:
            _tmp=m.find_element(By.CLASS_NAME,"fOyUs_bGBk.fOyUs_UeJS")
            style=_tmp.get_attribute("style")
            if re.search(r"margin:\s*([^;]*)1\.5",style):
                _tmp1=m.find_element(By.CLASS_NAME,"ic-item-row__content-link")
                href=_tmp1.get_attribute("href")
                print(href)
                dump_content(href)

def ask_AI():
    today=get_today()
    with open(f"./{today}.txt","r",encoding="utf-8") as file:
        content=file.read()
    message="我现在给你一份资料，里面包含多篇通知，请对他们逐个进行整理,如果是英文你需要将它翻译为中文。我要求的格式是：\n今天的日期与时间：YY-mm-dd xx时xx分 星期几\n链接是：https://xxxxxxx\n标题是：xxxxxx\n内容概述：（这里需要你最精简地用中文概述这篇通知,一定要包括各种你觉得容易遗漏的事情，比如存在附件，截止日期将至，各种要求等等）\n内容全文：（这里将原文放入，英文就放英文，中文就放中文）\n(这里为了排版整齐请空一行)\n接下来请你开始：\n"+content
    print(message)
    browser_get("https://www.doubao.com/chat/")
    time.sleep(3)
    _input=browser.find_element(By.TAG_NAME,"textarea")
    _input.click()
    _input.send_keys(message)
    send_buttom=browser.find_element(By.ID,"flow-end-msg-send")
    send_buttom.click()



#  browser_get(CANVAS_URL)
#  login_check()
#  unread_urls=unread_counts()
#  print(unread_urls)
#  get_unread_contents(unread_urls)
ask_AI()


