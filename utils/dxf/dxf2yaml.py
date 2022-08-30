import sys
import os
import argparse
import yaml

# dxf support
import ezdxf
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing import Frontend, RenderContext

# matlibplot support
import matplotlib.pyplot as plt
import matplotlib as mpl


def saveyaml(filename, new_layer_data, append_flag):
    
    # if need to append the layer to existing file
    if append_flag:
        # read from file
        with open(filename, 'r') as file:
            yamlfile = yaml.safe_load(file)
            yamlfile.update(new_layer_data)
        # write to file
        with open(filename, 'w') as file:
            yaml.safe_dump(yamlfile, file)
            print('YAML FILE UPDATED.')
    else:
        with open(filename, 'w') as file:
            yaml.safe_dump(new_layer_data, file)
            print('DATA EXPORTED TO YAML FILE.')


def main(args):
    # select the dxf file, now assuming it is in the test folder
    dxfdir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..')) + '\\test\\dxf_examples\\'
    yamldir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..')) + '\\test\\yaml_examples\\'
    dxffile = dxfdir + args.dxf_file
    yamlfile = yamldir + args.yaml_file

    # load dxf file
    doc = ezdxf.readfile(dxffile)
    msp = doc.modelspace()
    auditor = doc.audit()

    if len(auditor.errors) == 0:
        counter = 1
        polygon = []
        yaml_dict = {'layer_' + str(args.layer_number) : []}
        for entity in msp:
            # convert dxf entities to primitive shapes
            entity_primitive = ezdxf.disassemble.make_primitive(entity)
            vertices = list(ezdxf.disassemble.to_vertices([entity_primitive]))
            if len(vertices) > 1:    # if there is more than a point in entities, will exclude constractive points
                points = []
                for v in vertices:
                    points.append(str(v.xyz[0]) + ',' + str(v.xyz[1]) + ',' + str(v.xyz[2]) )
                poly_name = 'polygon'  # poly_name = 'polygon_' + str(counter)
                yaml_dict['layer_' + str(args.layer_number)].append({poly_name : points})
                counter +=1
        
        #print(yaml_dict)    # print yaml file
        # export data:
        saveyaml(yamlfile, yaml_dict, args.a)

        # for reading the data later, the points were stored in str format for better readablity, 
        # and need to be converted to float.
        #print([float(points[0].split(',')[0]), float(points[0].split(',')[1]), float(points[0].split(',')[2])])
    else:
        raise Exception('Error in reading DXF file.')


if __name__ == "__main__":
    description = (""""Convert DXF to YAML.

    Examples:  

    python dxf2yaml.py circle.DXF circle.yaml                # overwrite data
    python dxf2yaml.py circle.DXF circle.yaml -a -l 2        # append data with dict key called layer_2""")


    parser = argparse.ArgumentParser(prog='dxf2yaml', description=description,
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('dxf_file', type=str, nargs='?', metavar='DXF',
                        help="dxf file.")
    parser.add_argument('yaml_file', type=str, nargs='?', metavar='YAML',
                        help="yaml file.")
    parser.add_argument('-a', action='store_true',
                        help='append flag')
    parser.add_argument('-l', '--layer_number',  const=28, default=1, type=int,
                        help='layer number if data need to be apppend to the yaml file.', nargs='?')


    args = parser.parse_args()

    # check if layer number is provided
    if args.a:
        if args.layer_number == 1:
            raise Exception("Layer number should be provided")
    
    main(args)
