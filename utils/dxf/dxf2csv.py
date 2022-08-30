import os
import argparse
import csv

# dxf support
import ezdxf
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing import Frontend, RenderContext

# matlibplot support
import matplotlib.pyplot as plt
import matplotlib as mpl

# csv export
def savecsv(filename, polygons):
    fields = ['x', 'y', 'polygons']
    
    with open(filename, 'w', newline='') as f:
        # using csv.writer method from CSV package
        write = csv.writer(f)
        write.writerow(fields)
        write.writerows(polygons)

def main(args):
    # select the file to convert
    dxfdir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..')) + '\\test\\dxf_examples\\'
    csvdir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..')) + '\\test\\csv_examples\\'
    dxffile = dxfdir + args.dxf_file
    csvfile = csvdir + args.csv_file

    # load dxf file
    doc = ezdxf.readfile(dxffile)
    msp = doc.modelspace()
    auditor = doc.audit()

    if len(auditor.errors) == 0:
        count = 0
        polygons = []
        # loop over entities in dxf file
        for entity in msp:
            count = count  + 1
            # sampling primitive entities
            entity_primitive = ezdxf.disassemble.make_primitive(entity)           # not all enitties are supported, check the ezdxf lib docs
            vertices = list(ezdxf.disassemble.to_vertices([entity_primitive]))    
            for v in vertices:
                polygons.append(["%.2f" % v.x, "%.2f" % v.y, "%d" % count])
    
    # export to csv
    savecsv(csvfile, polygons)
    print('Conversion Done')


if __name__ == "__main__":
    description=("Convert DXF to CSV")

    parser = argparse.ArgumentParser(prog='dxf2csv', description=description,
                                    formatter_class=argparse.MetavarTypeHelpFormatter)

    parser.add_argument('dxf_file', type=str, nargs='?', metavar='DXF',
            help="dxf file")
    parser.add_argument('csv_file', type=str, nargs='?', metavar='CSV',
            help="csv file")

    args = parser.parse_args()

    main(args)
