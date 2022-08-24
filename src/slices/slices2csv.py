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
    fig = plt.figure()
    ax = plt.axes(projection='3d')
    xdata = []; ydata = []; zdata = []
    points =[]
    polygons = []
    for layer in tqdm(range(1,totalLayers+1)):
        # reading layer image
        img = cv2.imread(foldername + '\\' + str(layer) + '.png', cv2.IMREAD_GRAYSCALE)
        ret, binaryImg = cv2.threshold(img, 100, 255, cv2.THRESH_OTSU)
        contours, hierarchy = cv2.findContours(binaryImg, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        """
        # To show contours      -----------------------
        # convert to rgb for drawing contours later
        rgbImg = cv2.cvtColor(img,cv2.COLOR_GRAY2RGB)
        cv2.imshow('Binary image', binaryImg)
        cv2.waitKey(0) # Wait for keypress to continue        
        with_contours = cv2.drawContours(rgbImg, contours, -1, (255,0,0),3)
        cv2.imshow('Detected contours', with_contours)
        cv2.waitKey(0)
        """

        """        
        # contour leveling   hierarchy [Next, Previous, Child, Parent]
        # find the most external contour, which is the starting contour going inside
        outerContoursIndex = []
        for h in hierarchy:
            if h[2] < 0:   # does not have parent
                outerContoursIndex.append(hierarchy.index(h))

        levels = np.array(len(hierarchy))
        contourIndex = outerContoursIndex   # starting from the outer contour
        for i in len(hierarchy):
            levels[contourIndex] = i
            contourIndex = hierarchy.indx(hierarchy[contourIndex][2])  # searching for the index of the child
        print(levels)
        """
        count_polygons = 1
        # interpret contours in layer
        for contour, level in zip(contours,hierarchy[0]) :
            for p in contour:
                # converting from pixcels to mm (mm/pxl)
                mapped_point = [p[0][0] * (Xdimension / Xresolution), p[0][1] * (Ydimension / Yresolution), zlayers[layer-1]]  
                points.append(mapped_point)
                polygons.append(["%.2f" % mapped_point[0], "%.2f" % mapped_point[1], "%.2f" % mapped_point[2], "%d" % layer, "%d" % count_polygons, "%d" % (level[3]+2) ])
                xdata.append(mapped_point[0]); ydata.append(mapped_point[1]); zdata.append(mapped_point[2])
            count_polygons = count_polygons + 1
    pcd = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(np.array(points)))
    downsampled = pcd.voxel_down_sample(voxel_size=0.0001)
    # visualize contours
    o3d.visualization.draw_geometries([downsampled])
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
    description=("Converts Images slices of a model to contours (CSV), assumming zip file in stl_examples, and saving csv file to csv_examples.")

    parser = argparse.ArgumentParser(prog='slices2csv', description=description, formatter_class=argparse.MetavarTypeHelpFormatter)
    parser.add_argument('zip_file', type=str, nargs='?', metavar='ZIP', help="zip file")
    parser.add_argument('csv_file', type=str, nargs='?', metavar='CSV', help="csv file")
    args = parser.parse_args()

    main(args)
