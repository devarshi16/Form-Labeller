from tkinter import Tk,Canvas
import tkinter as tk
from config import *
from log_debug import *
import os

class DrawRect():
    def __init__(self,root,canvas,img_on_cnv,radius = 4):
        self.root = root
        self.canvas = canvas
        self.img_on_cnv = img_on_cnv
        self.points = []
        self.pt_coords = []
        self.radius = SMALL_RADIUS
        self.polygon = None
        self.canvas.update()       
        self.canvas.bind("<ButtonPress-1>",self.lmb_down)
        self.canvas.bind("<ButtonRelease-1>",self.lmb_up)

    def lmb_down(self,event):
        x,y = event.x,event.y
        
        self.create_point(x,y)
        self.create_point(x,y)
        self.create_point(x,y)
        self.create_point(x,y)
        self.polygon = self.canvas.create_polygon(
            *self.flatten(),
            outline = 'blue',
            fill = '',
            tag = 'Rect')
        self.canvas.bind('<Motion>',self.mouse_motion)
        
    def mouse_motion(self,event):
        x,y = event.x, event.y
        self.update_point(self.points[3],x,self.pt_coords[0][1])
        self.update_point(self.points[1],self.pt_coords[0][0],y)        
        self.update_point(self.points[2],x,y)
        self.canvas.coords(self.polygon,*self.flatten())
        self.canvas.update()

    def lmb_up(self,event):
        self.canvas.unbind('<Motion>')
        self.canvas.unbind('<ButtonRelease-1>')
        self.canvas.unbind('<ButtonPress-1>')

    def flatten(self):
        l = self.pt_coords[:]
        return [item for sublist in l for item in sublist]

    def create_point(self,x,y):
        self.pt_coords.append([x,y])
        self.points.append(
            self.canvas.create_oval(
                x-self.radius,y-self.radius,
                x+self.radius,y+self.radius,
                fill = "green",
                tag = "Point"
                )
            )

    def update_point(self,point_id,x,y):
        self.canvas.coords(
            point_id,
            x-self.radius,y-self.radius,
            x+self.radius,y+self.radius
        )
        self.pt_coords[self.points.index(point_id)] = [x,y]

    def delete_self(self):
        self.canvas.delete(self.polygon)
        for pt in self.points:
            self.canvas.delete(pt)
        self.pt_coords = []
        self.polygon = None
        self.canvas.update()
