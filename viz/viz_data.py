import os
import argparse
import csv
import ezdxf
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing import Frontend, RenderContext
import matplotlib.pyplot as plt
import matplotlib as mpl

def file_type(fname):
    name, ext = os.path.splitext(fname)
    return ext.lower()

def main(args):
    ftype = file_type(args.filename)

    # for dxf files
    if ftype == '.dxf':
        # assuming the dxf file is in the dxf_examples of the test folder
        dxfdir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..')) + '\\test\\dxf_examples\\'
        dxffile = dxfdir + args.filename
        print(dxffile)
        # load dxf file
        doc = ezdxf.readfile(dxffile)
        msp = doc.modelspace()
        auditor = doc.audit()

        # check no errors
        if len(auditor.errors) == 0:
            # plot dxf
            fig = plt.figure()
            ax = fig.add_axes([0, 0, 1, 1])
            ctx = RenderContext(doc)
            ctx.set_current_layout(msp)
            out = MatplotlibBackend(ax)
            Frontend(ctx, out).draw_layout(msp, finalize=True)
            plt.show()

    # for the csv files
    if ftype == '.csv':
        # assuming the dxf file is in the dxf_examples of the test folder
        csvdir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..')) + '\\test\\csv_examples\\'
        csvfile = csvdir + args.filename
        print(csvfile)
        with open(csvfile, 'r') as f:
            # using csv package
            csv_reader = csv.reader(f, delimiter=',', skipinitialspace = True)
            next(csv_reader, None) # skip header of the file
            x = [] ; y = []
            # read through the csv file
            for row in csv_reader:
                x.append(float(row[0]))
                y.append(float(row[1]))

            # plot shapes
            plt.scatter(x, y)
            plt.show()
    
    # for the svg files
    if ftype == '.svg':
        # plot here
        print('')


def valid_file(fname):
    name, ext = os.path.splitext(fname)
    if ext.lower() not in ('.dxf', '.csv', '.svg'):
        raise argparse.ArgumentTypeError('File type is not supported.')
    return fname

if __name__ == "__main__":
    description=("Visualization Tool for CSV, DXF, and SVG")

    parser = argparse.ArgumentParser(prog='viz_data', description=description, formatter_class=argparse.MetavarTypeHelpFormatter)
    parser.add_argument('filename', type = valid_file, nargs='?', help='The name of the file to be visualized. Supported files are DXF, CSV, and SVG')
    args = parser.parse_args()

    main(args)

