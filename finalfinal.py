import numpy as np
import time
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import re
import mysql.connector
import json
import datetime


class create_dict(dict):

    # __init__ function
    def __init__(self):
        self = dict()

    # Function to add key:value
    def add(self, key, value):
        self[key] = value


db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="root",
    database="facebookdb",
)

stud_json = create_dict()

options = webdriver.FirefoxOptions()
options.set_preference("dom.push.enabled", False)
driver = webdriver.Firefox(
    options=options, executable_path=r'C:\Users\ZOUNDER\Documents\geckodriver\geckodriver.exe')
driver.implicitly_wait(10)


url = "https://www.facebook.com"
driver.get(url)

# authentication
email_elem = driver.find_element_by_name("email")
email_elem.send_keys("")  # email
password_elem = driver.find_element_by_name("pass")
password_elem.send_keys("")  # password
password_elem.submit()
time.sleep(2)

# search facebook
input_keyword = driver.find_element_by_name("q")
# insert keyword
input_keyword.send_keys("otaku")
input_keyword.submit()
time.sleep(7)

# link = driver.find_element_by_link_text("")
# link.click()
# time.sleep(2)

# we  filter our search with just groups
btn = driver.find_element_by_xpath("//*[text()='Groups']")
btn.click()
time.sleep(2)



# we keep scrolling to load all groups
lenOfPage = driver.execute_script(
    "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
match = False
while(match == False):
    lastCount = lenOfPage
    time.sleep(3)
    lenOfPage = driver.execute_script(
        "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    if lastCount == lenOfPage:
        match = True

# get urls of groups
elems = driver.find_elements_by_xpath(
    "//div[@class='_4bl7 _3-90']/a[@href]")
groups_urls = []
for elem in elems:
    print(elem.get_attribute("href"))
    group_url = elem.get_attribute("href")
    groups_urls.append(group_url)

time.sleep(10)

groups_urls = list(dict.fromkeys(groups_urls))

print('*******************')

# now we search our groups one by one
for url in groups_urls:

    driver.get(url)
    time.sleep(3)

    element_name = driver.find_element_by_xpath("//h1[@id='seo_h1_tag']/a")
    group_name = element_name.text

    print(group_name)

    time.sleep(2)
    try:
        members_link = driver.find_element_by_xpath("//*[text()='About']")
        members_link.click()
        time.sleep(2)
    except:
        continue

    element_date = driver.find_element_by_xpath(
        "//span[@class='_2ieo']")
    group_date = element_date.text

    print(group_date)
    mycursor = db.cursor()
    sql = "INSERT INTO fbgroups (name, url,creation_date) VALUES (%s, %s, %s)"
    val = (group_name, url, group_date)
    mycursor.execute(sql, val)

    db.commit()
    print("commit yay")

    # we acceess members of the group
    try:
        members_link = driver.find_element_by_xpath("//*[text()='Members']")
        members_link.click()
        time.sleep(2)
    except:
        continue

    # we scroll to load all members
    print(datetime.datetime.now().time())
    lenOfPage = driver.execute_script(
        "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    match = False
    while(match == False):
        lastCount = lenOfPage
        time.sleep(3)
        lenOfPage = driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        if lastCount == lenOfPage:
            match = True

    # now we are going to keep looping and get names and urls of all members
    try:
        elems = driver.find_elements_by_xpath(
            "//div[@class='_60ri']/a[@href]")
    except:
        continue

    members_urls = []

    for elem in elems:
        # print(elem.get_attribute("href"))
        url = elem.get_attribute("href")
        name = elem.text
        user_url = url.split('fref')[0]
        members_urls.append(user_url)
        mycursor = db.cursor()
        sql = "INSERT INTO Clients (name, url) VALUES (%s, %s)"
        try:
            val = (name, user_url)
            mycursor.execute(sql, val)
            db.commit()
        except:
            continue
    print(datetime.datetime.now().time())
    time.sleep(2)

    cur = db.cursor()
    mydict = create_dict()

    sql = 'SELECT * from Clients'

    cur.execute(sql)
    rows = cur.fetchall()

    for row in rows:
        mydict.add(row[0], ({"name": row[1], "url": row[2]}))

    stud_json.add(group_name, mydict)

    with open("data.json", 'w', encoding='utf8') as outfile:
        json.dump(stud_json, outfile, indent=2,
                  sort_keys=True, ensure_ascii=False)

    mycursor = db.cursor()
    mycursor.execute("TRUNCATE table Clients")


time.sleep(10)

driver.get(url)
time.sleep(2)
