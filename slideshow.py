from ctypes import alignment
import tkinter as tk
from PIL import Image, ImageTk, ExifTags
import time
import sys
import os
import re

class HiddenRoot(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        #hackish way, essentially makes root window
        #as small as possible but still "focused"
        #enabling us to use the binding on <esc>
        self.wm_geometry("1920x1080+0+0")
        self.attributes('-alpha', 0)

        self.window = MySlideShow(self)
        self.window.startSlideShow()
        self.window.wm_geometry("1920x1080+0+0")

    def moveSlide(self, offset):
        self.window.moveSlide(offset)

    def moveSlideAbsolute(self, offset):
        self.window.moveSlideAbsolute(offset)

class MySlideShow(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)
        #remove window decorations 
        self.overrideredirect(True)

        #save reference to photo so that garbage collection
        #does not clear image variable in show_image()
        self.persistent_image = None
        self.imageList = []
        self.pixNum = 0

        #used to display as background image
        self.canvas = tk.Canvas(self, bg='black', bd=0, highlightthickness=0)
        self.canvas.pack(side="top", fill="both", expand=True)

        self.image = -1

        # Create a title label
        self.txtTitle = self.canvas.create_text(970,1035,text="asdf", fill="white", font=('Helvetica 60 bold'), justify=tk.CENTER)
        self.txtTitleLT = self.canvas.create_text(968,1033,text="asdf", fill="black", font=('Helvetica 60 bold'), justify=tk.CENTER)
        self.txtTitleRT = self.canvas.create_text(972,1033,text="asdf", fill="black", font=('Helvetica 60 bold'), justify=tk.CENTER)
        self.txtTitleLB = self.canvas.create_text(968,1037,text="asdf", fill="black", font=('Helvetica 60 bold'), justify=tk.CENTER)
        self.txtTitleRB = self.canvas.create_text(972,1037,text="asdf", fill="black", font=('Helvetica 60 bold'), justify=tk.CENTER)

        self.getImages()

    def moveSlide(self, offset):
        self.pixNum = (self.pixNum + offset) % len(self.imageList)
        print("Move to " + str(self.pixNum))
        self.after_cancel(self._job)
        self.startSlideShow()

    def moveSlideAbsolute(self, offset):
        self.pixNum = offset % len(self.imageList)
        print("Move to " + str(self.pixNum))
        self.after_cancel(self._job)
        self.startSlideShow()

    def showTitle(self, aTitle):
        # create a title
        self.canvas.itemconfig(self.txtTitleLT, text=aTitle)
        self.canvas.tag_raise(self.txtTitleLT)
        self.canvas.itemconfig(self.txtTitleRT, text=aTitle)
        self.canvas.tag_raise(self.txtTitleRT)
        self.canvas.itemconfig(self.txtTitleLB, text=aTitle)
        self.canvas.tag_raise(self.txtTitleLB)
        self.canvas.itemconfig(self.txtTitleRB, text=aTitle)
        self.canvas.tag_raise(self.txtTitleRB)
        self.canvas.itemconfig(self.txtTitle, text=aTitle)
        self.canvas.tag_raise(self.txtTitle)

    def getImages(self):
        '''
        Get image directory from command line or use current directory
        '''
        if len(sys.argv) == 2:
            curr_dir = sys.argv[1]
        else:
            curr_dir = 'D:\\F'

        for root, dirs, files in os.walk(curr_dir):
            for f in files:
                ft = f.lower()
                if ft.endswith(".png") or ft.endswith(".jpg") or ft.endswith(".heic") or ft.endswith(".tif"):
                    img_path = os.path.join(root, f)
                    self.imageList.append(img_path)
        self.imageList.sort()

    def startSlideShow(self, delay=5): #delay in seconds
        myimage = self.imageList[self.pixNum]
        self.pixNum = (self.pixNum + 1) % len(self.imageList)
        self.showImage(myimage)
        #its like a callback function after n seconds (cycle through pics)
        self._job = self.after(delay*1000, self.startSlideShow)

    def showImage(self, filename):
        rematch = re.search(r".*\\([^\\]*) \(\d*\)\..*$", filename)
        title=rematch.group(1)

        image = Image.open(filename)

        try:
            for tagID in ExifTags.TAGS.keys():
                if ExifTags.TAGS[tagID]=='Orientation': break

            exif = image._getexif()
            if exif[tagID] == 3:
                image=image.rotate(180, expand=True)
            elif exif[tagID] == 6:
                image=image.rotate(270, expand=True)
            elif exif[tagID] == 8:
                image=image.rotate(90, expand=True)
        except:
            pass

        img_w, img_h = image.size
        # scr_w, scr_h = self.winfo_screenwidth(), self.winfo_screenheight()
        scr_w, scr_h = 1920, 1080
        wFactor = scr_w / img_w
        hFactor = scr_h / img_h
        factor = min(wFactor, hFactor)

        width = int(img_w * factor)
        height = int(img_h * factor)
        image = image.resize((width,height))

        # width, height = min(scr_w, img_w), min(scr_h, img_h)
        # image.thumbnail((width, height), Image.ANTIALIAS)

        #set window size after scaling the original image up/down to fit screen
        #removes the border on the image
        # scaled_w, scaled_h = image.size
        # self.wm_geometry("{}x{}+{}+{}".format(scaled_w,scaled_h,0,0))
        
        # create new image 
        self.persistent_image = ImageTk.PhotoImage(image)
        if self.image < 0:
            self.image = self.canvas.create_image(960,540,image=self.persistent_image)
        else:
            self.canvas.itemconfig(self.image, image=self.persistent_image)

        self.showTitle(title)


slideShow = HiddenRoot()
slideShow.bind("<Escape>", lambda e: slideShow.destroy())  # exit on esc
slideShow.bind("<Prior>", lambda e: slideShow.moveSlide(-50))  # exit on esc
slideShow.bind("<Next>", lambda e: slideShow.moveSlide(+50))  # exit on esc
slideShow.bind("<Up>", lambda e: slideShow.moveSlide(-2))  # exit on esc
slideShow.bind("<Down>", lambda e: slideShow.moveSlide(0))  # exit on esc
slideShow.bind("<Home>", lambda e: slideShow.moveSlideAbsolute(0))  # exit on esc
slideShow.mainloop()