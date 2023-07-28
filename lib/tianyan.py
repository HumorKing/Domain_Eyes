import requests
from lib import tools,config
import time
from urllib import parse
import re
from lxml import etree
from rich.console import Console

console = Console()


UA=config.UA
cookie={
	"auth_token":f"{config.tianyan_token}"
}


def get_company_id(name):
    url = "https://www.tianyancha.com/search/?key=" + parse.quote(name)
    text_page=requests.get(url=url,headers=UA,cookies=cookie).content.decode()
    src = etree.HTML(text_page)
    try:
      company_id=src.xpath('//a[@class="index_alink__zcia5 link-click"]/@href')[0]
    except:
       console.print("尝试自动验证码识别！",style='green')
       bp=tools.Bypass()
       bp.bypass()
       if '身份验证' in requests.get(url=url,headers=UA,cookies=cookie).text:
        console.print("自动识别错误！请前往天眼查手动进行图形验证->https://www.tianyancha.com/search/?key=",style='red')
       exit()
       #get_company_id(name)
       
    return company_id.replace('https://www.tianyancha.com/company/','')

def get_page(total):
   if int(total) % 50 != 0: 
      page=(int(total) // 50)+1
   else:
      page=(int(total) // 50)
   return page

def get_total(ty_id):
    time_=str(int(time.time()*100))
    data={"gid":f"{ty_id}","pageSize":10,"pageNum":1,"province":"-100","percentLevel":"-100","category":"-100"}
    url=f"https://capi.tianyancha.com/cloud-company-background/company/investListV2?_={time_}"
    url2=f"https://capi.tianyancha.com/cloud-company-background/company/branchList?gid={ty_id}"
    res=requests.post(url=url,headers=UA,cookies=cookie,json=data)
    res2=requests.get(url=url2,headers=UA,cookies=cookie)
    total1=res.json()['data']['total']
    total2=res2.json()['data']['total']
    total=[total1,total2]
    return total


def get_all_company(ty_id,percent):
    company=[]
    data_num=get_total(ty_id)
    data_num1=data_num[0]
    data_num2=data_num[1]
    for ii in range(1,get_page(data_num1)+1):
      data={"gid":f"{ty_id}","pageSize":50,"pageNum":f"{ii}","province":"-100","percentLevel":"-100","category":"-100"}
      url=f"https://capi.tianyancha.com/cloud-company-background/company/investListV2?_="
      res=requests.post(url=url,headers=UA,cookies=cookie,json=data)
      temp=res.json()['data']['result']
      company+=temp
    for jj in range(1,get_page(data_num2)+1):
      url=f"https://capi.tianyancha.com/cloud-company-background/company/branchList?gid={ty_id}"
      res=requests.get(url=url,headers=UA,cookies=cookie)
      temp=res.json()['data']['result']
      company+=temp
    company,ids=tools.output_company_id(company,percent)  
    return company,ids

def get_icp_domain(company_id):
    url=f'https://www.tianyancha.com/pagination/icp.xhtml?id={company_id}'
    text_page=requests.get(url=url,headers=UA,cookies=cookie).text
    src=etree.HTML(text_page)
    '''icp=src.xpath('//td[@class="left-col"]/span/text()')
    while 1:
      try:
        icp.remove('-')
      except:
         break'''
    try:
      domain=src.xpath('//td[@class="left-col"]/text()')
    except:
       domain=''   
    return domain

def is_safe_company(info):
   is_safe=''
   keyword=['信息服务','软件开发','信息技术','IT','技术开发','计算机系统']
   for i in keyword:
      if i in info:
         is_safe=True
      else:
         is_safe=False
   return is_safe

def get_company_info(name):
  cookie={'BAIDUID':f'{config.aqc_token}'}
  url='https://aiqicha.baidu.com/s?q=' + parse.quote(name)
  try:
    text_page=requests.get(url=url,cookies=cookie,headers=UA).text
    re1=re.compile(r'"pid":"(\d*)"')
    pid=re1.search(text_page).group(1)
    url2=f"https://aiqicha.baidu.com/detail/basicAllDataAjax?pid={pid}"
    text_page=requests.get(url=url2,cookies=cookie,headers=UA)
    try:
      company_info=text_page.json()['data']['basicData']['scope']
    except:
      company_info='' 
    #print(company_info)
    is_safe=is_safe_company(company_info)
  except:
    console.print("请前往爱企查手动进行图形验证->https://aiqicha.baidu.com/s?q=",style='red')
    is_safe=False 
  return is_safe

'''def get_company_info(ty_id):
   url=f"https://capi.tianyancha.com/cloud-company-background/company/changeinfoEm?gid={ty_id}"
   text_page=requests.get(url=url,cookies=cookie,headers=UA).text
   print(text_page)
   try:
    company_info=json.loads(text_page)["data"]["result"][0]
   except:
      console.print("该公司无介绍",style='red')
      company_info=''
   is_safe=is_safe_company(company_info)
   return is_safe'''