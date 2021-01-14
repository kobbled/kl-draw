# This script will plot draw objects from a fanuc controller
# Must input the robot's ip, and the name of the draw object
# The program must have been previously run and populated.

# ..todo:: implement with karel sockets for handshake with fanuc
# controller.

#ftplib ref: http://zetcode.com/python/ftp/
import os
import sys
import time
import socket
import ftplib
from ftplib import FTP
import re
from random import randint
import matplotlib.path as mpath
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

#ftp parameters
ROBOT_IP = '127.0.0.1'
ROBOT_PORT = 80
USERNAME = ""
PASSWORD = ""

DRAWING_OBJECT = 'TSTPOLY'
#DRAWING_OBJECT = 'TEST_DRAW'
SAVE_DIRECTORY = 'plots'

CONTOUR_VARNAME = 'CONTOURS'
CONTOUR_VEC_SUFFIX = 'V'
CONTOUR_CODE_SUFFIX = 'CODE'

LINES_VARNAME = 'LINES'
LINE_START_SUFFIX = 'R0'
LINE_END_SUFFIX = 'R1'

#pattern1 = r"Field: {LINES_VARNAME}\.NODEDATA\[(\d{1,5})\]\.{LINE_START_SUFFIX} Access: RW: VECTOR =\s*(.*)"
#pattern2 = r"Field: {LINES_VARNAME}\.NODEDATA\[(\d{1,5})\]\.{LINE_END_SUFFIX} Access: RW: VECTOR =\s*(.*)"

folder_files = ''

raster_lines = []
polygons = []

def random_color_gen():
  """Generates a random RGB color
  
  :return: 3 elements in the form [R, G, B]
  :rtype: list
  """
  r = randint(0, 255)
  g = randint(0, 255)
  b = randint(0, 255)
  return (r, g, b)

def parseContour():

  parsefile = folder_files +'/' + SAVE_DIRECTORY + '/' + DRAWING_OBJECT + '.VA'

  pattern_code = rf"Field: {CONTOUR_VARNAME}\.NODEDATA\[(\d+)\]\.{CONTOUR_CODE_SUFFIX} Access: RW: INTEGER =\s*(.*)"
  pattern_vector = rf"Field: {CONTOUR_VARNAME}\.NODEDATA\[(\d+)\]\.{CONTOUR_VEC_SUFFIX} Access: RW: VECTOR =\s"
  patternx = r"X:\s*(-?\d{0,3}\.\d{1,3})"
  patterny = r"Y:\s*(-?\d{0,3}\.\d{1,3})"

  with open(parsefile,'r') as f:

    lines = f.readlines()
    for i in range(len(lines)):

      m2 = re.search(pattern_code, lines[i])
      m1 = re.search(pattern_vector, lines[i])

      if m1:
        # get index
        nid = int(m1.group(1)) - 1
        # get x coordinate
        mvec = re.search(patternx, lines[i+1])
        new_x = 0.0
        if mvec:
          new_x = float(mvec.group(1))
        # get x=y coordinate
        mvec = re.search(patterny, lines[i+1])
        new_y = 0.0
        if mvec:
          new_y = float(mvec.group(1))
        # append to list
        if len(polygons) > nid:
          node = polygons[nid]
          node[1] = (new_x, new_y)
          polygons[nid] = node
        else:
          polygons.insert(nid, [0,[new_x, new_y]] )

      if m2:
        # get index
        nid = int(m2.group(1)) - 1
        code = int(m2.group(2))
        if len(polygons) > nid:
          node = polygons[nid]
          node[0] = code
          polygons[nid] = node
        else:
          polygons.insert(nid, [code,[0, 0]] )

def parseLines():

  parsefile = folder_files +'/' + SAVE_DIRECTORY + '/' + DRAWING_OBJECT + '.VA'

  pattern_start = rf"Field: {LINES_VARNAME}\.NODEDATA\[(\d+)\]\.{LINE_START_SUFFIX} Access: RW: VECTOR =\s*(.*)"
  pattern_end = rf"Field: {LINES_VARNAME}\.NODEDATA\[(\d+)\]\.{LINE_END_SUFFIX} Access: RW: VECTOR =\s*(.*)"
  patternx = r"X:\s*(-?\d{0,3}\.\d{1,3})"
  patterny = r"Y:\s*(-?\d{0,3}\.\d{1,3})"

  with open(parsefile,'r') as f:

    lines = f.readlines()
    for i in range(len(lines)):

      m1 = re.search(pattern_start, lines[i])
      m2 = re.search(pattern_end, lines[i])
      
      if m1 or m2:
        # get index
        if m1:
          nid = int(m1.group(1)) - 1
        else:
          nid = int(m2.group(1)) - 1
        # get x coordinate
        mvec = re.search(patternx, lines[i+1])
        new_x = 0.0
        if mvec:
          new_x = float(mvec.group(1))
        # get x=y coordinate
        mvec = re.search(patterny, lines[i+1])
        new_y = 0.0
        if mvec:
          new_y = float(mvec.group(1))

      if m1:
        if len(raster_lines) > nid:
          node = lines[nid]
          node[0] = [new_x, new_y]
          raster_lines[nid] = node
        else:
          raster_lines.insert(nid, [[new_x, new_y],[0, 0]] )
      
      if m2:
        if len(raster_lines) > nid:
          node = raster_lines[nid]
          node[1] = [new_x, new_y]
          raster_lines[nid] = node
        else:
          raster_lines.insert(nid, [[0, 0],[new_x, new_y]] )

def print_list(list_obj):
  for i in range(len(list_obj)):
    print(str(list_obj[i]))

def plot():
  fig, ax = plt.subplots()

  #ploygons
  Path = mpath.Path
  codes, verts = zip(*polygons)
  start_idx = 0 ; end_idx = len(polygons)

  for i in range(len(polygons)):
    if codes[i] == Path.MOVETO:
      start_idx = i
    if (codes[i] == Path.CLOSEPOLY) or (codes[i] == Path.STOP):
      end_idx = i

      color = random_color_gen()
      face_color = list(map(lambda i: i*1.0/255, color))
      color2 = (color[0]*2%255, color[1]*2%255, color[2]*2%255)
      edge_color = list(map(lambda i: i*1.0/255, color2))

      path = mpath.Path(verts[start_idx:end_idx], codes[start_idx:end_idx])
      patch = mpatches.PathPatch(path, facecolor=face_color, edgecolor=edge_color, alpha=0.5)
      ax.add_patch(patch)

  #lines
  for line in raster_lines:
    x, y = zip(*line)

    color = random_color_gen()
    color = list(map(lambda i: i*1.0/255, color))
    draw = plt.Line2D(x, y, color=color)
    ax.add_line(draw)

  ax.grid()
  ax.axis('equal')
  plt.show()



class RobotFTP(object):
    
  def __init__(self, filename, ip, port = 80, username = "", password = ""):

    if (ip == ""):
        input("Robot FTP IP not defined, edit the top of the script to fix")
        sys.exit()

    if (username == ""):
        username = "anonymous"

    print("Trying to connect to: " + ip)
    self.ftp = FTP(ip) #compose of FTP class
    self.ftp.login()
    print("Connected to robot")

    self.ip = ip
    self.port = port
    self.username = username

    #store full list of programs to be ran
    self.program = filename + '.VA'

    self.savefile()

  def savefile(self):
    filename = self.program.upper()
    try:
      save_dir = folder_files +'/' + SAVE_DIRECTORY
      if not os.path.exists(save_dir):
        os.makedirs(save_dir)
      
      with open(save_dir + '/'+ filename, 'wb+') as fp:
        self.ftp.cwd("md:")
        self.ftp.retrbinary('RETR ' + self.program, fp.write)
    except ftplib.all_errors as e:
      print('FTP error:', e)


if __name__ == "__main__":
  folder_files = os.path.dirname(os.path.realpath(__file__))
  folder_files = os.path.abspath(os.path.join(folder_files, os.pardir))
  print('parent fldr: ', folder_files)
  # start an ftp instance
  robot = RobotFTP(DRAWING_OBJECT, ROBOT_IP, ROBOT_PORT, username = USERNAME, password = PASSWORD)
  # get contours
  parseContour()
  parseLines()
  print('polygons')
  print_list(polygons)
  print('lines')
  print_list(raster_lines)
  plot()


