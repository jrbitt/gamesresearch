#Download de imagens

import os
import io
import requests
import hashlib
from PIL import Image

arq = open('urls.txt','r')
out_dir = '/Users/jrbitt/Dropbox/full2/'
for line in arq:
    line = line[:-1]
    print line
    r = requests.get(line, stream=True)
    if r.status_code == 200:
        i = Image.open(io.BytesIO(r.content)).convert('RGB')
        name = hashlib.sha1(line).hexdigest()+'.jpg'
        i.save(os.path.join(out_dir,name))
        print out_dir+name
    