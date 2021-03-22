import numpy as np
import cv2
from collections import namedtuple
from enum import Enum, auto
import shutil
import os

# Named Tuples
Point = namedtuple("Point", ["x", "y"])
Color = namedtuple("Color", ["lower", "upper"])

# Enums
class PixelType(Enum):
  DENDRITE = auto()
  SOMA = auto()
  BACKGROUND = auto()
  UNKNOWN = auto()

class Direction(Enum):
  N, E, S, W = auto(), auto(), auto(), auto()
  NE, NW, SE, SW = auto(), auto(), auto(), auto()


# Image Processing Functions
def pc_to_255(H, S, V):
  """
  Converts the 360-100-100 format of HSV to the OpenCV
  180-255-255 HSV format.
  
  H:  Hue
  S:  Saturation
  V:  Value

  For more info: 
  https://docs.opencv.org/master/df/d9d/tutorial_py_colorspaces.html
  """
  return (H/2, ((S/100) * 255), ((V/100) * 255))


def gaussian(im, rad):
  """
  Takes in an image array/image filepath and applies a Gaussian 
  blur filter with the given radius.
  
  im:   a numpy array representing an image, or a path to an image
        file
  rad:  the radius for the gaussian blur filter
  """
  if type(im) == str:
    im = cv2.imread(im)
  im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
  blur = cv2.GaussianBlur(im,(rad, rad), 0)
  return blur

def watershed(curr_img):
  if type(curr_img) == str:
    curr_img = cv2.imread(curr_img)

  color = Color(pc_to_255(0, 0, 39), pc_to_255(360, 0, 100))

  hsv = cv2.cvtColor(curr_img, cv2.COLOR_BGR2HSV)
  mask = cv2.inRange(hsv, color.lower, color.upper)
  kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
  opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

  sure_bg = cv2.dilate(opening,kernel,iterations=2)

  dist_transform = cv2.distanceTransform(opening,cv2.DIST_L2,5)
  ret, sure_fg = cv2.threshold(dist_transform,0.7*dist_transform.max(), 255, 0)

  sure_fg = np.uint8(sure_fg)
  unknown = cv2.subtract(sure_bg,sure_fg)

  ret, markers = cv2.connectedComponents(sure_fg)

  markers = markers + 1

  markers[unknown == 255] = 0

  markers = cv2.watershed(curr_img,markers)
  curr_img[markers == -1] = [255,0,0]

  return curr_img

## CLASSES ##

# Soma
class Soma():

  def __init__(self, contour):
    """ 
    contour is an array generated in the generate_somas
    method in the ImageGraph class
    """
    self.contour = contour
    self.centroid = self.__calculate_centroid(contour)

  def __calculate_centroid(self, arr):
    arr = np.array([i[0] for i in arr])
    length = arr.shape[0]
    sum_x = np.sum(arr[:, 0])
    sum_y = np.sum(arr[:, 1])
    return Point(x=round(sum_x/length), y=round(sum_y/length))

# Image
class Image():

  def __init__(self, image):
    self.image_path = image
    self.original_image = cv2.imread(self.image_path)
   
    
    if not os.path.exists("data"):
      os.mkdir("data")
      os.mkdir("data/images")

    shutil.copyfile(self.image_path, "data/images/original_image.png")

    self.shape = self.original_image.shape[:2]

    self.cell_outlines = self.__generate_cell_outlines()

    self.somas_img, self.somas = self.__generate_somas()

    self.num_cells = len(self.somas)

    self.bw_image = self.__generate_BW()

    self.map, self.final_image = self.__generate_map_and_final_img()


  def __generate_cell_outlines(self):
    cv2.imwrite("data/images/gaussian.png", gaussian(self.original_image, 3))
    watershed_temp = watershed("data/images/gaussian.png")
    for y in range(len(watershed_temp)):
      for x in range(len(watershed_temp[0])):
        if not np.array_equal(watershed_temp[y][x] , np.array([255, 0, 0])):
          watershed_temp[y][x] = [0, 0, 0]

    watershed_temp[:, 0] = [0, 0, 0]
    watershed_temp[:, -1] = [0, 0, 0]
    watershed_temp[0, :] = [0, 0, 0]
    watershed_temp[-1, :] = [0, 0, 0]

    cv2.imwrite("data/images/outlines.png", watershed_temp)
    return watershed_temp


  def __generate_somas(self):
    cell_img = cv2.cvtColor(self.cell_outlines, cv2.COLOR_BGR2GRAY)

    cnts = cv2.findContours(cell_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    somas = []
    for c in cnts:
        cv2.drawContours(cell_img,[c], 0, (255,255,255), -1)
        somas.append(Soma(c))

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20,20))
    opening = cv2.morphologyEx(cell_img, cv2.MORPH_OPEN, kernel, iterations=2)

    cv2.imwrite("data/images/cells.png", cell_img)
    return cell_img, somas


  def __generate_BW(self):
    bw_img = self.original_image.copy()

    for i in range(len(bw_img)):
      for j in range(len(bw_img[i])):
        if bw_img[i][j][2] < 60:
          bw_img[i][j] = [0, 0, 0]
        else:
          bw_img[i][j] = [255, 255, 255]
    
    cv2.imwrite("data/images/bw_paths.png", bw_img)
    return bw_img

  def __generate_map_and_final_img(self):
    pmap = np.full(self.bw_image.shape[0:2], PixelType.UNKNOWN)
    final_image = np.zeros(self.bw_image.shape)

    for y in range(self.bw_image.shape[0]):
      for x in range(self.bw_image.shape[1]):
        if self.somas_img[y][x] == 255:
          pmap[y][x] = PixelType.SOMA
          final_image[y][x] = np.array([255, 0, 255])
        elif np.array_equal(self.bw_image[y][x], [255, 255, 255]):
          pmap[y][x] = PixelType.DENDRITE
          final_image[y][x] = np.array([255, 255, 255])
        else: #np.array_equal(self.bw_image[y][x], [0, 0, 0]):
          pmap[y][x] = PixelType.BACKGROUND
          final_image[y][x] = np.array([0, 0, 0])
      
    cv2.imwrite("data/images/final_image.png", final_image)
    return pmap, final_image


# Graph Node
class PixelNode():

  def __init__(self, px_type, point):
    self.px_type = px_type
    self.x, self.y = point.x, point.y

    self.neighbors = dict.fromkeys([
                                    Direction.N,  Direction.E, 
                                    Direction.S,  Direction.W,
                                    Direction.NE, Direction.NW,
                                    Direction.SE, Direction.SW
                                   ])
  def __str__(self):
    return "< " + self.px_type.name + " @ (" + str(self.x) + ", " + str(self.y) + ") >" 

  def __repr__(self):
    return "< " + self.px_type.name + " @ (" + str(self.x) + ", " + str(self.y) + ") >" 

# Graph
class PixelGraph():

  directions = {Direction.NW : {"x":-1, "y":-1},   Direction.N : {"x":0, "y":-1}, Direction.NE : {"x":1, "y":-1},
                 Direction.W : {"x":-1, "y": 0},                                   Direction.E : {"x":1, "y": 0},
                Direction.SW : {"x":-1, "y": 1},   Direction.S : {"x":0, "y": 1}, Direction.SE : {"x":1, "y": 1}}

  def __init__(self, img_obj):
    self.image_obj = img_obj
    self.somas = self.image_obj.somas

    self.node_map = self.__generate_node_map()

    self.__connect_all_nodes()

  def __generate_node_map(self):
    nmap = np.full(self.image_obj.shape, None)

    for y in range(nmap.shape[0]):
      for x in range(nmap.shape[1]):
        if self.image_obj.map[y][x] != PixelType.BACKGROUND:
          nmap[y][x] = PixelNode(self.image_obj.map[y][x], Point(x=x, y=y))

    return nmap
  
  def __connect_all_nodes(self):

    for y in range(self.node_map.shape[0]):
      for x in range(self.node_map.shape[1]):
        if self.node_map[y][x] is not None:
          self.__node_connector(x, y)

  
  def __node_connector(self, x, y):
    for dir, pt_diffs in PixelGraph.directions.items():
      pt = Point(x=(x + pt_diffs["x"]), y=(y + pt_diffs["y"]))
      if self.__in_range(pt) and self.node_map[y][x] is not None:
        self.node_map[y][x].neighbors[dir] = self.node_map[pt.y][pt.x]


  def __in_range(self, pt):
    y_in_range = pt.y >= 0 and pt.y < self.node_map.shape[0]
    x_in_range = pt.x >= 0 and pt.x < self.node_map.shape[1]
    return y_in_range and x_in_range

  def get_node(self, pt):
    return self.node_map[pt.y][pt.x]
