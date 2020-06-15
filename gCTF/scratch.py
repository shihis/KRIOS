import subprocess
import matplotlib.pyplot as plt
import numpy
import mrcfile
from read_input import read_input
import glob
import sys
import os
import re

list_file = []
list_fokus1= []
list_fokus2 = []
list_angle = []
list_phase = []
list_ccc = []
list_B_fctor = []
list_res_lim = []

input_log ="/mnt/local-scratch/2020-06-10-test-gctf/run06/img_0000865_df_RAW4_gctf.log"
list_file.append(input_log)
if not os.path.isfile(input_log):
    print("File path {} does not exist. Exiting...".format(input_log))
    sys.exit()
with open(input_log) as log:
    for line in log:
        print(cnt)
        if "Final Values" in str(line.strip()):
            print("Line {}: {}".format(cnt,line.strip()))

            tmp = re.findall(r"[-+]?\d*\.\d+|\d+",line)
            list_fokus1.append(tmp[0])
            list_fokus2.append(tmp[1])
            list_angle.append(tmp[2])
            list_phase.append(tmp[3])
            list_ccc.append(tmp[4])
        elif "RES_LIMIT" in str(line.strip()):
            tmp = re.findall(r"[-+]?\d*\.\d+|\d+", line)
            list_res_lim.append(tmp[0])
        elif "B_FACTOR" in str(line.strip()):
            tmp = re.findall(r"[-+]?\d*\.\d+|\d+", line)
            list_B_fctor.append(tmp[0])




