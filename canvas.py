from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from init import browser
import time
import re
import pyperclip
from datetime import datetime
import smtplib
import email.utils
from email.mime.text import MIMEText

CANVAS_URL = "https://jicanvas.com"
_SJTU_LOGIN="https://jicanvas.com/login/openid_connect"
JI_USERNAME = "muyi.gin@sjtu.edu.cn"
JI_PASSWD = "Bao20041102"
_FILE_FLAG=0

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

def dump_content(urls):
    for url in urls:
        browser_get(url)
        _wrapper=browser.find_element(By.ID,"content")
        content=_wrapper.get_attribute("outerHTML")
        today=get_today()
        filename=f"./dates/{today}.txt"
        global _FILE_FLAG
        if _FILE_FLAG:
            mod='a'
        else:
            mod='w'
            _FILE_FLAG=1
        print(mod)
        with open(filename,mod,encoding='utf-8') as file:
            file.write("此通知链接为："+url+content+"\n")

def get_unread_contents(unread_urls):
    for url in unread_urls:
        browser_get(url)
        _lists=browser.find_element(By.ID,"content")
        _mesgs=_lists.find_elements(By.CLASS_NAME,"ic-item-row.ic-announcement-row")
        href=[]
        for m in _mesgs:
            _tmp=m.find_element(By.CLASS_NAME,"fOyUs_bGBk.fOyUs_UeJS")
            style=_tmp.get_attribute("style")
            print(style)
            match=re.search(r"1\.5",style)
            if match:
                _tmp1=m.find_element(By.CLASS_NAME,"ic-item-row__content-link")
                href.append(_tmp1.get_attribute("href"))
                print(href)
        dump_content(href)

def ask_AI():
    today=get_today()
    with open(f"./dates/{today}.txt","r",encoding="utf-8") as file:
        content=file.read()
    message="我现在给你一份资料，里面包含多篇通知，请对他们逐个进行整理,如果是英文你需要将它翻译为中文。我要求的格式是：\n此通知发布的日期与时间(不一定是今天的日期，你需要在内容中查找)：YY-mm-dd xx时xx分 星期几\n链接是：https://xxxxxxx\n标题是：xxxxxx\n内容概述：（这里需要你最精简地用中文概述这篇通知,一定要包括各种你觉得容易遗漏的事情，比如存在附件，截止日期将至，各种要求等等\n(这里为了排版整齐请空一行)\n接下来请你开始：\n"+content+"\n然后当你回答完以后，请添加这根分割线在文章末尾=====================================================================\n"
    browser_get("https://www.doubao.com/chat/")
    _input=browser.find_element(By.TAG_NAME,"textarea")
    _input.click()
    pyperclip.copy(message)
    _input.send_keys(Keys.CONTROL,'v')
    send_buttom=browser.find_element(By.ID,"flow-end-msg-send")
    send_buttom.click()
    time.sleep(30)
    browser.back()
    browser.forward()
    try:
        time.sleep(3)
        _check=browser.find_element(By.ID,"dialog-0")
        _quit=_check.find_element(By.CLASS_NAME,"semi-button-content")
        _quit.click()
        time.sleep(3)
    except:
        pass
    dump_result()

def dump_result():
    time.sleep(3)
    res_html=browser.page_source
    filename=f"result.txt"
    with open(filename,'w',encoding='utf-8') as file:
        file.write(res_html)

def grab_content():
    with open(f"result.txt","r",encoding="utf-8") as file:
        text=file.read()
    pat_get_block=r'={10,}.*?={10,}'
    block=re.findall(pat_get_block,text,re.DOTALL)
    block=''.join(block)
    pat_date=r'(?<=时间：).*?(?=<br)'
    dates=re.findall(pat_date,block,re.DOTALL)
    pat_link=r'https://jicanvas.com/[^ <]*(?="\s*target)'
    links=re.findall(pat_link,block,re.DOTALL)
    pat_title=r'(?<=标题是：).*?(?=<br)'
    titles=re.findall(pat_title,block,re.DOTALL)
    pat_content=r'(?<=内容概述：).*?(?=\s?</div>)'
    contents=re.findall(pat_content,block,re.DOTALL)
    res=''
    for i in range(len(links)):
        res+='<html><body>'+\
                '<h1>'+titles[i]+'</h1>'+\
                '<p>链接：<a href='+links[i]+'>'+dates[i]+'</a></p>'+\
                '<p>'+contents[i]+'</p>'
    return res

def send_mail(content):
    FROM='1458652882@qq.com'
    TO='muyi.gin@sjtu.edu.cn'
    AUTH='wefmnhbnzydhbadc'
    message = MIMEText(content,'html','utf-8')
    message['From'] = email.utils.formataddr(('笨蛋机器人', FROM))
    message['To'] = email.utils.formataddr(('亲爱的主人', TO))
    message['Subject'] = "Canvas更新于"+datetime.now().strftime("%m月%d日 %H:%M:%S")
    server = smtplib.SMTP_SSL('smtp.qq.com', 465)
    server.login(FROM,AUTH)
    server.set_debuglevel(True)
    try:
        server.sendmail(FROM,[TO],msg=message.as_string())
    finally:
        server.quit()

browser_get(CANVAS_URL)
login_check()
unread_urls=unread_counts()
print(unread_urls)
get_unread_contents(unread_urls)
ask_AI()
send_mail(grab_content())
