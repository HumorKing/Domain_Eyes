# -*- coding: utf-8 -*-
from io import BytesIO
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from PIL import Image
from lib import config
import platform
import random
from rich.console import Console

console = Console()

class Bypass():
  def screen_scale_rate(self):
    """获取缩放后的分辨率"""
    if ('Windows' == platform.system()):
        from win32 import win32api, win32gui, win32print
        from win32.lib import win32con
        sX = win32api.GetSystemMetrics(0)   #获得屏幕分辨率X轴
        sY = win32api.GetSystemMetrics(1)   #获得屏幕分辨率Y轴
        # print(sY)
        """获取真实的分辨率"""
        hDC = win32gui.GetDC(0)
        x = win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)  # 横向分辨率
        y = win32print.GetDeviceCaps(hDC, win32con.DESKTOPVERTRES)  # 纵向分辨率
        # print(y)
        # 缩放比率
        screen_scale_rate = round( y/ sY, 2)
        # screen_scale_rate=self.screen_rate
        # print('屏幕缩放比为：',screen_scale_rate)
    else:
        screen_scale_rate=1
    return screen_scale_rate

  def __init__(self):
     self.screen_rate=float(self.screen_scale_rate())
     self.cookie_dict = {
#              'domain': '.tianyancha.com',
              'name': 'auth_token',
              'value': f'{config.tianyan_token}'
#              "expires": '',
#              'path': '/',
#              'httpOnly': False,
#              'HostOnly': False,
 #             'Secure': False
          }
     self.url = 'https://www.tianyancha.com/search?key='
  def compare_pixel(self,image1, image2, i, j):
      #判断两个像素是否相同
      #返回的值是RGB的值
      #i和j表示图片的横坐标和纵坐标
      pixel1 = image1.load()[i, j]
      pixel2 = image2.load()[i, j]

      #阈值
      threshold = 80

      if abs(pixel1[0] - pixel2[0])<threshold and abs(pixel1[1] - pixel2[1])<threshold and abs(pixel1[2] - pixel2[2])<threshold:
          return True
      else:
          return False
  def get_slide_track(self,distance):
        distance=int(distance)
        if not isinstance(distance, int) or distance < 0:
            raise ValueError(f"distance类型必须是大于等于0的整数: distance: {distance}, type: {type(distance)}")
        # 初始化轨迹列表
        slide_track = [
            [random.randint(-50, -10), random.randint(-50, -10), 0],
            [0, 0, 0],
        ]
        # 共记录count次滑块位置信息
        count = 30 + int(distance / 2)
        # 初始化滑动时间
        t = random.randint(50, 100)
        # 记录上一次滑动的距离
        _x = 0
        _y = 0
        for i in range(count):
            # 已滑动的横向距离
            x = round(self.__ease_out_expo(i / count) * distance)
            # 滑动过程消耗的时间
            t += random.randint(10, 20)
            if x == _x:
                continue
            slide_track.append([x, _y, t])
            _x = x
        slide_track.append(slide_track[-1])
        del slide_track[0]
        result=[]
        for i in range(len(slide_track)-1):
             result.append(slide_track[i+1][0]-slide_track[i][0])
        return result   # 大数组，滑动时间
  def __ease_out_expo(self,sep):
        if sep == 1:
            return 1
        else:
            return 1 - pow(2, -10 * sep)

  def bypass(self):
      #打开页面
      driver = webdriver.Chrome()
      driver.get(self.url)
      driver.add_cookie(cookie_dict=self.cookie_dict)
      driver.get(self.url)
      driver.maximize_window()  
      
      #获取图片左上角位置以及图片大小
      time.sleep(3)
      img = driver.find_element(By.CSS_SELECTOR,'#captcha > div.gt_holder.gt_custom > div.gt_widget > div.gt_box_holder > div.gt_box')
      location = img.location
      #print("图片的位置", location)
      size = img.size
      #得到图片的坐标
      top, buttom, left, right = location["y"], location["y"]+size["height"], location["x"], location["x"]+size["width"]
      #print(top, buttom, left, right)

      #截取滑块验证码的完整图片
      scrennshot = driver.get_screenshot_as_png()
      scrennshot = Image.open(BytesIO(scrennshot))
      captcha1 = scrennshot.crop((int(left)*self.screen_rate, int(top)*self.screen_rate, int(right)*self.screen_rate, int(buttom)*self.screen_rate))
      captcha1.save('./yanzhengma.png')
      #print('保存成功')

      #单击滑块按钮得到缺口图片并截图
      slider = driver.find_element(By.CSS_SELECTOR,'#captcha > div.gt_holder.gt_custom > div.gt_slider > div.gt_slider_knob.gt_show')
      ActionChains(driver).click_and_hold(slider).perform()
      time.sleep(3)
      scrennshot = driver.get_screenshot_as_png()
      scrennshot = Image.open(BytesIO(scrennshot))
      captcha2 = scrennshot.crop((int(left)*self.screen_rate, int(top)*self.screen_rate, int(right)*self.screen_rate, int(buttom)*self.screen_rate))
      captcha2.save('./yanzhengma2.png')
      time.sleep(2)

      #从滑块的右侧开始逐一比对RGB值来寻找缺口位置
      left =80
      has_find = False
      #i和j分别是图片的横坐标和纵坐标
      captcha1=Image.open("./yanzhengma.png")
      captcha2=Image.open("./yanzhengma2.png")
      #print('长度',captcha1.size[0])
      for i in range(left, int(captcha1.size[0])):
          if has_find:
              break
          for j in range(captcha1.size[1]):
              if not self.compare_pixel(captcha1, captcha2, i, j):
                  left = i    #进入这个if条件即表示寻到了缺口所在的位置，将缺口的横坐标赋值给left
                  has_find = True
                  break

      #需要移动的距离减去滑块距离左边边框的位置从而得到实际需要移动的距离
      #print(f'横坐标：{left}')
      move = (left - 10)/self.screen_rate
      #print("move",move)
      tracks=self.get_slide_track(move)      #拖动滑块到缺口位置
      for track in tracks:
        ActionChains(driver).move_by_offset(xoffset=track, yoffset=0).perform()
      # time.sleep(1)
      ActionChains(driver).pause(0.7).perform()
      ActionChains(driver).release().perform()
      time.sleep(2)



def output_company_id(data,percent):
    result=[]
    ids=[]
    if data:
      for i in data:
          if i['regStatus'] !='注销':
            try:
                percent_=i['percent'].replace('-','0%').replace('%','')
            except:
                percent_=100
            if int(float(percent_)) >= int(percent):
              temp=[]
              temp.append(i['name'])
              console.print("[+]",i['name'],style="green")
              temp.append(percent_)
              temp.append(i['id'])
              ids.append(i['id'])
              result.append(temp)
    return result,ids    

def quchong(filedir):
    with open(filedir,'r') as F:
          a=(F.readlines())
          a=set(a)
          with open(filedir,'w',encoding='utf-8') as W:
            for i in a:
              print(i)
              W.write(i)

