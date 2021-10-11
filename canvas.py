from polygon import Polygon
from log_debug import debug,logger
from PIL import ImageTk,Image,ImageOps
from config import * 
import json
import os
from threading import Lock
from tkinter import Scrollbar,HORIZONTAL,BOTTOM,RIGHT,VERTICAL,X,Y,ALL

class ImageOnCanvas():
    def __init__(self,root,frame,canvas,image_path):
        self.image_path = image_path
        self.json_path = '.'.join(image_path.split('.')[:-1])+".json"
        #self.json_path = '.'.join(os.path.split(image_path)[-1].split('.')[:-1])+".json"
        self.root = root
        self.canvas = canvas
        
        self.img = Image.open(self.image_path)
        self.img_width,self.img_height = self.img.size
        self.scale_factor = None
        self.imagetk = None
        ###
        
       
        self.canvas.update()
        #self.img.thumbnail((max_w,max_h),Image.ANTIALIAS)
        self.imagetk = ImageTk.PhotoImage(self.img)
        self.scale_factor = self.img.size[0]/self.img_width
        ####
        #self.resize()
        self.canvas_img = self.canvas.create_image(0,0,anchor='nw',image=self.imagetk)
        canvas.config(scrollregion=canvas.bbox(ALL))
        self.canvas.update()
        self.bbs = []
        self.polygons = []
        self.poly_type = []
        self.polygons_mutex = Lock()
        self.load_json()
        self.draw_bbs(self.bbs)
        self.drawing_polygon = False

    def current_state(self):
        return self.bbs, self.polygons, self.poly_type, self.drawing_polygon

    def resize(self):
        self.canvas.update()
        max_w,max_h = self.canvas.winfo_width(), self.canvas.winfo_height()
        self.canvas.configure(scrollregion=(0,0,max_w,max_h), yscrollcommand=self.vbar.set, xscrollcommand=self.hbar.set)
        #self.img.thumbnail((max_w,max_h),Image.ANTIALIAS)
        self.imagetk = ImageTk.PhotoImage(self.img)
        self.scale_factor = self.img.size[0]/self.img_width

    def load_json(self):
        debug (2,"Loading json from:"+self.json_path)
        try:
            fl =  open(self.json_path,'r')
            data = json.load(fl)
            boxes = data["textBBs"]
            for i,item in enumerate(boxes):
                debug (2, str(item))
                pts = item["poly_points"]
                for i in range(len(pts)):
                    pts[i][0],pts[i][1] = int(pts[i][0]),int(pts[i][1])
                self.bbs.append(pts)
                self.poly_type.append(item["type"])
                debug (2, str(self.poly_type))
            fl.close()
        except:
            fl = open(self.json_path,'w+')
            data = {"textBBs":[]}
            json.dump(data,fl,indent=4)
            fl.close()
        debug(3, "Total BBs in json:"+str(len(self.bbs)))        
    
    def save_json(self,out_dir):
        img_name = os.path.split(self.image_path)[-1]
        data = {}
        data["textBBs"]=[]
        self.polygons_mutex.acquire()
        poly_copy = self.polygons[:]
        for j,poly in enumerate(poly_copy):
            pt_data = {}
            pts = []
            for i in range(len(poly.pt_coords)):
                pts.append([int(poly.pt_coords[i][0]),int(poly.pt_coords[i][1])])
            '''            
            if self.scale_factor!=None:
                for i in range(len(poly.pt_coords)):
                    pts.append([int(poly.pt_coords[i][0]/self.scale_factor),int(poly.pt_coords[i][1]/self.scale_factor)])
            else:
                for i in range(len(poly.pt_coords)):
                    pts.append([int(poly.pt_coords[i][0]),int(poly.pt_coords[i][1])])
            '''
            pt_data["poly_points"] = pts
            pt_data["id"] = str(j)
            pt_data["type"] = poly.poly_type
            data["textBBs"].append(pt_data)
        self.polygons_mutex.release()
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        json_file_path = os.path.join(out_dir,'.'.join(img_name.split('.')[:-1])+'.json')
        print ("Saving json to",json_file_path)
        debug (2,"No of polygons drawn: "+str(len(data["textBBs"])))
        with open(json_file_path,'w') as fl:
            json.dump(data,fl,indent=4)

    def draw_bbs(self,bbs):
        self.polygons_mutex.acquire()
        for bb in bbs:
            if self.scale_factor == None:
                self.polygons.append(Polygon(self.root,self.canvas,bb,radius=RADIUS))
                continue
            for i in range(len(bb)):
                for j in range(2):
                    bb[i][j] = bb[i][j] * self.scale_factor
            self.polygons.append(Polygon(self.root,self.canvas,bb,radius=RADIUS))
        for i,pt in enumerate(self.poly_type):
            self.polygons[i].poly_type = pt
        self.polygons_mutex.release()
        debug (3,"Total Polygons drawn:"+str(len(self.polygons)))

    def add_poly(self, pts):
        if self.scale_factor == None:
            self.bbs.append(pts)
            self.polygons.append(Polygon(self.root,self.canvas,bb,radius=RADIUS))
        else:
            pts_copy = pts[:]
            for i in range(len(pts)):
                for j in range(2):
                    pts_copy[i][j] = pts[i][j] * self.scale_factor
            self.bbs.append(pts_copy)
            self.polygons.append(Polygon(self.root,self.canvas,pts_copy,radius=RADIUS))
        self.poly_type.append(None)
        self.polygons[-1].poly_type = None
        debug (3,"Polygon added, total polygons: "+ str(len(self.polygons)))
