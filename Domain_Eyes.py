import argparse
import sys
from lib import tianyan,config,tools
from rich.console import Console

console = Console()

def banner():
    msg = '''                                                                                                           
        =@@@@@\.                                     =@@`                       ,@@@@@@@/                           
        @@^ .\@@`                                    ,\[                        =@@.                                
       .@@^   @@@  ./@@@\.  =@@/@@\./@@@`   ,@@@/@@. @@^ =@@/@@@`               /@/     =@@   ,@@` ,@@@@`  ./@@@\   
       =@@.   @@@ ,@@` =@@  /@@` @@@` \@@  @@/.,@@@ .@@` =@@` \@@               @@^     .@@.  @@^ @@/..@@^ @@^ =@@  
       /@@    @@^ @@^  .@@` @@^  @@^  @@^ =@@   @@^ =@@  @@^  @@^              =@@@@@@@  @@^ =@/ =@@   @@^ @@\.     
       @@^   ,@@^=@@.  =@@.=@@. ,@@.  @@^ @@^  .@@` /@^ ,@@.  @@^              =@@       @@^,@@. @@@@@@@@^  \@@\    
      =@@`   @@/ =@@   /@/ =@/  =@@  =@@  @@^  =@@  @@^ =@@  =@@               @@^       =@^@@`  @@^          \@@   
      =@@  ]@@/  =@@. =@@. @@^  @@^  =@/  @@^ ,@@^ =@@. @@^  =@/              .@@^       =@@@^   @@^ ./@^=@@  =@@   
      @@@@@@/.    ,@@@@/. .@@.  @@^  @@^  ,@@@@@@^ =@@  @@^  @@               =@@@@@@@/   @@@    ,@@@@@`  ,@@@@/.   
                                                                ^^^^^^^^^^^^^^^           ,@@.                                                                                                                               
    '''

    console.print(msg, style="bold red")

banner()
class Run():
    def __init__(self,name,percunt,deep):
         self.name=name
         self.percent=int(percunt)
         self.deep=int(deep)
         self.all_company=[]
    def deep_company(self,ty_id,deep):  
        deep-=1
        company,ids = tianyan.get_all_company(ty_id,self.percent)   
        self.all_company+=company
        if ids:   
            for el in ids:   
                if deep<=0:
                     break
                self.deep_company(el,deep+1)    #重新调用次函数,不过参数为新的路径名
    
    def run(self):
        with open(f'./result/{self.name}.csv','a') as W:
            W.write('企业名称,天眼查ID,域名,是否为供应商\n')
            ty_id=tianyan.get_company_id(self.name)
            self.all_company.append([self.name,ty_id,tianyan.get_icp_domain(ty_id)])
            console.print(self.name,style="green")
            self.deep_company(ty_id,self.deep)
            for j in self.all_company:
                    company_name=j[0]
                    ty_id=j[2]
                    is_safe=tianyan.get_company_info(company_name)
                    domain=tianyan.get_icp_domain(ty_id)
                    temp=[company_name,ty_id,domain,is_safe]
                    console.print(temp,style="bold red")
                    for i in temp:
                        i=str(i).replace(',','，').replace('[','').replace(']','').replace("\'",'')
                        W.write(str(i)+',')
                    W.write('\n') 
            #tools.quchong(f'./result/{self.name}.csv')
if not (config.aqc_token+config.tianyan_token):
     console.print("请修改config.py配置文件！",style="red")
     exit()
parser = argparse.ArgumentParser(description='企业资产收集')
parser.add_argument('--name', '-n', help='企业名称')
parser.add_argument('--deep', '-d', help='企业递归层数(默认两层)',default=2)
parser.add_argument('--percent', '-p', help='占股百分比(默认50)',default=50)
parser.add_argument('--file','-f',help='批量地址')
args = parser.parse_args()
if not args.file:
    task=Run(args.name,args.percent,args.deep)
else:
     with open(args.file,'r',encoding='utf-8') as F:
          for target in F.readlines():
               target=target.strip()
               task=Run(target,args.percent,args.deep)
task.run()