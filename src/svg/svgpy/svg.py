from math import sqrt, atan2
from xml.dom import minidom
from .path import Path
from .parser import parse_path
from collections import MutableSequence
import re

# This module helps to import an SVG file into the svg.path 1.1 package
# To do:
# -Move the paths separately along with each group "<g />" according to transform="translate(x,y) or "matrix(0.96,0,0,0.96,20.027955,16.249495)"
# -Support for svg features other than "path"
# -Improve tangent calculations by differentiating the Bézier curves


class Point(object):
    '''Creates a 2D point or vector with values x and y. Example: Point(10,-20)'''
    def __init__(self, x, y=0):
        '''Defines x and y variables'''
        if isinstance(x,complex):
            self.x = x.real
            self.y = x.imag
        else:
            self.x = x
            self.y = y

    def move(self, dx, dy):
        '''Translates the point'''
        self.x = self.x + dx
        self.y = self.y + dy

    def __str__(self):
        return "Point(%s,%s)"%(self.x, self.y)

    def __repr__(self):
        return self.__str__()

    def getX(self):
        '''Returns the X coordinate of the point'''
        return self.x

    def getY(self):
        '''Returns the Y coordinate of the point'''
        return self.y

    def distance(self, other):
        '''Calculates the distance between two points'''
        dx = self.x - other.y
        dy = self.x - other.y
        return math.sqrt(dx*dx + dy*dy)
    
    def switchXY(self):
        '''Switches the X coordinate for the Y coordinate. This is useful if we are switching from image coordinates (X points to the right, Y points down) to a different coordinate system (X points down, Y points to the right)'''
        newx = self.y
        self.y = self.x
        self.x = newx

    def angle(self):
        '''Returns the angle of a vector with respect to the X axis'''
        return atan2(self.y, self.x)

class Path_feature():
    '''Holds the svg information of a path feature. It also calculates the path polygons.'''
    def __init__(self, idname, path, color, width, fill):
        self.type = 'path'
        self.idname = idname
        self.path = path
        self.fill_color = fill
        self.line_color = color
        self.line_width = width
        self.poly_vertex = []
        self.poly_vector = []        
        self.poly_scale = -1
        
    def __getitem__(self, index):
        p_i = self.poly_vertex[index]
        v_i = self.poly_vector[index]
        return Point(p_i.real, p_i.imag), [v_i.real, v_i.imag]
        
    def nPoints(self):
        '''Returns the number of points in the path polygon'''
        return len(self.poly_vertex)

    def getPoint(self,i):
        '''Returns the number of points in the path polygon'''
        #return Point(self.poly_vertex[i].real, self.poly_vertex[i].imag).switchXY()
        return Point(self.poly_vertex[i].imag, self.poly_vertex[i].real)

    def getVector(self,i):
        '''Returns the number of points in the path polygon'''
        return Point(self.poly_vector[i].imag, self.poly_vector[i].real)    
    
    def calc_polygon(self, poly_div=100, scale=1):
        '''Calculates the polygon for the path with poly_div vertex and vector (path tangent)'''
        if len(self.poly_vertex) != poly_div or self.poly_scale != scale:
            self._calc_polygon(poly_div, scale)

    def _calc_polygon(self, poly_div=100, scale=1):
        '''Performs the polygon calculations (use calc_polygon instead)'''
        self.poly_vertex = []
        self.poly_vector = []        
        self.poly_scale = scale
        #print('calculating polygon')
        factor = 1/(poly_div-1)
        for i in range(poly_div):
            p_i = self.path.point(i*factor)*scale
            self.poly_vertex.append(p_i)
        for i in range(poly_div-1):
            vi = self.poly_vertex[i+1] - self.poly_vertex[i]
            normvi = sqrt(vi.real*vi.real + vi.imag*vi.imag)
            if normvi < 1e-6:
                vi = complex(1,0)
            else:
                vi = vi/normvi
            self.poly_vector.append(vi)            
        self.poly_vector.append(vi)
            
    def polygon_move(self, tx, ty):
        '''Translates the polygon by [tx,ty] coordinates'''
        poly_div = len(self.poly_vertex)
        for i in range(poly_div):
            p_i = self.poly_vertex[i]
            self.poly_vertex[i] = complex(p_i.real+tx, p_i.imag+ty)

    def calc_size_poly(self, poly_div=None):
        '''Calculates the size of the scaled polygon (returns minXY, maxXY)'''
        if poly_div is None: poly_div = len(self.poly_vector)
        if poly_div == 0: poly_div = 100
        if self.poly_scale <= 0: self.poly_scale = 1
        self.calc_polygon(poly_div, self.poly_scale)
        #path_size = complex(0,0) #0+0*1j also works
        min_x = 1e6
        min_y = 1e6   
        max_x = -1e6
        max_y = -1e6     
        for i in range(len(self.poly_vertex)):
            min_x = min(min_x, self.poly_vertex[i].real)
            min_y = min(min_y, self.poly_vertex[i].imag)
            max_x = max(max_x, self.poly_vertex[i].real)
            max_y = max(max_y, self.poly_vertex[i].imag)
            
        return complex(min_x, min_y), complex(max_x, max_y)

    def calc_size_path(self, poly_div=None):
        '''Calculates the size of the path in original coordinates (same coordinates as if we used Inkscape for example)'''
        pmin, pmax = self.calc_size_poly(poly_div)
        return pmin/self.poly_scale, pmax/self.poly_scale

    def __repr__(self):
        string = self.type + ': ' + self.idname + '\n'
        string = string + 'line color: ' + self.line_color.__repr__() + '\n'
        string = string + 'line width: ' + str(self.line_width) + '\n'
        if len(self.poly_vertex) > 0:
            string = string + 'polygon vertex size: ' + str(len(self.poly_vertex)) + '\n'
            string = string + 'polygon scale: ' + str(self.poly_scale) + '\n'
            poly_sz = self.calc_size_poly()
            string = string + 'polygon scaled size: ' + str(poly_sz)
        else:
            string = string + 'polygons not calculated, run calc_polygon_fit()' + '\n'
        string = string + '\n'
        return string
        
class Svg(MutableSequence):
    '''Holds the data of an SVG image'''
    def __init__(self):
        self._features = []
        
    def __getitem__(self, index):
        return self._features[index]

    def __setitem__(self, index, value):
        self._features[index] = value

    def __delitem__(self, index):
        del self._features[index]
        
    def insert(self, index, value):
        self._features.insert(index, value)
        
    def __len__(self):
        return len(self._features)

    def __repr__(self):
        string = ''
        count = 0
        for x in self._features:
            count = count + 1
            string = string + '<feature %i>\n' % count
            string = string + '<width %f ; color %f, %f, %f>\n' % (x.line_width, x.line_color[0], x.line_color[1], x.line_color[2])
            string = string + repr(x.path)
            string = string + '\n'
        return string

    def calc_size_path(self):
        '''Calculates the size of the path (minimum & maximum corner)'''
        img_minX = 1e6
        img_minY = 1e6  
        img_maxX = -1e6
        img_maxY = -1e6      
        for feat in self._features:
            pathmin, pathmax = feat.calc_size_path()
            img_minX = min(img_minX, pathmin.real)
            img_minY = min(img_minY, pathmin.imag)
            img_maxX = max(img_maxX, pathmax.real)
            img_maxY = max(img_maxY, pathmax.imag)
        return complex(img_minX,img_minY), complex(img_maxX, img_maxY)

    def calc_size_poly(self):
        '''Calculates the size of the polygon, which can be scaled/replaced with respect to the path (minimum & maximum corner)'''
        img_minX = 1e6
        img_minY = 1e6  
        img_maxX = -1e6
        img_maxY = -1e6      
        for feat in self._features:
            pathmin, pathmax = feat.calc_size_poly()
            img_minX = min(img_minX, pathmin.real)
            img_minY = min(img_minY, pathmin.imag)
            img_maxX = max(img_maxX, pathmax.real)
            img_maxY = max(img_maxY, pathmax.imag)
        return complex(img_minX,img_minY), complex(img_maxX, img_maxY)

    def size_poly(self):
        '''Calculates the size of the polygon.'''
        [corner_min, corner_max] = self.calc_size_poly()
        return Point(corner_max.imag, corner_max.real)

    def calc_polygon_fit(self, fit_size=Point(500,500), arc_size=5):
        '''Calculates the path polygons and fits the svg image in the desired coordinates size'''
        img_min, img_max = self.calc_size_path()
        img_sz_x = img_max.real - img_min.real
        img_sz_y = img_max.imag - img_min.imag            
        scale_x = fit_size.y / img_sz_x
        scale_y = fit_size.x / img_sz_y
        scale = min(scale_x, scale_y)
        #print(scale)

        for feat in self._features:
            poly_len_scaled = feat.path.length()*scale
            poly_div = round(poly_len_scaled / arc_size)
            poly_div = max(poly_div,2) # make sure we have at least 2 vertex in the polygon
            MAX_POLY_SIZE = 2000
            if poly_div > MAX_POLY_SIZE:
                print('warning, polygon too large, max points set to = ' + str(MAX_POLY_SIZE))
                poly_div = MAX_POLY_SIZE
                
            feat.calc_polygon(poly_div, scale)
            #feat.polygon_move(-img_min.real*scale, -img_min.imag*scale) #this is faster but less accurate
            
        polymin, polymax = self.calc_size_poly()
        for feat in self._features:
            feat.polygon_move(-polymin.real, -polymin.imag)
            
        return complex(img_sz_x, img_sz_y)*scale
    

def hex_2_rgb(colorstring):
    """ convert #RRGGBB to an (R, G, B) tuple """
    r, g, b = colorstring[:2], colorstring[2:4], colorstring[4:]
    r, g, b = [int(n, 16)/255 for n in (r, g, b)]
    return [r, g, b]



def svg_load(svgfile):
    '''Loads an SVG file into a Svg() class'''
    svg = Svg()
    xmldoc = minidom.parse(svgfile)
    itemlist = xmldoc.getElementsByTagName('path') 
    #print(len(itemlist))
    #print(itemlist[0].attributes['d'].value)
    i=0
    path_data = []
    for s in itemlist:
        if s.parentNode.tagName != 'marker':
            i = i + 1        
            data = s.attributes['d'].value
            path = parse_path(data)            
            #print('Path: ',i)
            try:
                idname = s.attributes['id'].value
            except:
                idname = 'noname'
                
            haslinecolor = False
            try:
                style = s.attributes['style'].value + ';'
                lcolor = hex_2_rgb(re.search('stroke:#(.*?);', style).group(1))
                haslinecolor = True
                strwidth = re.search('stroke-width:(.*?);', style).group(1)
                if strwidth[-2:] == 'px': strwidth = strwidth[:-2]
                lwidth = float(strwidth)
            except:
                #print('no stroke data for path: '+idname)
                lcolor = [0,0,0] # black as default color
                lwidth = 1 # 1 pixel width as default color
   
            try:
                fill = hex_2_rgb(re.search('fill:#(.*?);', style).group(1))
                if not haslinecolor:
                    lcolor = fill
            except:
                fill = lcolor
                
            svg.append(Path_feature(idname, path, lcolor, lwidth, fill))
    return svg
