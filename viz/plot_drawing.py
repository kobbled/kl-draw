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
import argparse
import numpy as np
import collections

import matplotlib.path as mpath
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

#ftp parameters
ROBOT_IP = '127.0.0.1'
ROBOT_PORT = 80
USERNAME = ""
PASSWORD = ""

SAVE_DIRECTORY = 'plots'

CONTOUR_VARNAME = 'CONTOURS'
CONTOUR_VEC_SUFFIX = 'V'
CONTOUR_VEC_TYPE = 'VECTOR'
CONTOUR_CODE_SUFFIX = 'CODE'
CONTOUR_CODE_TYPE = 'SHORT'

LINES_VARNAME = 'LINES'
LINE_START_SUFFIX = 'R0'
LINE_END_SUFFIX = 'R1'
LINE_TYPE = 'VECTOR'
LINES_TYPENAME = 'T_SEG2D_POLY'
LINES_TYPENAME2 = 'T_VEC_PATH'

PATH_MAP = 'PATH_PLAN'
PATH_MAP_SUFFIX = 'V'
PATH_MAP_TYPE = 'INTEGER'
PATH_DATA = 'LINES'
PATH_DATA_SUFFIX = 'V'
MOTION_DATA_TYPE = 'VECTOR'

#pattern1 = r"Field: {LINES_VARNAME}\.NODEDATA\[(\d{1,5})\]\.{LINE_START_SUFFIX} Access: RW: VECTOR =\s*(.*)"
#pattern2 = r"Field: {LINES_VARNAME}\.NODEDATA\[(\d{1,5})\]\.{LINE_END_SUFFIX} Access: RW: VECTOR =\s*(.*)"

folder_files = ''

raster_lines = []
t_line = collections.namedtuple('t_line',
  'r0 '
  'r1 '
  'polygon '
  'tangent'
)
polygons = []
t_polygon = collections.namedtuple('t_polygon',
  'coords '
  'code '
  'polygon '
  'tangent'
)

def random_color_gen():
  """Generates a random RGB color
  
  :return: 3 elements in the form [R, G, B]
  :rtype: list
  """
  r = randint(0, 255)
  g = randint(0, 255)
  b = randint(0, 255)
  return (r, g, b)

def parseContour(args):

  parsefile = folder_files +'/' + SAVE_DIRECTORY + '/' + args.rbt_fl + '.VA'

  pattern_code = rf"Field: {CONTOUR_VARNAME}\.NODEDATA\[(\d+)\]\.{CONTOUR_CODE_SUFFIX} Access: RW: {CONTOUR_CODE_TYPE} =\s*(.*)"
  pattern_vector = rf"Field: {CONTOUR_VARNAME}\.NODEDATA\[(\d+)\]\.{CONTOUR_VEC_SUFFIX} Access: RW: {CONTOUR_VEC_TYPE} =\s"
  pattern_polygon = rf"Field: {CONTOUR_VARNAME}\.NODEDATA\[(\d+)\]\.POLYGON Access: RW: {CONTOUR_CODE_TYPE} =\s*(.*)"
  pattern_tangent = rf"Field: {CONTOUR_VARNAME}\.NODEDATA\[(\d+)\]\.TANGENT Access: RW: VECTOR =\s"
  patternx = r"X:\s*(-?\d{0,3}\.\d{1,3})"
  patterny = r"Y:\s*(-?\d{0,3}\.\d{1,3})"

  coords = ('', '')
  code = ''
  polygon = ''
  tangent = ('', '')

  with open(parsefile,'r') as f:

    lines = f.readlines()
    for i in range(len(lines)):

      m2 = re.search(pattern_code, lines[i])
      m1 = re.search(pattern_vector, lines[i])
      m3 = re.search(pattern_tangent, lines[i])
      m4 = re.search(pattern_polygon, lines[i])
      
      nid = None
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
        coords = (new_x, new_y)
      
      if m2:
        # get index
        nid = int(m2.group(1)) - 1
        code = int(m2.group(2))
      
      if m3:
        # get index
        nid = int(m3.group(1)) - 1
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
        tangent = (new_x, new_y)
      
      if m4:
        # get index
        nid = int(m4.group(1)) - 1
        polygon = int(m4.group(2))

      poly = t_polygon(
          coords = coords,
          code = code,
          polygon = polygon,
          tangent = tangent
        )
      if nid is not None:
        if len(polygons) > nid:
          polygons[nid] = poly
        else:
          polygons.insert(nid, poly )
        
        nid = None

def parseLines(args):

  parsefile = folder_files +'/' + SAVE_DIRECTORY + '/' + args.rbt_fl + '.VA'

  pattern_start = rf"Field: {LINES_VARNAME}\.NODEDATA\[(\d+)\]\.{LINE_START_SUFFIX} Access: RW: {LINE_TYPE} =\s*(.*)"
  pattern_end = rf"Field: {LINES_VARNAME}\.NODEDATA\[(\d+)\]\.{LINE_END_SUFFIX} Access: RW: {LINE_TYPE} =\s*(.*)"
  pattern_poly = rf"Field: {LINES_VARNAME}\.NODEDATA\[(\d+)\]\.POLYGON Access: RW: SHORT =\s*(.*)"
  pattern_tangent = rf"Field: {LINES_VARNAME}\.NODEDATA\[(\d+)\]\.TANGENT Access: RW: VECTOR =\s"

  patternx = r"X:\s*(-?\d{0,3}\.\d{1,3})"
  patterny = r"Y:\s*(-?\d{0,3}\.\d{1,3})"

  r0 = ('', '')
  r1 = ('', '')
  poly = ''
  tangent = ('', '')

  with open(parsefile,'r') as f:

    lines = f.readlines()
    for i in range(len(lines)):

      m1 = re.search(pattern_start, lines[i])
      m2 = re.search(pattern_end, lines[i])
      m3 = re.search(pattern_poly, lines[i])
      m4 = re.search(pattern_tangent, lines[i])

      nid = None
      
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
        
        r0 = (new_x, new_y)
      
      if m2:
        # get index
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

        r1 = (new_x, new_y)
      
      if m3:
        # get index
        nid = int(m3.group(1)) - 1
        poly = int(m3.group(2))

      if m4:
        # get index
        nid = int(m4.group(1)) - 1
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
        
        tangent = (new_x, new_y)

      line = t_line(
          r0 = r0,
          r1 = r1,
          polygon = poly,
          tangent = tangent
        )

      if nid is not None:
        if len(raster_lines) > nid:
          raster_lines[nid] = line
        else:
          raster_lines.insert(nid, line)
        
        nid = None

def print_cont(list_obj):
  for i in range(len(list_obj)):
    print("{}: {:.3f}, {:.3f} : {:.3f}, {:.3f}".format(list_obj[i].code, list_obj[i].coords[0], list_obj[i].coords[1], list_obj[i].tangent[0], list_obj[i].tangent[1]))

def print_line(list_obj):
  for i in range(len(list_obj)):
    print("{}: {:.3f}, {:.3f} : {:.3f}, {:.3f} : {:.3f}, {:.3f}".format(list_obj[i].polygon, list_obj[i].r0[0], list_obj[i].r0[1], list_obj[i].r1[0], list_obj[i].r1[1], list_obj[i].tangent[0], list_obj[i].tangent[1]))

def slice(obj, name):
  list = []
  for o in obj:
    list.append(getattr(o, name))
  
  return list

def plot(args):
  fig, ax = plt.subplots()

  #ploygons
  Path = mpath.Path
  if len(polygons) > 0:
    codes = slice(polygons, 'code')
    verts = slice(polygons, 'coords')
    tang = slice(polygons, 'tangent')
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

    if args.showtangents:
      # add tangent vectors
      ax.arrow(verts[i][0], verts[i][1], tang[i][0]*10, tang[i][1]*10, head_width=5, head_length=10, fc='r', ec='r')

  #lines
  if len(raster_lines) > 0:
    r0 = np.array(slice(raster_lines, 'r0'))
    r1 = np.array(slice(raster_lines, 'r1'))
    poly = slice(raster_lines, 'polygon')
    tang = slice(raster_lines, 'tangent')
  
    x = list(zip(r0[:,0], r1[:,0]))
    y = list(zip(r0[:,1], r1[:,1]))

  for i in range(len(raster_lines)):
    color = random_color_gen()
    color = list(map(lambda x: x*1.0/255, color))
    #color = 'yellow'
    draw = plt.Line2D(x[i], y[i], color=color)
    ax.add_line(draw)

    if args.showtangents:
      # add tangent vectors
      ax.arrow((r0[i][0]+r1[i][0])/2, (r0[i][1]+r1[i][1])/2, tang[i][0]*10, tang[i][1]*10, head_width=5, head_length=10, fc='g', ec='g')

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

def main():
  description=("Visualization tool for interpretting paths on the"
               "FANUC controller")

  parser = argparse.ArgumentParser(prog='plot_drawing', description=description,
                                  formatter_class=argparse.MetavarTypeHelpFormatter)

  parser.add_argument('rbt_fl', type=str, nargs='?',
        help="Name of karel file")
  parser.add_argument('-t', '--showtangents', action='store_true', dest='showtangents',
        help='visualize tangent vectors')

  args = parser.parse_args()

  folder_files = os.path.dirname(os.path.realpath(__file__))
  folder_files = os.path.abspath(os.path.join(folder_files, os.pardir))
  print('parent fldr: ', folder_files)
  # start an ftp instance
  robot = RobotFTP(args.rbt_fl, ROBOT_IP, ROBOT_PORT, username = USERNAME, password = PASSWORD)
  
  # get contours
  parseContour(args)

  parseLines(args)

  print('polygons')
  print_cont(polygons)
  print('lines')
  print_line(raster_lines)
  
  plot(args)



if __name__ == "__main__":
  main()
