from tkinter import CURRENT
import tkinter as tk
from tkinter import ttk
import sys,os,string,time
from config import *

class Polygon():
    '''
    root: Tk() object parent of canvas
    canvas: Canvas tkinter object on root
    pts: points of corners on the canvas 
    radius: radius of each point default = 4
    '''
    def __init__(self,root,canvas,pts,radius=4):
        self.canvas = canvas
        self.root = root
        self.points = [] 
        self.enter_status = [0]*len(pts)
        self.drag_status = [0]*len(pts)
        self.pt_coords = pts
        self.point_in_use = None
        self.poly_type = None
        self.type_text = None
        self.type_bg = None
        self.now_showing_type = False
        self.radius = SMALL_RADIUS 
        self.inside_poly = False
        self.down_inside_poly = False
        self.select_poly = False

        # Add points to list of points
        self.initialize_points()
        #flatten = lambda l: [item for sublist in l for item in sublist]
        # Create a polygon tkinter widget
        self.polygon = self.canvas.create_polygon(
            self.flatten(),
            outline = 'red',
            fill = '',
            tag = 'Quad')
        self.draw_points()        
        for pt in self.points:
            # Binds point on which LMB(Left Mouse Button is pressed)
            self.canvas.tag_bind(pt,"<ButtonPress-1>",self.down)
            # Binds point on which LMB is unpressed
            self.canvas.tag_bind(pt,"<ButtonRelease-1>",self.chkup)
            # Binds self.enter to point on which the cursor enters
            self.canvas.tag_bind(pt,"<Enter>",self.enter)
            # Binds self.leave to point on which the cursor exits
            self.canvas.tag_bind(pt,"<Leave>",self.leave)

        self.canvas.tag_bind(self.polygon,"<Enter>",self.enter_poly)
        self.canvas.tag_bind(self.polygon,"<Leave>",self.leave_poly)
        self.canvas.tag_bind(self.polygon,"<ButtonPress-1>",self.down_poly)
        self.canvas.tag_bind(self.polygon,"<ButtonRelease-1>",self.chkup_poly)

    def enter_poly(self,event):
        self.inside_poly = True
        if self.select_poly == False:
            self.canvas.itemconfigure(CURRENT,stipple='gray25',fill='blue')

    def delete_self(self):
        print ("Deleting Polygon:",self.polygon)
        for pt in self.points:
            self.canvas.delete(pt)
        self.canvas.delete(self.polygon)
        if self.type_text != None:
            self.canvas.delete(self.type_text)
            self.type_text = None
        if self.type_bg != None:
            self.canvas.delete(self.type_bg)
            self.type_text = None

    def leave_poly(self,event):
        self.inside_poly = False
        self.down_inside_poly = False
        if self.select_poly == False:
            self.canvas.itemconfigure(CURRENT,stipple='', fill = '')

    def down_poly(self,event):
        self.down_inside_poly = True

    def chkup_poly(self,event):
        if self.down_inside_poly == True:
            if self.select_poly == False:
                self.canvas.itemconfigure(CURRENT,fill = 'red',stipple='gray50')
                self.select_poly = True
                #self.show_type()
                self.points_bigger()
            elif self.select_poly == True:
                self.canvas.itemconfigure(CURRENT,fill = '',stipple='')
                self.select_poly = False
                #self.unshow_type()
                self.points_smaller()
                self.canvas.tag_raise(self.polygon)
                self.draw_points()
        self.down_inside_poly = False


    def flatten(self):
        l = self.pt_coords
        return [item for sublist in l for item in sublist]

    # draw circular point widgets on the canvas
    def initialize_points(self):
        for i in range(len(self.pt_coords)):
            self.points.append(
                self.canvas.create_oval(
                    self.pt_coords[i][0]-self.radius,self.pt_coords[i][1]-self.radius,
                    self.pt_coords[i][0]+self.radius,self.pt_coords[i][1]+self.radius,
                    fill = "green",
                    tag = "Point"
                )
            )
    
    def show_type(self):
        if not self.now_showing_type:
            self.now_showing_type = True
        else:
            return
        sums = [0,0]
        for row in self.pt_coords:
            for i , num in enumerate(row):
                sums[i] += num
        center = [int(x/len(self.pt_coords)) for x in sums]
        if self.poly_type == None:
            text = "None"
        else:
            text = self.poly_type
        self.type_text = self.canvas.create_text(*center,anchor=tk.CENTER,font=("Times", FONT_SIZE,'bold'),text=text)
        self.type_bg = self.canvas.create_rectangle(self.canvas.bbox(self.type_text),fill="white")
        self.canvas.tag_lower(self.type_bg,self.type_text)

    def unshow_type(self):
        if self.now_showing_type:
            self.now_showing_type = False
        else:
            return
        self.canvas.delete(self.type_text)
        self.canvas.delete(self.type_bg)
        self.type_text = None
        self.type_bg = None

    # Triggered when cursor enters the bound widget(A point in our case)
    def enter(self,event):
        self.canvas.itemconfigure(CURRENT,fill="blue")
        self.loc = 1

    def leave(self,event):
        self.canvas.itemconfigure(CURRENT,fill="green")
 
    # Updates location of each point according to the coordinates in self.coords
    def draw_points(self):
        for i in range(len(self.points)):
            self.update_point(self.points[i],self.pt_coords[i][0],self.pt_coords[i][1])
        for pt in self.points:
            self.canvas.tag_raise(pt)

    # Updates a single point in self.coords
    def update_point(self,point_id,x,y):
        self.canvas.coords(
            point_id,
            x-self.radius,y-self.radius,
            x+self.radius,y+self.radius
        ) 
        self.pt_coords[self.points.index(point_id)] = [x,y]

    # Updates the polygon according to the changed point in self.coords
    def update_polygon(self):
        #flatten = lambda l=l: [item for sublist in l for item in sublist]
        self.canvas.coords(
            self.polygon,
            *self.flatten()
            )

    # Triggered by binding action
    def down(self,event):
        self.point_in_use = event.widget 
        event.widget.bind("<B1-Motion>",self.motion)
        self.canvas.itemconfigure(CURRENT,fill = "red")   

    # Triggered when a point is press and moved
    def motion(self,event):
        #if self.select_poly:
        #    self.unshow_type()
        self.root.config(cursor = "crosshair")
        self.point_in_use = event.widget
        self.point_in_use.itemconfigure(CURRENT,fill = "red")
        x,y = self.point_in_use.canvasx(event.x), self.point_in_use.canvasy(event.y)
        pt = self.canvas.find_withtag("current")[0]
        self.update_point(
            pt,
            self.point_in_use.canvasx(event.x),
            self.point_in_use.canvasy(event.y)
            )
        self.update_polygon()
        self.draw_points()
        #got = canvas.coords(self.point,self.x-self.radius,self.y-self.radius,self.x+self.radius,self.y+self.radius)

    # triggered when a point is unpressed
    def chkup(self,event):
        event.widget.unbind("<B1-Motion>")
        self.root.config(cursor = "")
        self.canvas.itemconfigure(CURRENT,fill="green")
        #if self.select_poly:
        #    self.show_type()

    def deselect_poly(self):
        if self.select_poly == False:
            pass
        else:
            self.canvas.itemconfigure(self.polygon,fill = '',stipple='')
            self.select_poly = False
            #self.unshow_type()
            self.down_inside_poly = False
            self.points_smaller()

    def points_smaller(self):
        self.radius = SMALL_RADIUS
        self.draw_points()

    def points_bigger(self):
        self.radius = BIG_RADIUS
        self.draw_points()
