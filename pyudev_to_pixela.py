#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyudev
import datetime
import urllib.request
import json

#PLEASE EDIT <username> and <x-user-token>
URL_PIXELA = 'https://pixe.la/v1/users/<username>/graphs/piano-time-graph/' 
HEADER_X_USER_TOKEN = <x-user-token>

def func():
  #initialize pyudev
  monitor = initializePyudevMonitor()
  monitor.start()

  isActiveUSB = False

  #monitor USB status
  for device in iter(monitor.poll, None):

    if device.action == 'add' and isActiveUSB is not True:
      #detect active
      isActiveUSB = True
      dt_start = datetime.datetime.now()
      print("active:" + str(dt_start))

    if device.action == 'remove' and isActiveUSB:
      #detect inactive
      isActiveUSB = False
      dt_end = datetime.datetime.now()
      print("inactive:" + str(dt_end))

      active_time = computeActiveTime(dt_start, dt_end)

      #https request to Pixela
      putRequestToPixela(dt_start, str(active_time))

def initializePyudevMonitor():
  context = pyudev.Context()
  monitor = pyudev.Monitor.from_netlink(context)
  monitor.filter_by(subsystem='usb')
  return monitor

def computeActiveTime(dt_start, dt_end):
  #compute this active time
  t_elapsed = dt_end - dt_start
  this_active_time = round(float(t_elapsed.seconds) / 60.0, 2)

  #compute last active time
  last_quantity = getRequestToPixela(dt_start)
  if last_quantity is None:
    last_active_time = 0.0
  else:
    last_active_time = float(getRequestToPixela(dt_start))
  print("last_active_time"+str(last_active_time))

  #compute active time
  active_time = this_active_time + last_active_time

  return active_time

def getRequestToPixela(date):
  url = URL_PIXELA + date.strftime('%Y%m%d')
  headers = {
      'X-USER-TOKEN': HEADER_X_USER_TOKEN,
  }
  data = None

  body = https_request(url,headers,data,'GET')
  print(body)

  if body is not None:    
    return json.loads(body)['quantity']


def putRequestToPixela(date, quantity):
  url = URL_PIXELA + date.strftime('%Y%m%d')
  headers = {
      'X-USER-TOKEN': HEADER_X_USER_TOKEN,
  }
  data = {
    "quantity" : quantity,
  }
  https_request(url,headers,data,'PUT')


def https_request(url, headers, data, method):
  print(url)
  print(data)
  print(headers)
  print(method)
  if data is None:
    req = urllib.request.Request(url=url, headers=headers, method=method)
    print(data is None)
  else:
    req = urllib.request.Request(url=url, data=json.dumps(data).encode(), headers=headers, method=method)
    print(json.dumps(data).encode())

  try:
    with urllib.request.urlopen(req) as res:
      body = res.read()
  except urllib.error.HTTPError as err:
      body = None
      print(err.code)
  except urllib.error.URLError as err:
      body = None
      print(err.reason)

  return body

if __name__ == '__main__':
    func()