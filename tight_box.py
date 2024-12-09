import cv2
from polygon import Polygon
import numpy as np
changed_poly = []
class TightBox():
    def __init__(self,root,cnv,thresh):
        self.root = root
        self.cnv = cnv
        self.thresh = thresh
        self.changed_poly = []

    def tight_box(self):
        _,polygons,_,_,_ = self.cnv.current_state()
        for p in polygons:
            if p.select_poly:
                
                cnt = []
                for pt in p.points:
                    cnt.append(p.get_pt_center(pt))
                self.changed_poly.append([p,cnt])
                print(cnt)
                cnt = np.array(cnt).reshape((-1,1,2)).astype(np.int32)
                # Load a cv image from path
                img = cv2.imread(self.cnv.image_path)
                # Resize the CV image according to the size of thumbnail image in ImageCanvas object
                img = cv2.resize(img,self.cnv.img.size,interpolation = cv2.INTER_AREA)
                # Create a mask around the contour
                mask = np.zeros(img.shape[:2],np.uint8)
                #cv2.polylines(mask, [cnt], True, (255,255,255), thickness=3)
                #cv2.drawContours(mask,cnt,-1,(255),1)
                cv2.fillPoly(mask,pts=[cnt],color=(255,255,255))
                #cv2.imshow('new window',mask)
                #cv2.waitKey(0)
                #cv2.destroyAllWindows()
                # Convert image to gray
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                # Threshold image by the threshold set in GUI
                _,img = cv2.threshold(img, self.thresh, 255, cv2.THRESH_BINARY)
                # Mask the cv image using the mask
                new_img = cv2.bitwise_and(img,img,mask=mask)
                
                # Find new contours in the masked image
                new_cnts,_ = cv2.findContours(new_img,cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                # Sort the contours according to their area, descending order
                # Don't consider the first element (biggest area)
                # As what we are only interested with what is inside it
                new_cnts = sorted(new_cnts,key=cv2.contourArea,reverse=True)[1:]
                # Add each point to a list for finding min area rect around it
                all_pts = [pt for ct in new_cnts for pt in ct]
                all_pts = np.array(all_pts).reshape((-1,1,2)).astype(np.int32)
                min_area_rect = cv2.minAreaRect(all_pts)
                # Convert min area rect to box points (4 points)
                box = cv2.boxPoints(min_area_rect)
                box = np.intp(box)
                for i,point in enumerate(p.points):
                    p.update_point(point,box[i][0],box[i][1])
                print(box)
                p.update_polygon()
                p.draw_points()
        #self.cnv.canvas.update()

    def save_tight_box(self):
        pass

    def discard_tight_box(self):
        for p,pts in self.changed_poly:
            for i,pt in enumerate(p.points):
                p.update_point(pt,pts[i][0],pts[i][1])
            p.update_polygon()
            p.draw_points()
        self.cnv.canvas.update()


