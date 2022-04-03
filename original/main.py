import cv2 as cv
import numpy as np

def main():
  camera = 0
  cap = cv.VideoCapture(camera)
  # open the default camera, use something different from 0 otherwise;
  # Check VideoCapture documentation.
  if ( not cap.open(camera) ):
    return 0
  
  while True:
    ret, frame = cap.read()
    if( frame is None ):
      break # end of video stream
    cv.imshow("This is you, smile! :)", frame)
    if cv.waitKey(1) == 27: # stop capturing by pressing ESC
      break
  
  cap.release()  # release the VideoCapture object
  cv.destroyAllWindows()
  return 0

if __name__ == "__main__":
    main()