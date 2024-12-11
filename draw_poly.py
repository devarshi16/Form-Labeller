from tkinter import Tk,Canvas
import tkinter as tk
from config import *
from log_debug import *
import os

class DrawPoly():
    def __init__(self,root,canvas,img_on_cnv,radius = 4):
       self.root = root
       self.canvas = canvas
       self.img_on_cnv = img_on_cnv
       self.points = []
       self.pt_coords = []
       self.polygon = None
       self.radius = SMALL_RADIUS
       self.canvas.update()
       self.x1, self.y1 = canvas.canvasx(0), canvas.canvasy(0)
       self.canvas.bind('<ButtonRelease-1>',self.draw_point)

    def draw_point(self,event):
        debug (1, "inside draw point")
        if self.img_on_cnv.drawing_polygon == False:
            debug (2,"no point being drawn because not drawing polygon")
            return
        else:
            x,y = event.x+self.x1,event.y+self.y1
            if x > self.img_on_cnv.img_width*self.img_on_cnv.scale_factor or y > self.img_on_cnv.img_height*self.img_on_cnv.scale_factor:
                return
            else:
                self.pt_coords.append([x,y])
                self.points.append(
                    self.canvas.create_oval(
                    x - self.radius, y - self.radius,
                    x + self.radius, y + self.radius,
                    fill = "green",
                    tag = "Point"
                    )
                )
                self.canvas.tag_bind(self.points[-1],"<Enter>",self.enter_point)
                self.canvas.tag_bind(self.points[-1],"<Leave>",self.leave_point)
                self.canvas.tag_bind(self.points[-1],"<ButtonRelease-3>",self.chkup_rmb_point)

    def enter_point(self,event):
        pt = self.canvas.find_withtag("current")[0]
        self.canvas.itemconfigure(pt,fill = "blue")
        
    def leave_point(self,event):
        pt = self.canvas.find_withtag("current")[0]
        self.canvas.itemconfigure(pt,fill = "green")

    def chkup_rmb_point(self,event):
        pt = self.canvas.find_withtag("current")[0]
        index_pt = self.points.index(pt)
        self.canvas.delete(pt)
        self.points.pop(index_pt)
        self.pt_coords.pop(index_pt)

    def delete_self(self):
        #self.canvas.delete(self.polygon)
        for pt in self.points:
            self.canvas.delete(pt)
        self.pt_coords = []
        self.polygon = None
        self.canvas.update()
