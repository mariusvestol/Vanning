
#-*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from tkinter import *
import time
import libioplus as lio

key = {
}


cred = credentials.Certificate(key)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://vanning-334c1-default-rtdb.europe-west1.firebasedatabase.app/'
})

ref = db.reference('/')
readback = db.reference('readback')
twinError = db.reference('twinError')

bool1 = False
currentO = 1

scaleVal = float(0)


window = Tk()

label = Label(window, text=bool1)
label.pack()


tap = [
["kran1",[],1],
["kran2",[],2],
["kran3",[],3],
["kran4",[],4],
["kran5",[],5]
]

tapTime = [
["time1",[]],
["time2",[]],
["time3",[]],
["time4",[]],
["time5",[]]
]

tapPmw = [
["pmw1",[]],
["pmw2",[]],
["pmw3",[]],
["pmw4",[]],
["pmw5",[]]
]

uka = ["monday", "tuesday", "wendsday", "thursday", "friday", "saturday", "sunday"]

GPIO.setwarnings(False)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(11,GPIO.OUT)
GPIO.setup(13,GPIO.OUT)
GPIO.setup(10,GPIO.OUT)
GPIO.setup(12,GPIO.OUT)
GPIO.setup(15,GPIO.OUT)

def listener(event):
	global kran1
	global currentO
	newVal = event.data
	#print(event.path)
	if 'value' in newVal:
		if newVal['value'] == "True":
			label.config(text="True")
			pwm1.ChangeDutyCycle(scaleVal)

			if currentO > 2:
			  lio.setOdPwm(0,2,80*100)
			lio.setRelayCh(0,currentO,1)
		if newVal['value'] == "False":
			label.config(text="False")
			pwm1.ChangeDutyCycle(0)
			lio.setOdPwm(0,2,0)
			lio.setRelayCh(0,currentO,0)
			
		
	for i in range(len(tap)): 
	  if tap[i][0] in newVal:
	      tap[i][1] = newVal[tap[i][0]]
	      #print(taps[1][3])
	      
	  if tap[i][0] in event.path:
	    tap[i][1] = event.data
	    print(tap[i][1])
	    if int(readback.get()['value']) == 0: window.after(1001); readback.update({'value':'1'})
	    else: readback.update({'value':'0'}); window.after(1001);
	    twinCheck(event.data, i)
	
# twinError.update({'value':'1'})
	
	
	for t in tapTime:
	  if t[0] in event.data:
	    t[1] = event.data[t[0]]
	  if t[0] in event.path:
	    t[1] = event.data
	    if int(readback.get()['value']) == 0:
	      readback.update({'value':'1'}); window.after(1001);
	    else:
	      readback.update({'value':'0'}); window.after(1001);
	      
	for t in tapPmw:
	  if t[0] in event.data:
	    t[1] = event.data[t[0]]
	  if t[0] in event.path:
	    t[1] = event.data
	    if int(readback.get()['value']) == 0:
	      readback.update({'value':'1'}); window.after(1001);
	    else:
	      readback.update({'value':'0'}); window.after(1001);    
	
	if 'currentO' in newVal:
	  currentO = int(newVal['currentO']['value'])
	  #print(currentO)
	if 'currentO' in event.path:
	  currentO = int(event.data['value'])
	  print(currentO)
	  
	  
	if 'vann1' in event.path:
	  x = event.data['value']
	  scalePrint(x)


def twinCheck(data, i):
   tempBool = True
   for u in range(len(data)):
     tempArray = []
     for x in range(len(tap)):
       if i == x: tempArray.append(data[u])
       else: tempArray.append(tap[x][1][u])
     if len(set(tempArray)) != len(tempArray):
       tempBool = False
       findTwin(tempArray, u)
   print(tempBool)
   return(tempBool)

def findTwin(tempArray, u):
  tempString = ""
  for q in range(len(tempArray)):
    for w in range(len(tempArray)):
      if tempArray[q] == tempArray[w] and q!=w: tempString = f"Tap number {q+1} and {w+1} are both going off at {tap[q][1][u]} on {uka[u]}!"; print(tempString); twinError.update({'value':tempString}); window.after(1000);






def waterOn(tapNow, newTime, day):
  lio.setRelayCh(0,tapNow,1)
  if tapNow == tap[0][2] or tapNow == tap[1][2]:
    inputLoop(tapNow)
  else:
    if tapNow > 2:
      lio.setOdPwm(0,2,int(tapPmw[newTime][1][day])*100)
      tid = int(tapTime[newTime][1][day])*1000*60
      print(tid)
      print(int(tapPmw[newTime][1][day]))
      window.after(tid, lambda: waterOff(tapNow))
  
    

def waterOff(tapNow):
    lio.setRelayCh(0,tapNow,0)
    lio.setOdPwm(0,2,0)



#GPIO input testing

GPIO.setup(40,GPIO.IN)
print(GPIO.input(40))

def inputLoop(tapNow):
  newInp = lio.getOptoCh(0,tapNow)
  
  # if newInp == ""  else:
  
  if int(newInp) == 1:
    waterOff(tapNow)
  else:
    window.after(1000, lambda: inputLoop(tapNow))
  #window.after(1000, inputLoop)


def checkListener():
  global newListen
  if newListen is None:
    newListen = ref.listen(listener)
  else:
    if not newListen.is_alive():
      print("restaring listener")
      newListen = ref.listen(listener)
    window.after(1000, checkListener)

def timeloop():
	#global tapNow
  
	timeNow = time.localtime()
	minute = timeNow.tm_min
	second = timeNow.tm_sec
	hour = int(timeNow.tm_hour)
	day = timeNow.tm_wday
	delay = 3600 - minute*60 - second
	
	#print(timeNow)
	print("time: " + str(hour))
	print(delay)
	"""
	if len(tap[0][1]) > 5:
	  newKran = int(tap[0][1][day])
	  if newKran == hour:
	    print("VANN PAA")
	    waterOn()"""
	
	
	for i in range(len(tap)):
	  if len(tap[i][1]) > 5:
	    newKran = int(tap[i][1][day])
	    if newKran == hour:
	      print("Vann fra " + tap[i][0])
	      waterOn(tap[i][2], i, day)
	
	
	
	window.after(delay*1000, timeloop)


newListen = None
checkListener()
window.after(1000, timeloop)



#PWM testing

GPIO.setup(37,GPIO.OUT)
pwm1 = GPIO.PWM(37,1000)
pwm1.start(0)




def scalePrint(x):
  global scaleVal
  #print(x)
  scaleVal = float(x)
  #pwm1.ChangeDutyCycle(y)


scale = Scale(window, command = scalePrint)
scale.pack()



window.mainloop()
