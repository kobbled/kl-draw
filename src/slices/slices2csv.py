import os
import argparse
from queue import Empty
import cv2
import csv
import numpy as np
import re
from zipfile import ZipFile
import matplotlib.pyplot as plt
import shutil
import open3d as o3d
from tqdm import tqdm


def savecsv(filename, polygons):
    fields = ['x', 'y', 'z', 'layer', 'Ploygon', 'Level']
    
    with open(filename, 'w', newline='') as f:
        # using csv.writer method from CSV package
        write = csv.writer(f)
        write.writerow(fields)
        write.writerows(polygons)
    print('CSV File Exported.')


def gcode_get_params(filename):
    with open(filename, 'r') as gFile:
        gcode = gFile.read()

        # search for image resolutions, table dimension, and layer heights:
        Xresolution = int(re.search(';resolutionX:([0-9.]+)', gcode).group(1))
        Yresolution = int(re.search(';resolutionY:([0-9.]+)', gcode).group(1))
        Xdimension = float(re.search(';machineX:([0-9.]+)', gcode).group(1))
        Ydimension = float(re.search(';machineY:([0-9.]+)', gcode).group(1))
        totalLayers = int(re.search(';totalLayer:([0-9.]+)', gcode).group(1))
        zlayers = re.findall(';currPos:([0-9.]+)', gcode, re.MULTILINE)

        # layers heights
        for layer in range(totalLayers):
            zlayers[layer] = (float(zlayers[layer]))

    return Xresolution, Yresolution, Xdimension, Ydimension, totalLayers, zlayers

# convert slices (binary images) to 2D contours
def img2contour(Xresolution, Yresolution, Xdimension, Ydimension, totalLayers, zlayers, foldername):
    model_points = []
    polygons = []
    for layer in tqdm(range(1,totalLayers+1)):
        # reading layer image
        img = cv2.imread(foldername + '\\' + str(layer) + '.png', cv2.IMREAD_GRAYSCALE)
        ret, binaryImg = cv2.threshold(img, 100, 255, cv2.THRESH_OTSU)
        contours, hierarchy = cv2.findContours(binaryImg, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        """"
        # To show contours
        if layer == args.show_layer:
            # convert to rgb for drawing contours later
            rgbImg = cv2.cvtColor(img,cv2.COLOR_GRAY2RGB)    
            with_contours = cv2.drawContours(rgbImg, contours, -1, (255,0,0),3)
            cv2.imshow('Detected contours', with_contours)
            cv2.waitKey(0)
        """
        count_polygons = 1
        # interpret contours in layer
        for contour, level in zip(contours,hierarchy[0]):
            points = []
            for p in contour:
                # converting from pixels to mm (mm/pxl)
                mapped_point = [p[0][0] * (Xdimension / Xresolution), p[0][1] * (Ydimension / Yresolution), zlayers[layer-1]]  
                points.append(mapped_point)
            
            # voxel downsampling using open3d
            if args.sampling_magnitude != 0:
                points_obj = (o3d.geometry.PointCloud(o3d.utility.Vector3dVector(np.array(points))))       # convert to open3d format
                sampled_points = np.asarray(points_obj.voxel_down_sample(voxel_size= args.sampling_magnitude).points) # sampled points array
            else:
                sampled_points = points
            
            # store points in polygon to export them in csv
            for sp in sampled_points:
                polygons.append(["%.2f" % sp[0], "%.2f" % sp[1], "%.2f" % sp[2], "%d" % layer, "%d" % count_polygons, "%d" % (level[3]+2) ])
            
            # store all points for
            model_points.extend(sampled_points)

            # next contour
            count_polygons = count_polygons + 1
    
    if args.vis:
        # visualize contours using Open3D
        o3d.visualization.draw_geometries([o3d.geometry.PointCloud(o3d.utility.Vector3dVector(np.array(model_points)))])
    
    return polygons

def main(args):
    # model slices file
    zipdir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..')) + '\\test\\stl_examples\\'
    csvdir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..')) + '\\test\\csv_examples\\'
    zipfile = zipdir + args.zip_file 
    csvfile = csvdir + args.csv_file
    
    # extract file in zip file 
    with ZipFile(zipfile) as myzip:
        myzip.extractall(zipdir + '\\temp')

    # read parameters in gcode file
    Xresolution, Yresolution, Xdimension, Ydimension, totalLayers, zlayers = gcode_get_params(zipdir + '\\temp' + '\\run.gcode')

    # convert png images to contours
    polygons = img2contour(Xresolution, Yresolution, Xdimension, Ydimension, totalLayers, zlayers, zipdir + '\\temp')

    # export it as csv
    savecsv(csvfile, polygons)

    # remove the temp folder after finish
    shutil.rmtree(zipdir + '\\temp', ignore_errors=False, onerror=None)



if __name__ == "__main__":
    description=("""Converts Images slices of a model to contours (CSV), assumming zip file in stl_examples, and saving csv file to csv_examples.)
    
    Examples:  

    python slices2csv.py _rocket_nozzle.zip _rocket_nozzle.csv -sm 5 -vis                 # sampling size is 5 
     python slices2csv.py _rocket_nozzle.zip _rocket_nozzle.csv -vis          # don't sample points, but show contours""")

    parser = argparse.ArgumentParser(prog='slices2csv', description=description, formatter_class=argparse.MetavarTypeHelpFormatter)
    parser.add_argument('zip_file', type=str, nargs='?', metavar='ZIP', help="zip file")
    parser.add_argument('csv_file', type=str, nargs='?', metavar='CSV', help="csv file")
    parser.add_argument('-sm', '--sampling_magnitude', default=0, type=int, help='contour sampling magnitude.', nargs='?')
    parser.add_argument('-vis', action='store_true', help='visualization contours flag')
    args = parser.parse_args()

    main(args)
