import numpy as np
import PIL
import sys
sys.path.append('/usr/local/lib/python2.7/site-packages')
import cv2
import os
import glob
from PIL import Image
import argparse
import logging


log = logging.getLogger()

#define function to sort the contours from left to right
def greater_by_x(a, b):
        x,y,w,h = cv2.boundingRect(a)
        x1,y1,w1,h1 = cv2.boundingRect(b)
        if x>x1:
           #print "returning 1"
           return 1
        else:
           #print "returning 0"
           return -1

#define the function 
def process_images_and_extract_contours(mypath,root_path, input_directory):
    imagelist = []
    imagelist = glob.glob(mypath)
    #Make the directories to put the contours in
    if not os.path.exists(input_directory):
	    images_output= os.makedirs(input_directory)
    for imagefn in imagelist:
	    fn=os.path.basename(os.path.normpath(imagefn))
	    img = cv2.imread(imagefn, cv2.CV_8UC1)
	    if img is None:
		continue
	    #if dir exists then don't make it else make it
            log.info("Processing image = %s",imagefn)
	    if not os.path.exists(input_directory+"/"+fn[:-4]):
		os.makedirs(input_directory+"/"+ fn[:-4])
		os.makedirs(input_directory+"/"+fn[:-4]+"/"+"contours/")
	    #Find the contours in the image
	    img3,contours,hierarchy = cv2.findContours(img.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	    cntr =0
	    tosave = img.copy()
	    #Sort the contours
	    contours.sort(greater_by_x) 
	    for contour in contours:
		a = cv2.contourArea(contour)
		#If the contour is too small skip it
		if a < 1000:
		    continue
		x,y,w,h = cv2.boundingRect(contour)
		#extract the contour from the image
		letter = tosave[y:y+h, x:x+w]
#		letter = ~letter
		cv2.rectangle(img, (x,y), (x+w, y+h),(0, 255,0), 3)
		cntr+=1 
		cfnm = root_path+"/"+input_directory + "/" + fn[:-4]+ "/contours" + "/"+str(cntr)+'.jpg'
		#Write the contour to the file path
		cv2.imwrite(cfnm, letter)
		temp_filename = "tempfile.jpg"
		Image.open(cfnm).convert('L').save(temp_filename)
		imsize=28,28 
		im = Image.open(temp_filename)
		im1 = im.resize(imsize, Image.ANTIALIAS)
		#Reshape the image and write it
		imgArr = np.array(im1.getdata(), np.uint8)
		log.debug(imgArr.shape)
		with open(cfnm, 'wr+') as f:
			 f.write(imgArr.flatten())
		f.close()
		
		img_numpy_array = np.fromfile(cfnm,dtype=np.uint8)
		reshaped_numpy_image_array = img_numpy_array.reshape(28,28)





#command line arguments
if __name__ == '__main__':	
    parser = argparse.ArgumentParser(description = "path name")
    parser.add_argument("--my_path")
    parser.add_argument("--root_path")
    parser.add_argument("--input_directory")
    parser.add_argument("--logging_level",type=int)
    parser.set_defaults(root_path = "/home/ubuntu/solver")
    parser.set_defaults(my_path = "/home/ubuntu/solver/images/")
    parser.set_defaults(logging_level = logging.INFO)
    args = parser.parse_args()
    mypath = args.my_path + "*.jpg"
    root_path = args.root_path
    input_directory = args.input_directory
    
    streamhandler = logging.StreamHandler(sys.stdout)
    
    if args.logging_level==10:
       streamhandler.setLevel(logging.INFO)
       log.setLevel(logging.INFO)
    if args.logging_level==20:
       streamhandler.setLevel(logging.DEBUG)
       log.setLevel(logging.DEBUG)

    filehandler = logging.FileHandler("logging")
    formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")

    streamhandler.setFormatter(formatter)
    log.addHandler(streamhandler)
    process_images_and_extract_contours(mypath,root_path, input_directory) 
