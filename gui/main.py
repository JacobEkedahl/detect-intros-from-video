import threading
import time
from tkinter import *
from tkinter.ttk import *

import cv2
import PIL.Image
import PIL.ImageTk

import file_handler
import imutils
import svtplaywrapper

START_TIME = 0
WIDTH_VIDEO = 480
HEIGHT_VIDEO = 253
MARGIN_TOP = 30
WIDTH_MARKER = 5 # only possible value atm

#"gui/temp/al-pitcher-pa-paus.s01e01.avsnitt-1-converted.mp4"
class App:
    def __init__(self, root, window_title):
        #clear temp of old downloads, or missdownloads
        file_handler.init_temp()
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
        self.txt.grid(row=0, column=1, sticky=N, pady= 5, padx = 5)
        self.txt.focus()

        #Buttons for interacting with application
        self.buttonFrame = Frame(self.infoFrame)
        self.buttonFrame.grid(row= 1, column=1, sticky=E, pady=5, padx=5)
        self.clear_btn = Button(self.buttonFrame, text="Clear", command=self.clear_box)
        self.clear_btn.grid(row= 0, column=2, padx=5)
        self.intro_btn = Button(self.buttonFrame, text="Submit", command=self.load)
        self.intro_btn.grid(row= 0, column=3)

        # init frame for placing slider and video
        self.videoFrame = Frame(self.root)
        self.videoFrame.grid(row=1, column=0, padx=10, sticky=N+S+W+E)

    def replace_text_in_box(self, text):
        self.txt.delete(0,END)
        self.txt.insert(0,text)

    def clear_box(self):
        self.txt.delete(0,END)
        
    def refresh(self):
        self.root.update()
        self.root.after(1000,self.refresh)
    
    def init_slider(self):
        self.w = Canvas(self.videoFrame, width=WIDTH_VIDEO + 20, height=55)
        self.move_start = False
        self.move_end = False
        self.w.bind("<ButtonRelease-1>", self.leave)
        self.w.bind("<Button-1>", self.down)
        self.w.bind ("<Leave>", self.leave)
        self.w.bind ("<Motion>", self.motion)
        self.w.pack()
        self.w.create_rectangle(10, MARGIN_TOP, WIDTH_VIDEO + 10, MARGIN_TOP, fill="black")

        self.add_start_marker()
        self.add_end_marker()
        self.start_marker_pred = self.w.create_rectangle(self.predicted_start + (WIDTH_MARKER * 2) + 2, MARGIN_TOP - 10, (self.predicted_start + WIDTH_MARKER * 3) - 2, MARGIN_TOP + 10, fill="blue")
        self.end_marker_pred = self.w.create_rectangle(self.predicted_end + (WIDTH_MARKER * 2) +2, MARGIN_TOP - 10, (self.predicted_end + WIDTH_MARKER * 3) - 2, MARGIN_TOP + 10, fill="blue")
        self.start_lbl_pred = self.w.create_text(self.predicted_start + 10,10,fill="blue",font="Times 8",
                    text=self.predicted_start)
        self.end_lbl_pred = self.w.create_text(self.predicted_end + 10,10,fill="blue",font="Times 8",
            text=self.predicted_end)

    def add_end_marker(self):
        self.end_marker = self.w.create_rectangle(self.end + WIDTH_MARKER * 2, MARGIN_TOP - 10, self.end + WIDTH_MARKER * 3, MARGIN_TOP + 10, fill="red")
        self.end_lbl = self.w.create_text(self.end + 12, MARGIN_TOP + 20,fill="red",font="Times 8",
            text=self.end)

    def add_start_marker(self):
        self.start_marker = self.w.create_rectangle(self.start + WIDTH_MARKER * 2, MARGIN_TOP - 10, self.start + WIDTH_MARKER * 3, MARGIN_TOP + 10, fill="green")
        self.start_lbl = self.w.create_text(self.start + 12,MARGIN_TOP + 20,fill="green",font="Times 8",
                    text=self.start)

    def draw_start(self):
        self.w.delete(self.start_marker)
        self.w.delete(self.start_lbl)
        self.add_start_marker()
        
    def draw_end(self):
        self.w.delete(self.end_marker)
        self.w.delete(self.end_lbl)
        self.add_end_marker()

    def down(self, event):
        x, y = event.x, event.y
        self.is_pressed = True
        if x >= self.start + 10 and x <= self.start + 15:
            self.move_start = True
        elif x >= self.end and x <= self.end + 15:
            self.move_end = True
        else:
            self.move_start = False
            self.move_end = False
    
    def leave(self, event):
        self.move_start = False
        self.move_end = False

    def motion(self, event):
        x, y = event.x, event.y
        #if x >= self.start and x <= self.start + 25:
        if x >= self.start + 10 and x <= self.start + 15 or self.move_start:
            self.root.config(cursor='hand2')
        elif x >= self.end and x <= self.end + 15 or self.move_end:
            self.root.config(cursor='hand2')
        else:
            self.root.config(cursor='')

        if self.move_start:
            if x <= 492 and x > 0:
                if x - 12 > self.end:
                    return 
                self.start = x - 12
                if self.start < 0:
                    self.start = 0
                elif self.start > 480:
                    self.start = 480
                elif self.start + 5 > self.end:
                    self.start = self.end - 5
                self.draw_start()
                self.display(self.start)
        elif self.move_end:
            if x <= 492 and x > 0:
                if self.start + 5 > x - 12:
                    return
                self.end = x - 12
                if self.end < 0:
                    self.end = 0
                elif self.end > 480:
                    self.end = 480
                elif self.start + 5 > self.end:
                    self.end = self.start + 5
            self.draw_end()
            self.display(self.end)

    def set_new_video(self):
        self.video_source = "gui/temp/current-converted.mp4"
        self.vid = MyVideoCapture(self.video_source)
        self.canvas = Canvas(self.videoFrame, width = WIDTH_VIDEO, height = HEIGHT_VIDEO)
        self.canvas.pack()
        self.display(0)

    def clear_video_frame(self):
        for child in self.videoFrame.winfo_children():
            child.destroy()

    def load(self):
        url = self.txt.get()
        if not url.startswith("http"):
            self.replace_text_in_box('http')
            print("not valid")
            return

        self.clear_video_frame()
        self.intro_fetched_completed = False
        self.download_completed = False
        self.download(url)
        self.load_slider()

    def load_slider(self):
        def get_intro_and_pred():   
            self.init_loading_intro()
            self.check_load_intro_thread() 
            time.sleep(4)
            self.start = 10
            self.end = 44.5
            self.predicted_start = 9.5
            self.predicted_end = 44
            #get intro

        global load_intro_thread
        load_intro_thread = threading.Thread(target=get_intro_and_pred)
        load_intro_thread.start()

    def init_loading_intro(self):
        self.progress_intro= Progressbar(self.videoFrame,orient=HORIZONTAL,length=100,mode='determinate')
        self.progress_intro.pack(fill=X)       
        self.progress_intro.start()

    def init_loading_download(self):
        self.progress_download= Progressbar(self.videoFrame,orient=HORIZONTAL,length=100,mode='determinate')
        self.progress_download.pack(fill=X)       
        self.progress_download.start()

    def download(self, url):
        #Callback function
        def use_svtplay():
            self.init_loading_download()
            self.check_submit_thread() 
            svtplaywrapper.download_video(url)
        
        self.intro_btn.configure(state=DISABLED)
        self.clear_btn.configure(state=DISABLED)
        self.intro_btn.grid(row= 0, column=3)
        global submit_thread
        submit_thread = threading.Thread(target=use_svtplay)
        submit_thread.start()

    # will check if this thread is done, (for future impl of loadingbar)
    def check_load_intro_thread(self):
        if load_intro_thread.is_alive():
            self.root.after(20, self.check_load_intro_thread)
        else:
            self.intro_fetched_completed = True
            self.progress_intro.pack_forget()
            self.lbl = Label(self.videoFrame, text="Intro fetching completed")
            self.lbl.pack()
            self.check_if_both_is_completed()
            print("done loading intro") # set flag for loading intro to true

    def check_if_both_is_completed(self):
        if self.intro_fetched_completed and self.download_completed:
            self.intro_btn.configure(state=NORMAL)
            self.clear_btn.configure(state=NORMAL)
            self.clear_box()
            self.clear_video_frame()
            self.set_new_video()
            self.init_slider()
            self.display(self.start)

    # will check if this thread is done, (for future impl of loadingbar)
    def check_submit_thread(self):
        if submit_thread.is_alive():
            self.root.after(20, self.check_submit_thread)
        else:
            self.download_completed = True
            self.progress_download.pack_forget()
            self.lbl = Label(self.videoFrame, text="Downloading of video has been completed")
            self.lbl.pack()
            self.check_if_both_is_completed()
            print("done loading video")
            #progressbar.stop()

    # Will only display first frame of the video atm
    def display(self, seconds):
        ret, frame = self.vid.get_frame(seconds)
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
            if ret:
            # Return a boolean success flag and the current frame converted to BGR
                frame = imutils.resize(frame, width=WIDTH_VIDEO, height=HEIGHT_VIDEO)
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
App(root, "Svtplay Intro Detector")
root.mainloop()
