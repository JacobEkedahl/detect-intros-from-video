import threading
import time
from tkinter import *

import cv2
import PIL.Image
import PIL.ImageTk

import file_handler
import imutils
import svtplaywrapper

START_TIME = 0
WIDTH_VIDEO = 450
HEIGHT_VIDEO = 250

#"gui/temp/al-pitcher-pa-paus.s01e01.avsnitt-1-converted.mp4"
class App:
    def __init__(self, root, window_title):
        #clear temp of old downloads, or missdownloads
        file_handler.clear_temp()

        #init root window with title and setting a reference for it within this class
        self.root = root
        root.title(window_title)

        #init the main frames of the app
        self.infoFrame = Frame(self.root)
        self.infoFrame.grid(row= 0, column=0)

        #Entry and description for downloading url
        self.lbl = Label(self.infoFrame, text="Enter Url")
        self.lbl.grid(row=0, column=0, sticky = N, pady= 5)
        self.txt = Entry(self.infoFrame, width=60)
        self.txt.grid(row=0, column=1, sticky=N, pady= 5)
        self.txt.focus()

        #Buttons for interacting with application
        self.buttonFrame = Frame(self.infoFrame)
        self.buttonFrame.grid(row= 1, column=1, sticky=E, pady=5, padx=5)
        self.clear_btn = Button(self.buttonFrame, text="Clear", pady=2, command=self.clear_box)
        self.clear_btn.grid(row= 0, column=2)
        self.intro_btn = Button(self.buttonFrame, text="Submit", pady=2, command=self.download)
        self.intro_btn.grid(row= 0, column=3)

    def replace_text_in_box(self, text):
        self.txt.delete(0,END)
        self.txt.insert(0,text)

    def clear_box(self):
        self.txt.delete(0,END)
        
    def refresh(self):
        self.root.update()
        self.root.after(1000,self.refresh)

    def set_new_video(self):
        self.videoFrame = Frame(self.root)
        self.videoFrame.grid(row=1, column=0)
        self.video_source = "gui/temp/current-converted.mp4"
        self.vid = MyVideoCapture(self.video_source)
        self.canvas = Canvas(self.videoFrame, width = WIDTH_VIDEO, height = HEIGHT_VIDEO)
        self.canvas.pack()
        self.display()

    def download(self):
        url = self.txt.get()
        if not url.startswith("http"):
            self.replace_text_in_box('http')
            return
        
        #Callback function
        def use_svtplay():
            self.check_submit_thread() 
            self.intro_btn.configure(state=DISABLED)
            self.clear_btn.configure(state=DISABLED)
            self.intro_btn.grid(row= 0, column=3)
            svtplaywrapper.download_video(url)
            self.intro_btn.configure(state=NORMAL)
            self.clear_btn.configure(state=NORMAL)
            self.clear_box()
            self.set_new_video()
        
        global submit_thread
        submit_thread = threading.Thread(target=use_svtplay)
        submit_thread.start()

    # will check if this thread is done, (for future impl of loadingbar)
    def check_submit_thread(self):
        if submit_thread.is_alive():
            self.root.after(20, self.check_submit_thread)
        else:
            print("done")
            #progressbar.stop()

    # Will only display first frame of the video atm
    def display(self):
        ret, frame = self.vid.get_frame(START_TIME)
        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image = self.photo, anchor = NW)

class MyVideoCapture:
    def __init__(self, video_source=0):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)
        # Get video source width and height
        self.width = WIDTH_VIDEO
        self.height = HEIGHT_VIDEO

    def get_frame(self, time):
        if self.vid.isOpened():
            self.vid.set(cv2.CAP_PROP_POS_MSEC,time*1000)
            ret, frame = self.vid.read()
            frame = imutils.resize(frame, width=WIDTH_VIDEO, height=HEIGHT_VIDEO)
            if ret:
            # Return a boolean success flag and the current frame converted to BGR
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (ret, None)

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
# Create a window and pass it to the Application object
root = Tk()
GUI = App(root, "Svtplay Intro Detector")
root.mainloop()
