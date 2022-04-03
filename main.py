from turtle import width
import cv2 as cv
from cv2 import BORDER_CONSTANT
from cv2 import flip
from cv2 import VideoWriter
from cv2 import VideoWriter_fourcc
import numpy as np

class Filter:
  def __init__(self, isEnabled, value):
    self.isEnabled = isEnabled
    self.value = value
  
  def toggle(self):
    self.isEnabled = not self.isEnabled
  
  def getIsEnabled(self):
    return self.isEnabled
  
  def getValue(self):
    return self.value

  def setValue(self, val):
    self.value = val

def print_commands():
  print('B or b: Blurring (Gaussian)')
  print('E or e: Edges (Canny)')
  print('F or f: Flip the video')
  print('+ or -: Increment/Decrement flip mode')
  print('G or g: Grayscale')
  print('N or n: Negative')
  print('O or o: Contrast')
  print('R or r: Brightness enhancement')
  print('S or s: Gradient (Sobel)')
  print('T or t: Rotate the video')
  print('V or v: Toggle video recording')
  print('Z or z: Toggle resize frame to half')

def init_filter_array():
  ### 0: gaussian
  filters = [Filter(False, 0)]
  ### 1: canny
  filters.append(Filter(False, 0))
  ### 2: sobel
  filters.append(Filter(False, 0))
  ### 3: brightness
  filters.append(Filter(False, 0))
  ### 4: contrast
  filters.append(Filter(False, 0))
  ### 5: negative
  filters.append(Filter(False, 0))
  ### 6: greyscale
  filters.append(Filter(False, 0))
  ### 7: downsize
  filters.append(Filter(False, 0))
  ### 8: 90º rotation
  filters.append(Filter(False, 0))
  ### 9: mirror_v
  filters.append(Filter(False, 0))
  ### 10: mirror_h
  filters.append(Filter(False, 0))

  return filters

def post_processing(filters, frame):
  output = frame
  # Gaussian Blur
  if filters[0].getIsEnabled():
    kernel_size = filters[0].getValue()
    if kernel_size % 2 == 0:
      kernel_size += 1
    output = cv.GaussianBlur(output, (kernel_size, kernel_size), 0)
  # Edge Detection (canny)
  if filters[1].getIsEnabled():
    output = cv.Canny(output, 100, 200)
  # Negative
  if filters[5].getIsEnabled():
    copy = output.copy()
    cv.convertScaleAbs(copy, output, 1, -255)
  # Brightness & Contrast
  if filters[3].getIsEnabled() or filters[4].getIsEnabled():
    copy = output.copy()
    alpha = 1
    beta = 0
    if filters[3].getIsEnabled():
      beta = filters[3].getValue()
    if filters[4].getIsEnabled():
      alpha = filters[4].getValue() / 100
    cv.convertScaleAbs(copy, output, alpha, beta)
  # Greyscale
  if filters[6].getIsEnabled():
    output = cv.cvtColor(output, cv.COLOR_BGR2GRAY)
  # Downsize
  if filters[7].getIsEnabled():
    height = output.shape[0] * 0.5
    width = output.shape[1] * 0.5
    dim = (int(width), int(height))
    output = cv.resize(output, dim, interpolation = cv.INTER_AREA)
  # 90º Rotation
  if (filters[8].getValue() > 0):
    output = cv.rotate(output, cv.cv2.ROTATE_90_CLOCKWISE)
  if (filters[8].getValue() > 90):
    output = cv.rotate(output, cv.cv2.ROTATE_90_CLOCKWISE)
  if (filters[8].getValue() > 180):
    output = cv.rotate(output, cv.cv2.ROTATE_90_CLOCKWISE)
  if (filters[8].getValue() > 270):
    filters[8].setValue(0)
  # Mirror Vertical
  if filters[9].getIsEnabled():
    output = cv.flip(output, 0)
  # Mirror Horizontal
  if filters[10].getIsEnabled():
    output = cv.flip(output, 1)
  # Sobel
  if filters[2].getIsEnabled():
    copy = output.copy()
    output = cv.Sobel(copy,cv.CV_64F,1,1,ksize=5)
  
  return output

def onChange(x):
  pass

def main():
  camera = 0
  cap = cv.VideoCapture(camera)
  # open the default camera, use something different from 0 otherwise;
  # Check VideoCapture documentation.
  if ( not cap.open(camera) ):
    return 0
  
  # creating filter boolean array
  filters = init_filter_array()
  flip_mode = 0

  # print commands
  print_commands()

  # create windows and trackbar
  cv.namedWindow('input')
  cv.namedWindow('output')
  cv.createTrackbar('Value', 'output', 0, 255, onChange)
  trackbar_index = 0

  # open video stream
  video = VideoWriter('webcam.avi', VideoWriter_fourcc(*'MP42'), 25.0, (640, 480))
  isRecording = False
  
  while True:
    # getting frame and declaring output
    ret, frame = cap.read()
    output_frame = frame

    if( frame is None ):
      break # end of video stream

    cv.imshow('input', frame)
    
    # reading key commands
    key = cv.waitKey(1)
    if key == 27: # stop capturing by pressing ESC
      break
    elif key == ord('b') or key == ord('B'):
      cv.setTrackbarMin('Value', 'output', 0)
      cv.setTrackbarMax('Value', 'output', 255)
      cv.setTrackbarPos('Value', 'output', 3)
      trackbar_index = 0
      filters[0].toggle()
    elif key == ord('e') or key == ord('E'):
      filters[1].toggle()
    elif key == ord('s') or key == ord('S'):
      filters[2].toggle()
    elif key == ord('f') or key == ord('F'):
      if flip_mode == 0:
        filters[9].toggle()
      elif flip_mode == 1:
        filters[10].toggle()
    elif key == ord('g') or key == ord('G'):
      filters[6].toggle()
    elif key == ord('n') or key == ord('N'):
      filters[5].toggle()
    elif key == ord('o') or key == ord('O'):
      cv.setTrackbarMin('Value', 'output', 0)
      cv.setTrackbarMax('Value', 'output', 300)
      cv.setTrackbarPos('Value', 'output', 125)
      trackbar_index = 4
      filters[4].toggle()
    elif key == ord('r') or key == ord('R'):
      cv.setTrackbarMin('Value', 'output', 0)
      cv.setTrackbarMax('Value', 'output', 255)
      cv.setTrackbarPos('Value', 'output', 50)
      trackbar_index = 3
      filters[3].toggle()
    elif (key == ord('t') or key == ord('T')) and not isRecording:
      if (not filters[8].getIsEnabled()):
        filters[8].setValue(filters[8].getValue()+90)
    elif (key == ord('z') or key == ord('Z')) and not isRecording:
      filters[7].toggle()
    elif key == ord('+'):
      flip_mode = 1
    elif key == ord('-'):
      flip_mode = 0
    elif key == ord('v') or key == ord('V'):
      isRecording = not isRecording

    if trackbar_index > -1 :
      trackbar_val = cv.getTrackbarPos('Value', 'output')
      filters[trackbar_index].setValue(trackbar_val)
    
    output_frame = post_processing(filters, frame)
    cv.imshow('output', output_frame)

    if isRecording:
      video.write(output_frame)
  
  cap.release()  # release the VideoCapture object
  video.release()
  cv.destroyAllWindows()
  return 0

if __name__ == "__main__":
    main()