#


import os
import subprocess
import numpy as np
import mrcfile
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import cv2
import glob
import datetime
import re
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages


list_x = []
list_file = []
list_fokus= []
list_astig = []
list_angle = []
list_phase = []
list_ccc = []
list_B_fctor = []
list_res_lim = []


def read_input(inputFile):
    print("Reading parameter file....:",inputFile)
    if not inputFile:
        print("read input funktion needs the in put file as parameter"
              "please specify an input file"
              "USAGE: read_input(inputfile) parses the in putfile and loads parameters in a dictionary")
        exit()
    #inputFile = "input.cfg"
    fileObj = open(inputFile)
    params = {}
    for line in fileObj:
        line = line.strip()
        if not line.startswith("#"):
            line = line.split("#",1)[0]
            line = line.rstrip()
            #print (line)
            key_value = line.split("=")
            if len(key_value) == 2:
                params[key_value[0].strip()] = key_value[1].strip()
    fileObj.close()
    return params

def show_images(images, cols=1, titles=None,outfile = "output.pdf"):
    print("Generating image gallery....")
    """Display a list of images in a single figure with matplotlib.

    Parameters
    ---------
    images: List of np.arrays compatible with plt.imshow.

    cols (Default = 1): Number of columns in figure (number of rows is
                        set to np.ceil(n_images/float(cols))).

    titles: List of titles corresponding to each image. Must have
            the same length as titles.
    """
    fontsize = int(120/cols)
    if fontsize > 20: fontsize = 20

    assert ((titles is None) or (len(images) == len(titles)))
    n_images = len(images)
    print("number of image: ",n_images)
    if titles is None: titles = ['Image (%d)' % i for i in range(1, n_images + 1)]
    fig = plt.figure()
    for n, (image, title) in enumerate(zip(images, titles)):
        #a = fig.add_subplot(cols, np.ceil(n_images / float(cols)), n + 1)
        a = fig.add_subplot(np.ceil(n_images / float(cols)),cols, n + 1,)
        plt.axis("off")
#        fig.set_size_inches(512/92,512/96)
        #print("image dimensions = ",int(image.ndim))
        if image.ndim == 2:
            plt.gray()
        plt.imshow(image)
        a.set_title(title,fontsize= fontsize)
    fig.set_size_inches(cols*512/96,int((n_images/cols)*512/96))
    #fig.set_size_inches(np.array(fig.get_size_inches()) * n_images)
    plt.axis("off")
    #plt.tight_layout()
    #plt.show()
    plt.savefig(outfile,dpi = 72)
    plt.close()

def gCTF(infile):
    print("Running Gctf...")
    if extension == "mrc":
        binary = str(parameters["binary"])
        apix = " --apix "+str(parameters["--apix"])
        cs = " --cs "+str(parameters["--cs"])

        command = binary + apix + cs + " --ac " + str(parameters["--ac"])+ " --resL "+str(parameters["--resL"])
        command = command + " --resH "+str(parameters["--resH"])+" --boxsize "+str(parameters["--boxsize"])
        print(binary)
        if int(parameters["--search_phase_shift"]) == 1:

            command = command + " --phase_shift_L "+str(parameters["--phase_shift_L"]) + " --phase_shift_H "+str(parameters["--phase_shift_H"])
            command = command + " --phase_shift_T "+str(parameters["--phase_shift_T"]) + " --refine_2d_T "+str(parameters["--refine_2d_T"])
            command = command + " --cosearch_refine_ps "+str(parameters["--cosearch_refine_ps"])
            #print(binary, apix, cs, phase_shift_L, phase_shift_H, phase_shift_T, refine_2d_T, cosearch_refine_ps, infile)
            #process = subprocess.Popen([binary, apix, cs, phase_shift_L, phase_shift_H, phase_shift_T, refine_2d_T, cosearch_refine_ps, infile], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            #stdout, stderr = process.communicate()
            #print(stdout.decode("utf-8"))
        if int(parameters["--do_EPA"]) == 1:
            command = command + " --do_EPA " + str(parameters["--do_EPA"])
            command = command + " --EPA_oversmp " + str(parameters["--EPA_oversmp"])

        command = command + " " +infile
        process = subprocess.Popen([command],shell=True)
        stdout, stderr = process.communicate()


        return command

def open_mrc(file,size=512):
    print ("Opening mrc files...")

    with mrcfile.open(file) as mrc:
        #mrc.print_header()
        img = mrc.data
        new_size = max(np.shape(img))
        if len(np.shape(img)) == 3:
            img = np.reshape(img, (new_size, new_size))
        img = cv2.normalize(img, dst=None, alpha=0,beta=255, norm_type=cv2.NORM_MINMAX,dtype=cv2.CV_8U)
        img = cv2.equalizeHist(img)
        img = cv2.resize(img,(size,size),interpolation=cv2.INTER_CUBIC)
        img = cv2.GaussianBlur(img,(3,3),0)
        return img


def parse_logfile(input_log,x):
    print("parsing gctf_log...")
    list_file.append(input_log)
    list_x.append(x)
    if not os.path.isfile(input_log):
        print("File path {} does not exist. Exiting...".format(input_log))
        exit()
    with open(input_log) as log:
        for line in log:
            if "Final Values" in str(line.strip()):

                tmp = re.findall(r"[-+]?\d*\.\d+|\d+", line)
                fokus = (float(tmp[0]) + float(tmp[1]))/20
                astig = abs(float(tmp[1])-float(tmp[0]))/10
                list_fokus.append(fokus)
                list_astig.append(astig)
                list_angle.append(float(tmp[2]))
                if int(parameters["--search_phase_shift"]) == 1:
                    list_phase.append(float(tmp[3]))
                    list_ccc.append(float(tmp[4]))
                else: list_ccc.append(float(tmp[3]))
            elif "RES_LIMIT" in str(line.strip()):
                tmp = re.findall(r"[-+]?\d*\.\d+|\d+", line)
                list_res_lim.append(float(tmp[0]))
            elif "B_FACTOR" in str(line.strip()):
                tmp = re.findall(r"[-+]?\d*\.\d+|\d+", line)
                list_B_fctor.append(float(tmp[0]))
def create_pdf_page(x_values,y_values,x_label,y_label,title,bins = 10):
    fig=plt.figure()
    gridspec.GridSpec(3,12)
    plt.subplot2grid((3, 12), (0, 0), colspan=8, rowspan=3)
    plt.plot(x_values, y_values, "+")
    plt.title(title)
    plt.ylabel(y_label)
    plt.xlabel(x_label)
    plt.subplot2grid((3,12),(0,9),colspan=3,rowspan=3)
    plt.hist(y_values,bins = bins)
    plt.xlabel(y_label)
    plt.ylabel("cts")
    fig.set_size_inches(w=11,h=5)


def plot_grapphs(outfile = "graphs.pdf",pdfs = 1,plots = 1):
    print("Generating graph output...")
    print("graphs are saved to: ",outfile)
    with PdfPages(outfile) as pdf:
        fig = plt.figure()
        plt.axis([0, 10, 0, 10])
        t = "Experiment from "+ str(timestamp)
        plt.text(-1,10,t, ha="left", wrap=True)
        plt.text(-1, 8, inputfolder, ha='left', wrap=True)
        #if not "command" in locals(): command = "gCTF command not defined"
        #plt.text(-1, 7, command, ha='left', wrap=True)
        plt.text(-1,7,meta,ha="left",va="top",wrap = True)
        plt.axis("off")
        fig.set_size_inches(w=11, h=5)
        pdf.savefig()

        create_pdf_page(list_x,list_fokus,"Image Number","Defocus / nm","Defocus (positive value = underfocus)")
        pdf.savefig()
        create_pdf_page(list_x,list_astig,"Image Number","Astigmatism / nm","Astigmatism" )
        pdf.savefig()
        if len(list_phase)>0:
            create_pdf_page(list_x,list_phase,"Image Number","Phase Shift / °","Phase Shift" )
            pdf.savefig()
        create_pdf_page(list_x,list_res_lim,"Image Number","Resolution limit / A","Resolution limit" )
        pdf.savefig()
        create_pdf_page(list_x,list_ccc,"Image Number","CCC","Cross corelation coefficient",bins=15 )
        pdf.savefig()
        create_pdf_page(list_x,list_B_fctor,"Image Number","B-factor","B-factor",bins=15 )
        pdf.savefig()

    if plots == 1:
        plt.show()

def check_mrc(inputfile,outmode=1):
    a = mrcfile.validate(inputfile)
    #a = mrcfile.validate('/Users/shi/Desktop/out1.mrc')
    if   a == True :
        print ("input file: ", file ," ok" )
    else:
        print(inputfile," is not a vaild mrc file....trying to repair")
        if outmode == 1:
            outfile = inputfile
        else:
            outfile = inputfile.rstrip(".mrc")+"_r.mrc"
        process = subprocess.Popen(["newstack",inputfile,outfile],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        #print(stdout.decode("utf-8"))
        a = mrcfile.validate(outfile)

        if a == True:
            print("file ok. saved to :", outfile)
        else:
            print("repair not succesful")
            exit()

def generate_tables(outfile="tables.csv"):
    print("Generating tables....")
    print("output to :",outfile)

    fig, ax = plt.subplots()

    # hide axes
    fig.patch.set_visible(False)
    ax.axis('off')
    ax.axis('tight')
    #pd.options.display.float_format = '${:,.2f}'.format
    #df = pd.DataFrame(np.random.randn(10, 4), columns=list('ABCD'))
    df = pd.DataFrame(list(zip(list_x,title_list,list_fokus,list_astig, list_phase,list_ccc,list_res_lim,list_B_fctor)),
                      columns=("Image #","Image","Focus","Astig","Phaseshift","CCC","Res_lim","B-factor"))
    #pd.DataFrame(list(zip(lst1, lst2, lst3)))
    df.update(df[['Focus',"Astig","Phaseshift"]].applymap('{:,.2f}'.format))
    ax.table(cellText=df.values, colLabels=df.columns, loc='center')
    df.to_csv(outfile, index=False, header=True)
    #print(df)
    fig.tight_layout()

#    plt.show()


######   main program

parameters = read_input("/home/irsen/PycharmProjects/KRIOS/gCTF/input.dat")
#print("paramters",parameters)
image_list = []
title_list = []
extension = str(parameters["extension"])
inputfolder = str(parameters["input_folder"])
files = glob.glob(inputfolder+"/*."+extension)
num_cols = int(parameters["num_cols"])
timest = datetime.datetime.now()
timestamp = str(timest.strftime("%Y-%m-%d_%H_%M"))
outpdf = timestamp+"_"+extension+".pdf"
imagefolder = str(parameters["image_folder"])
#print (outpdf)


print("Enter/Paste your content. return and Ctrl-D  to save it.")
content = []
meta = "experiment summary:"
while True:
    try:
        line = input()
    except EOFError:
        break
    content.append(line+"\n")
    meta = ' '.join(map(str, content))

print(meta)
print ("hallo")
for file in files:
#    print (file)
    title = file.split("/")
    #print (title[len(title)-1])
    title_list.append(title[len(title)-1])
    if int(parameters["run_gctf"]) == 1:
        check_mrc(file)
        command = gCTF(file)
    if  int(parameters["plot_mrc"]) == 1:
        check_mrc(file)
        img = open_mrc(file)
        image_list.append(img)
    if int(parameters["parse_gctf_log"]) == 1:
        logfile = file[:-4]+"_gctf.log"
        parse_logfile(logfile,len(title_list))

if  int(parameters["plot_mrc"]) == 1:
    #print(str(parameters["input_folder"])+"/"+outpdf)
    #print(image_list)
    #print(len(image_list),len(title_list))
    #print(num_cols)
    #show_images(image_list,cols=num_cols,outfile="out.pdf")
    show_images(image_list,cols=num_cols,outfile=str(parameters["input_folder"])+"/"+outpdf,titles=title_list)

if int(parameters["parse_gctf_log"]) == 1:
    plot_grapphs(outfile=str(parameters["input_folder"])+"/"+str(timestamp)+"_graphs.pdf")

if int(parameters["generate_tables"]) == 1:
    generate_tables(outfile=str(parameters["input_folder"])+"/"+str(timestamp)+"_tables.csv")