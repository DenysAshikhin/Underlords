import os
import cv2
root = "C:/Program Files (x86)/Steam/userdata/87849181/760/remote/1046930/screenshots/"
save = "D:/Documents/underlords save/"

files = os.listdir(root)

for file in files:
    file_name = os.path.join(root,file)
    print(files)
    img = cv2.imread(file_name)
    crop = img[10:10+56, 550:550+50]
    cv2.imwrite(os.path.join(save,file), crop)
