import os
import numpy as np, cv2

"""
directory = "cat"

for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    # checking if it is a file
    if os.path.isfile(f):
        with open(f, "rb") as image:
            f = image.read()
            b = bytearray(f)

        with open(filename, 'wb') as file:
            file.write(b)
"""
"""
with open("cat/imag.jpeg", "rb") as image:
  f = image.read()
  b = bytearray(f)

with open('result.jpeg', 'wb') as file:
  file.write(b)
"""

"""

directory = "cat"
for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    # checking if it is a file
    if os.path.isfile(f):
        im = cv2.imread(f)
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        im = cv2.filter2D(im, -1, kernel)
        cv2.imwrite(filename, im)

"""
with open("cat/imag.jpeg", "rb") as image:
  f = image.read()
  b = bytearray(f)
  img = str(b, 'utf-8')

nparr = np.fromstring(img, np.uint8)
im = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
im = cv2.filter2D(im, -1, kernel)
cv2.imwrite("imag.jpeg", im)