# -*- coding: utf-8 -*-
"""
Created on Wed Feb  2 20:57:05 2022

@author: Marvin TONG

This Scirpt is aim to retrive COVID patient data from HKgov press release website.
(Releasing with title: "公立醫院2019冠狀病毒病個案最新情況")
The gov will publish daily report for how many patients has discharged or pasted.
And they will mentioned if any patients are currently in critical or serious situation.
Compare those info with comfirmed COVID patients data, we might have better insight 
for the ongoing epidemic.
"""

import requests
from bs4 import BeautifulSoup
import datetime
import time
import os
import pandas as pd
import pygsheets as pygs

key_words = ["出院", "嚴重", "危殆", "離世", "死亡"]
patient_list = []
status_list = []
releasedate_list = []
link_list = []
exception_list = []
""" For input string containning patient ids, replace all punctuation to ",", 
    remove the heading before "個案編號:", and the tail after "）", 
    split the string with ',' then we can get every id separated"""
    
"""
def info_extract(in_str, key_word):
    try :
        # replace all punctuation with ",", keep ":" $ ")" in half shape in order to remove heading and tails
        # append patient detail and id to lists
        for p in in_str.strip().split(","):
            patient_list.append(p)
            status_list.append(key_word)
            releasedate_list.append(release_date)
            link_list.append(content_link)
        # print 
        print(release_date + ": " + key_word + " 共有" + str(len(in_str.split(","))) + "宗")
    except:
        print("An exception occured")
"""


def content_reader (link):
    """Be a responsible citizen by waiting before you hit again"""
    print("watiting 3 sec to establish...")
    time.sleep(3)
    content_web = requests.get(link)
    content_web.encoding = "utf-8"
    content_soup = BeautifulSoup(content_web.text, "html.parser")
    content_str = content_soup.find('span', attrs={'id':'pressrelease'}).text
    release_date = content_soup.find('div', attrs={'class':'mB15 f15'}).find_next('div').text.split("（")[0]
    release_date = datetime.datetime.strptime(release_date, "%Y年%m月%d日").strftime("%Y-%m-%d")

    

    for s in content_str.replace("。", "，").replace("；", "，").split("，"):
        print(s)
        if any(k in s for k in key_words) and "個案編號" in s:
            print("info detected")
            if "如下" in s:
                print("its a table")
                for i in list(range(0,len(s.split("\n")))):
                    for k in key_words:
                        if k in s.split("\n")[i]:
                            id_reader(k +"個案編號:" + s.split("\n")[i+1] + "）")
            else:
                print ("its a string")
                id_reader(s)
                        
"""                
        elif len(s.split("個案編號")) > 2:
            for k in key_words:
                if k in s.split("個案編號")[0]:
                    spliter = ")"
                    fix_front = ""
                    fix_end = ")"
                else:
                    spliter = "個案編號"
                    fix_front = "個案編號"
                    fix_end = ""
            for ss in s.split(spliter):
                for k in key_words:
                    if k in ss:
                        info_extract(fix_front + ss + fix_end, k)
                    elif ("及" in ss or "和" in ss) and k in s:
                        info_extract(fix_front + ss + fix_end, k)
"""
            
def id_reader (in_str):
        df_compare = pd.DataFrame({'str': [in_str[i]+in_str[i+1] for i in list(range(0, len(in_str)-1))]},
                                   index = [wd in key_words for wd in [in_str[i]+in_str[i+1] for i in list(range(0, len(in_str)-1))]])
        print("The key word follows:")
        print(df_compare.loc[True].values[0])
        if len(df_compare.loc[True]) > 0:    
            for i in list(range(0, len(df_compare.loc[True]))):
                try: 
                    adj_str = in_str.replace("及", ",").replace("、",",").replace("，",",").replace("：",":").replace(")","）").replace("︰",":").replace("和", ",").replace(" ","")
                    adj_str = adj_str.split("個案編號:")[1+i].split("）")[0]
                    for p in adj_str.strip().split(","):
                        patient_list.append(p)
                        print(p)
                        status_list.append(df_compare.loc[True].iloc[i].values[0])
                        print(df_compare.loc[True].iloc[i].values[0])
                        releasedate_list.append(release_date)
                        link_list.append(content_link)
                    print(release_date + ": " + df_compare.loc[True].iloc[i].values[0] + " 共有" + str(len(adj_str.split(","))) + "宗")
                except:
                    exception_list.append(content_link)
                    print(" An exception occured")

read_until = "2020-02-01"
date_dis = datetime.datetime.now() - datetime.datetime.strptime(read_until, "%Y-%m-%d")

for d in list(range(1,date_dis.days+1)):
    today_str = (datetime.date.today()-datetime.timedelta(d))
    link_str = "https://www.info.gov.hk/gia/general/" + today_str.strftime("%Y%m/%d") + "c.htm"
    release_date = today_str.strftime("%Y-%m-%d")
    
    """Be a responsible citizen by waiting before you hit again"""
    print("watiting 3 sec to establish...")
    web_req = requests.get(link_str)
    web_req.encoding = "utf-8"
    web_soup = BeautifulSoup(web_req.text, "html.parser")
    
    for a in web_soup.findAll('a', attrs={'class':'NEW'}):
        if "冠狀病毒病個案最新情況" in a.text:
            content_link = "https://www.info.gov.hk" + a['href']
            print("Now scraping COVID 19 cases updated on " + today_str.strftime("%Y-%m-%d"))
            content_reader(content_link)

patient_result = pd.DataFrame({"Patient_id":    patient_list,
                               "Status":        status_list,
                               "Release_date":  releasedate_list,
                               "Reference_link":link_list})
#Download COVID cases details, !!!CHP has suspended update on 06-02-2022
xl_url = "https://www.chp.gov.hk/files/xls/previous_cases_covid19_tc.xlsx"
patient_detail = pd.read_excel(xl_url, usecols=[0,1,2,3,4,5,6,7,8])
#"""Back up scraped data by write to excel"""
patient_result.to_excel("patient_result.xlsx")
patient_detail.to_excel("previous_COVID_19_cases.xlsx")

#"""Rename & as dtypes to match colnames with df.patient_result"""
patient_detail = patient_detail.rename(columns={'個案編號': 'Patient_id'})
patient_result['Patient_id'] = patient_result['Patient_id'].astype(str)
patient_detail['Patient_id'] = patient_detail['Patient_id'].astype(str)

#"""Find most recently date as D-day, indicate when of the patients Discharged/Death"""
patient_result["D-day"] = [patient_result[patient_result["Patient_id"] == pid]["Release_date"].max() for pid in patient_result['Patient_id']]
#"""Find out how serious of patient"""
patient_result["to_sort"] = [key_words.index(st) for st in patient_result['Status']]

"""
sort_list = []
date_max = []
#Find most recently date as D-day, indicate when of the patients Discharged/Death
for pid in patient_result['Patient_id']:
    date_max.append(patient_result[patient_result["Patient_id"] == pid]["Release_date"].max())
#Find out how serious of patient
for st in patient_result['Status']:
    sort_list.append(key_words.index(st))
#Combine data to dataframe
patient_result["to_sort"] = sort_list
patient_result["D-day"] = date_max
"""

#"""Sort by patient status, remove duplicated, drop.na"""
patient_result.sort_values("to_sort", inplace = True)
patient_result.drop_duplicates("Patient_id", keep = "last", inplace = True)
patient_result.dropna(subset = ['Patient_id'], inplace = True)
#merge data and output
output_df = patient_detail.merge(patient_result[['Patient_id', 'Status', 'D-day', 'Reference_link']], how='left', on='Patient_id')

gs_auth = pygs.authorize(service_account_file=("C:\\task_scheduler\\pygsheets-creds.json"))
"""Create new google spreadsheet at first time"""

gwb = gs_auth.create("HK_COVID_patients")
ppwks = gwb.add_worksheet("Patient_progress", rows = len(output_df.index))
ppwks.set_dataframe(output_df,(1,1))
pdwks = gwb.add_worksheet("Patient_detail", rows = len(patient_detail.index))
pdwks.set_dataframe(patient_detail, (1,1))
gwb.share("tsk.bgihk@gmail.com", role='writer')

output_df.to_excel('Patient List merged.xlsx')
