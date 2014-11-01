#coding: gbk
import os
import _winreg
import win32gui
import win32api
import win32con
import subprocess
import time
from xml.etree import ElementTree
from ctypes import windll
import re
import commands
import sys
import shutil
import re

from common.path_mgmt import PathMgmt
from common.application import Application
from TestResultApi import TestResultApi, TestCase

gLogMode = "-V" # -V -S

gTitle1 = 'title1'
gTitleDNA1 = 'title2'
gImagePath = 'image'

urlConfig = 'URLConfig1.xml'

currPath = os.path.split(sys.argv[0])[0]

path_mgmt = PathMgmt()
path_mgmt.change_cur_dir(sys.argv[0])

print "argc:%s" % len(sys.argv);
print "argv:%s" % sys.argv[1:];

task_id = '-1'
center_id = '-1'
verify_serial_no = '-1'
verify_type_name = 'BRautotest'
job_name = '-'
build_num = '-1'
mgr_url = ''
test_job_name = '-'

if len(sys.argv) < 12:
	print 'Usage:%s  -T TaskId -C CenterID -S vsn -J JobName -B BuildNum -U url -L TestJobName' % (os.path.basename(sys.argv[0]))
	sys.exit(-1)
else:
	if sys.argv.count('-T') == 1:
			task_id = sys.argv[sys.argv.index('-T') + 1]
			
	if sys.argv.count('-C') == 1:
			center_id = sys.argv[sys.argv.index('-C') + 1]

	if sys.argv.count('-S') == 1:
			verify_serial_no = sys.argv[sys.argv.index('-S') + 1]

	if sys.argv.count('-J') == 1:
			job_name = sys.argv[sys.argv.index('-J') + 1]

	if sys.argv.count('-B') == 1:
			build_num = sys.argv[sys.argv.index('-B') + 1]

	if sys.argv.count('-U') == 1:
			mgr_url = sys.argv[sys.argv.index('-U') + 1]
			
	if sys.argv.count('-L') == 1:
			test_job_name = sys.argv[sys.argv.index('-L') + 1]    

print "Trunk Name:%s" % job_name;
print "Job Name:%s" % test_job_name;
print "Build ID:%s" % build_num;
print "Packge Url:%s" % mgr_url;

trunk_name = job_name
build_id = build_num
download_url = mgr_url


tapi = TestResultApi(task_id,center_id,verify_serial_no,verify_type_name,job_name,build_num)


def IsVisibleWnd(hwnd, wndLst):
	if(win32gui.IsWindowVisible(hwnd)):
		wndLst.append(hwnd)

def GetHwndByTitle(title):
	wndLst = []
	win32gui.EnumWindows(IsVisibleWnd, wndLst)
	for hwnd in wndLst:
		wndTitle = win32gui.GetWindowText(hwnd)
		if wndTitle.find(title) != -1:
			return hwnd
	return 0

def CloseWindow(hwnd):
	try:
		(left, top, right, bottom) = win32gui.GetWindowRect(hwnd)
	except:
		print 'GetWindowRect failed'
		return 0
	xx = right - 10
	yy = top + 10
	cmd = 'leftClick.exe %s %s' % (xx, yy)
	print 'left click : cmd = %s' % cmd
	p = subprocess.Popen(cmd)
	p.wait()

def CloseWindowDNA(hwnd):
	try:
		(left, top, right, bottom) = win32gui.GetWindowRect(hwnd)
	except:
		print 'GetWindowRect failed'
		return 0
	xx = right - 30
	yy = top + 30
	cmd = 'leftClick.exe %s %s' % (xx, yy)
	print 'left click : cmd = %s' % cmd
	p = subprocess.Popen(cmd)
	p.wait()

def GrabScreenImage(filename):
	width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
	height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
	image_name = '%s.png' % filename
	pic_path = '%s/%s' % (gImagePath, image_name)
	print 'image_name = %s, pic_path = %s' % (image_name, pic_path)
	dll = windll.LoadLibrary('CCommonFunDll.dll')
	dll.CF_CutScreenToFile(0, 0, width, height, pic_path)
	time.sleep(2)

def GrabWindowImage(hwnd, filename):
	print 'grab image'
	try:
		(left, top, right, bottom) = win32gui.GetWindowRect(hwnd)
	except:
		print 'GetWindowRect failed'
		return 
	
	image_name = '%s.png' % filename
	pic_path = '%s/%s' % (gImagePath, image_name)
	print 'image_name = %s, pic_path = %s' % (image_name, pic_path)
	dll = windll.LoadLibrary('CCommonFunDll.dll')
	dll.CF_CutScreenToFile(left, top, right, bottom, pic_path)
	time.sleep(2)

def ExecCmd(cmd):
	p = subprocess.Popen(cmd)

class NetMonitorTest:
	def __init__(self, url, type):
		self.url = url
		self.type = type
		self.currentTestCase = ''
		self.log = ""
		
	def VerifyTips(self):
		for i in range(1, 5):
			hWnd1 = GetHwndByTitle(gTitle1)
			hWndDNA1 = GetHwndByTitle(gTitleDNA1)
			if hWnd1 != 0:
				hWnd = hWnd1
				gTitle = gTitle1
				filename = re.sub('[/?:.]','_',self.url)
				if hWnd != 0:
					GrabWindowImage(hWnd, filename)
					for j in range(1, 5):
						CloseWindow(hWnd)
						hWnd = GetHwndByTitle(gTitle)
						if hWnd == 0:
							break
						else:
							time.sleep(1)
					return True
				else:
					GrabScreenImage(filename)
					time.sleep(1)
			elif hWndDNA1 !=0:
				hWnd = hWndDNA1
				gTitle = gTitleDNA1
				filename = re.sub('[/?:.]','_',self.url)
				if hWnd != 0:
					GrabWindowImage(hWnd, filename)
					for j in range(1, 5):
						CloseWindowDNA(hWnd)
						hWnd = GetHwndByTitle(gTitle)
						if hWnd == 0:
							break
						else:
							time.sleep(1)
					return True
				else:
					GrabScreenImage(filename)
					time.sleep(1)
		return False

	def IsFileExist(self):
		if os.path.isfile('NetMoniterTest_*') and (self.type !=0):
			return True
		else:
			return False
		
	def ResetLog(self):
		self.log = ""

	def AddLog(self, logStr):
		self.log += logStr
		self.log += "\n"
	
	def RecordResult(self, result):
		if result == 'Pass':
			if (gLogMode == '-V'):
				print self.log
			
		else:
			if (gLogMode != '-S'):
				print self.log
		print self.currentTestCase, ":", result
		if result == 'Pass':
			case = TestCase("XPSP3_Net",self.currentTestCase,tapi)
			case.SetResult(result)
			case.flushResultToDB()
		elif result == 'Fail':
			case = TestCase("XPSP3_Net",self.currentTestCase,tapi)
			case.SetResult(result)
			case.SetLog(self.log)
			case.flushResultToDB()

	def RunNetTool(self, url):
		newToolName = 'nettool_' + time.strftime('%Y%m%d%H%M%S') + r'.exe'
		filename = 'NetMoniterTest_' + time.strftime('%Y%m%d%H%M%S')
		try:
			shutil.copyfile(r'nettool.exe', newToolName)
			time.sleep(0.5)
		except:
			pass
		cmdLine = newToolName + ' ' + url + ' ' + filename
		self.AddLog("CmdLine: " + cmdLine)
		ret = ExecCmd(cmdLine)
		time.sleep(2)
		
	def UrlTest(self):
		self.ResetLog()
		if self.type == '1':
			self.currentTestCase = 'ReceiveTest ' + self.url
		elif self.type == '2':
			self.currentTestCase = 'DownloadTest ' + self.url
		elif self.type == '0':
			self.currentTestCase = 'WhiteURLTest ' + self.url
		
		self.RunNetTool(self.url)
		
		if self.type !=0:
			if self.VerifyTips() == False:
				self.AddLog("No tips window")
				self.RecordResult('Fail')
				return
			if self.IsFileExist():
				self.AddLog("blackfile is in local")
				self.RecordResult('Fail')
			else:
				self.AddLog("blackfile is not in local")
				self.RecordResult('Pass')
	
	def Run(self):
		print "\nCurrently testing:", self.url
		self.UrlTest()
		try:
			os.system("del nettool_*.exe")
		except:
			pass
	
if __name__ == '__main__':
		
	if not os.path.exists(gImagePath):
		os.mkdir(gImagePath)

	fileObject1 = open(urlConfig)
	fileObject2 = open(urlConfig+'_2.xml', 'w')
	for line in fileObject1:
		if line.find(r"<URL_ITEM") != -1 or line.find(r"CASE_CONFIG") != -1:
			fileObject2.write(line)
	fileObject1.close()
	fileObject2.close()

	root = ElementTree.parse(urlConfig+'_2.xml')
	lstMonitorItems = root.getiterator('URL_ITEM')
	for monitorItem in lstMonitorItems:
		print lstMonitorItems
		url = monitorItem.attrib['Name']
		type = monitorItem.attrib['Type']
		netMonitorItem = NetMonitorTest(url, type)
		netMonitorItem.Run()
		
		
		
		
		
		
		
