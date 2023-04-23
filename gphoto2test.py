#!/usr/bin/env python



import gphoto2 as gp

cam = gp.Camera()
cam.init()

#text = cam.get_summary()
#print(str(text))

folder = '/store_00020001/DCIM/101EOSR5/'

result = cam.folder_list_files(folder)
for line in result:
  print(str(line[0]))

  file = cam.file_get(folder,line[0],gp.GP_FILE_TYPE_NORMAL)
  print(dir(file))
  print('----')
  print(dir(cam))
  #cam.file_save(file,dest)
  file.save('/tmp/sadf.cr3')
  break

#print(dir(cam))

cam.exit()

# 'gp_filesystem_number', 'gp_filesystem_put_file', 'gp_filesystem_read_file',
