# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import os
import pandas as pd

def info_extract(in_str):
    try :
        in_str = in_str.replace("及", ",").replace("、",",").replace("，",",").replace("：",":").replace(")","）").replace("︰",":").replace("和", ",").replace(" ","")
        in_str = in_str.split("個案編號:")[1]
        in_str = in_str.split("）")[0]
        for p in in_str.strip().split(","):
            patient_list.append(p)
            status_list.append(k)
            releasedate_list.append(release_date)
        print(release_date + ": " + k + " 共有" + str(len(in_str.split(","))) + "宗")
    except:
        print("An exception occured")

title_list = []
date_list = []
link_list = []


for i in list(range(1,5)):
    """A url string with searching result of "公立醫院2019冠狀病毒病個案最新情況" at GovHK, for press releases on or before 2022-01-03"""
    #url_str = "https://www.search.gov.hk/result?ui_lang=zh-hk&proxystylesheet=ogcio_home_adv_frontend&output=xml_no_dtd&ui_charset=utf-8&a_submit=false&query=%E5%85%AC%E7%AB%8B%E9%86%AB%E9%99%A22019%E5%86%A0%E7%8B%80%E7%97%85%E6%AF%92%E7%97%85%E5%80%8B%E6%A1%88%E6%9C%80%E6%96%B0%E6%83%85%E6%B3%81&ie=UTF-8&oe=UTF-8&site=gia_home&tpl_id=stdsearch&gp=0&gp0=gia_home&gp1=gia_home&p_size=10&num=10&doc_type=all&as_filetype=&as_q=&as_epq=&is_epq=&as_oq=&is_oq=&as_eq=&is_eq=&r_lang=&lr=&web=this&sw=1&txtonly=0&rwd=0&date_v=%23-1&date_last=%23-1&s_date_year=2022&s_date_month=01&s_date_day=01&e_date_year=2022&e_date_month=01&e_date_day=28&last_mod=&sort=date%3AD%3AL%3Ad1&page="
    """A url string with searching result of "公立醫院新型冠狀病毒病個案最新情況" at GovHK, for press releases after 2022-01-04"""
    url_str = "https://www.search.gov.hk/result?ui_lang=zh-hk&proxystylesheet=ogcio_home_adv_frontend&output=xml_no_dtd&ui_charset=utf-8&a_submit=false&query=%E5%85%AC%E7%AB%8B%E9%86%AB%E9%99%A2%E6%96%B0%E5%9E%8B%E5%86%A0%E7%8B%80%E7%97%85%E6%AF%92%E7%97%85%E5%80%8B%E6%A1%88%E6%9C%80%E6%96%B0%E6%83%85%E6%B3%81&ie=UTF-8&oe=UTF-8&site=gia_home&tpl_id=stdsearch&gp=0&gp0=gia_home&gp1=gia_home&p_size=10&num=10&doc_type=all&as_filetype=&as_q=&as_epq=&is_epq=&as_oq=&is_oq=&as_eq=&is_eq=&r_lang=&lr=&web=this&sw=1&txtonly=0&rwd=0&date_v=%23-1&date_last=%23-1&s_date_year=2022&s_date_month=01&s_date_day=01&e_date_year=2022&e_date_month=01&e_date_day=30&last_mod=&sort=date%3AD%3AL%3Ad1&page="
    page = str(i)
    url_fullstr = url_str + page
    print("Scraping page " + page)
    
    http_text = requests.get(url_fullstr).text
    soup = BeautifulSoup(http_text, "html.parser")
    
    """test"""
    for a in soup.findAll('div', attrs={'class':'item'}):
        if "冠狀病毒病" in str(a):
            title_list.append(a.find('h3').text.strip())
            link_list.append(a.find('span', attrs={'class':'itemDetailsLink'}).text)
            date_list.append(a.find('span', attrs={'class':'misc'}).find_next('span').text)
    
    """Be a responsible citizen by waiting before you hit again"""
    time.sleep(3)


df_output = pd.DataFrame({
    "Title": title_list,
    "Date": date_list,
    "Link": link_list})

df_output.to_excel('COVID19 gov press releases link.xlsx')


"""retriving releasing content for every day"""
    
patient_list = []
status_list = []
releasedate_list = []
key_words = ["出院", "危殆", "嚴重", "離世"]
    

for l in list(range(1,len(link_list))):
    """Be a responsible citizen by waiting before you hit again"""
    print("watiting 3 sec to establish...")
    print("Now scraping No." + str(l) + " of total " + str(len(link_list)))
    time.sleep(3)
    content_web = requests.get("https://" + link_list[l])
    content_web.encoding = "utf-8"
    content_soup = BeautifulSoup(content_web.text, "html.parser")
    content_str = content_soup.find('span', attrs={'id':'pressrelease'}).text
    release_date = content_soup.find('div', attrs={'class':'mB15 f15'}).find_next('div').text.split("（")[0]
    release_date = datetime.strptime(release_date, "%Y年%m月%d日").strftime("%Y-%m-%d")

    

    for s in content_str.replace("。", "，").split("，"):
        if len(s.split("個案編號")) == 2:
            is_death = True
            
            if "如下" in s:
                for i in list(range(0,len(s.split("\n")))):
                    for k in key_words:
                        if k in s.split("\n")[i]:
                            info_extract("個案編號:" + s.split("\n")[i+1] + "）")
            else:
                for k in key_words:
                    if k in s:
                        info_extract(s)
                        is_death = False
                if is_death:
                    k = key_words[3]    
                    info_extract(s)
                
        elif len(s.split("個案編號")) > 2:
            for k in key_words:
                if k in s.split("個案編號")[0]:
                    spliter = ")"
                    fix_front = ")"
                    fix_end = ""
                elif k in s.split("個案編號")[1]:
                    spliter = "個案編號："
                    fix_front = ""
                    fix_end = "個案編號："
            for ss in s.split(spliter):
                for k in key_words:
                    if k in s:
                        info_extract(fix_front + s + fix_end)


df_patients = pd.DataFrame({"Patient_id": patient_list,
                            "Status": status_list,
                            "Release_date": releasedate_list})

df_patients.to_excel('C:\\Users\\Marvin TONG\\Downloads\\Patient List.xlsx')
