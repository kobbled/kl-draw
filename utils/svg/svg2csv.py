import sys 
import os
import csv
from svgpy.svg import *
import argparse


SIZE_BOARD = (80, 80)     # Size of the image. The image will be scaled keeping its aspect ratio
MM_X_PIXEL = 6           # in mm. The path will be cut depending on the pixel size. If this value is changed it is recommended to scale the pixel object

def draw(svg_img):
  polygon = []

  count = 0
  for path in svg_img:
    count = count + 1
    print('polygon: {}'.format(count))
    np = path.nPoints()
    print('number of points: {}'.format(np))

    for i in range(np):
      p_i = path.getPoint(i)
      v_i = path.getVector(i)

      polygon.append(["%.2f" % p_i.x, "%.2f" % p_i.y, "%d" % count])
  
  return polygon

def savecsv(filename, polygon):
  fields = ['x', 'y', 'polygon']

  with open(filename, 'w', newline='') as f:
    # using csv.writer method from CSV package
    write = csv.writer(f)

    write.writerow(fields)
    write.writerows(polygon)

def main(args):
  # select the file to draw
  svgfile = os.path.dirname(os.path.abspath(__file__)) + '\\' + args.image_file
  csvfile = os.path.dirname(os.path.abspath(__file__)) + '\\' + args.csv_file

  # import the SVG file
  svgdata = svg_load(svgfile)
  size = tuple(args.scale)
  image_size = Point(size[0],size[1])   # size of the image in MM
  svgdata.calc_polygon_fit(image_size, args.pixel_dist)

  poly = draw(svgdata)
  savecsv(csvfile, poly)



if __name__ == "__main__":
  description=("Convert SVG to CSV")

  parser = argparse.ArgumentParser(prog='svg2csv', description=description,
                                  formatter_class=argparse.MetavarTypeHelpFormatter)

  parser.add_argument('-s', '--scale', nargs="+", type=float, dest='scale',
        default=SIZE_BOARD,
        help="rescale the svg image")
  parser.add_argument('-i', '--increment_dist', type=int, dest='pixel_dist',
        default=MM_X_PIXEL,
        help="distance between line increments")
  parser.add_argument('image_file', type=str, nargs='?', metavar='SVG',
        help="svg file")
  parser.add_argument('csv_file', type=str, nargs='?', metavar='CSV',
        help="csv file")

  args = parser.parse_args()

  main(args)

