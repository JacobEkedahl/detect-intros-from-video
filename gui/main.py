import datetime
import threading
import time
from tkinter import *
from tkinter.ttk import *

import cv2
import PIL.Image
import PIL.ImageTk

import extract_audio
import file_handler
import imutils
import pygame
import svtplaywrapper

START_TIME = 0
WIDTH_VIDEO = 480
HEIGHT_VIDEO = 253
MARGIN_TOP = 30
MARGIN_SLIDER_SIDE = 50
WIDTH_MARKER = 5 # only possible value atm
PREDICTION_MARKER_WIDTH = 1

#"gui/temp/al-pitcher-pa-paus.s01e01.avsnitt-1-converted.mp4"
class App:
    def __init__(self, root, window_title):
        #clear temp of old downloads, or missdownloads
        file_handler.init_temp()
       # file_handler.clear_temp()

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
        self.intro_btn = Button(self.buttonFrame, text="Load", command=self.load)
        self.intro_btn.grid(row= 0, column=3)

        # init frame for placing slider and video
        self.videoFrame = Frame(self.root)
        self.videoFrame.grid(row=1, column=0, padx=10, sticky=N+S+W+E)

        '''
        self.start = 10
        self.end = 44.5
        self.predicted_start = 9.5
        self.predicted_end = 44
        self.set_new_video()
        self.init_slider()
        self.display(self.start)
        self.init_play_bar()
        '''
        
    def load_audio(self):        
        extract_audio.extract()
        print("extracting")
        pygame.mixer.init()
        print("init pygame")
        pygame.mixer.music.load("gui/temp/current.ogg")

    def replace_text_in_box(self, text):
        self.txt.delete(0,END)
        self.txt.insert(0,text)

    def clear_box(self):
        self.txt.delete(0,END)
        
    def refresh_start(self):
        if self.play_start:
            curr_time = datetime.datetime.now()
            diff = curr_time - self.old_time
            addon = (diff.total_seconds() * 1000) / 1000
            new_start = self.old_start + addon
            self.global_change_start(new_start)
            self.root.update()
            self.root.after(1,self.refresh_start)

    def refresh_end(self):
        if self.play_end:
            curr_time = datetime.datetime.now()
            diff = curr_time - self.old_time
            addon = (diff.total_seconds() * 1000) / 1000
            new_end = self.old_end + addon
            self.global_change_end(new_end)
            self.root.update()
            self.root.after(1,self.refresh_end)

    def updatePlayBtns(self):
        self.play_stop_start["text"] = "Pause Start" if self.play_start else "Play Start"
        self.play_stop_end["text"] = "Pause End" if self.play_end else "Play End"

    def startPlayingVideo(self, type):
        def playStart():           
            self.old_time = datetime.datetime.now()
            self.old_start = self.start
            pygame.mixer.music.play(0, self.start)
            self.refresh_start()
        def playEnd():
            self.old_time = datetime.datetime.now()
            self.old_end = self.end
            pygame.mixer.music.play(0, self.end)
            self.refresh_end()

        global play_video_thread
        if type == "start" and self.play_start:
            print("start playing")
            play_video_thread = threading.Thread(target=playStart)
            play_video_thread.start()
        elif type == "end" and self.play_end:
            print("play end")
            play_video_thread = threading.Thread(target=playEnd)
            play_video_thread.start()

    def toggle_start(self):
        self.play_start = not self.play_start
        self.play_end = False if self.play_start else self.play_end
        if not self.play_start:
            pygame.mixer.music.stop()
        self.startPlayingVideo("start")
        self.updatePlayBtns()
        
    def toggle_end(self):
        self.play_end = not self.play_end
        self.play_start = False if self.play_end else self.play_start
        if not self.play_end:
            pygame.mixer.music.stop()
        self.startPlayingVideo("end")
        self.updatePlayBtns()

    def init_play_bar(self):
        self.play_start = False
        self.play_end = False
        self.sendPlayFrame = Frame(self.videoFrame)
        self.sendPlayFrame.pack()
        self.play_stop_start = Button(self.sendPlayFrame, command=self.toggle_start)
        self.play_stop_start.grid(row= 0, column=2, padx=5, pady=5)
        self.play_stop_end = Button(self.sendPlayFrame, command=self.toggle_end)
        self.play_stop_end.grid(row= 0, column=3, padx=5, pady=5)
        self.send_intro = Button(self.sendPlayFrame, text="Save", command=self.confirm_into)
        self.send_intro.grid(row= 0, column=4, pady=5)
        self.updatePlayBtns()

    def confirm_into(self):
        # start a new thread, load, then remove loading
        print("sent!")
    
    def init_slider(self):
        self.w = Canvas(self.videoFrame, width=WIDTH_VIDEO + MARGIN_SLIDER_SIDE * 2, height=55)
        self.move_start = False
        self.move_end = False
        self.w.bind("<ButtonRelease-1>", self.leave)
        self.w.bind("<Button-1>", self.down)
        self.w.bind ("<Leave>", self.leave)
        self.w.bind ("<Motion>", self.motion)
        self.w.pack()
        self.w.create_rectangle(MARGIN_SLIDER_SIDE, MARGIN_TOP, WIDTH_VIDEO + MARGIN_SLIDER_SIDE, MARGIN_TOP, fill="black")

        self.add_start_marker()
        self.add_end_marker()
        self.start_marker_pred = self.w.create_rectangle(MARGIN_SLIDER_SIDE + self.predicted_start, MARGIN_TOP - 10, self.predicted_start + 51, MARGIN_TOP + 10, fill="blue")
        self.end_marker_pred = self.w.create_rectangle(self.predicted_end + 50, MARGIN_TOP - 10, self.predicted_end + PREDICTION_MARKER_WIDTH + MARGIN_SLIDER_SIDE, MARGIN_TOP + 10, fill="blue")
        self.start_lbl_pred = self.w.create_text(self.predicted_start + MARGIN_SLIDER_SIDE,10,fill="blue",font="Times 8",
                    text=self.predicted_start)
        self.end_lbl_pred = self.w.create_text(self.predicted_end + MARGIN_SLIDER_SIDE,10,fill="blue",font="Times 8",
            text=self.predicted_end)

    def add_end_marker(self):
        self.end_marker = self.w.create_rectangle(self.end + MARGIN_SLIDER_SIDE, MARGIN_TOP - 10, self.end + MARGIN_SLIDER_SIDE + 5, MARGIN_TOP + 10, fill="red")
        self.focus_end_entry()

    def focus_end_entry(self):
        self.end_entry = Entry(self.w, width= 4, textvariable=self.end)
        self.end_entry.delete(0,END)
        self.end_entry.insert(0,self.end)
        self.end_entry.bind('<Return>', self.change_end)
        self.end_lbl = self.w.create_window(self.end + MARGIN_SLIDER_SIDE + 25,MARGIN_TOP,window=self.end_entry)

    def global_change_end(self, new_end):
        if new_end >= 5 and new_end <= 480:
            if new_end - 5 < self.start:
                self.start = new_end - 5
                self.draw_start()
            self.end = new_end
            self.draw_end()
            self.display(self.end)

    def change_end(self, event):
        new_end = float(self.end_entry.get())
        self.global_change_end(new_end)

    def global_change_start(self, new_start):
        if new_start >= 0 and new_start <= 475:
            if new_start + 5 > self.end:
                self.end = new_start + 5
                self.draw_end()
            self.start = new_start
            self.draw_start()
            self.display(self.start)

    def change_start(self, event):
        new_start = float(self.start_entry.get())
        self.global_change_start(new_start)

    def focus_start_entry(self):
        self.start_entry = Entry(self.w, width= 4, textvariable=self.start)
        self.start_entry.delete(0,END)
        self.start_entry.insert(0,self.start)
        self.start_entry.bind('<Return>', self.change_start)
        self.start_lbl = self.w.create_window(self.start + MARGIN_SLIDER_SIDE - 20,MARGIN_TOP,window=self.start_entry)

    def add_start_marker(self):
        self.start_marker = self.w.create_rectangle(self.start + MARGIN_SLIDER_SIDE, MARGIN_TOP - 10, self.start + MARGIN_SLIDER_SIDE + 5, MARGIN_TOP + 10, fill="green")
        self.focus_start_entry()

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
        if x >= self.start + MARGIN_SLIDER_SIDE and x <= self.start + MARGIN_SLIDER_SIDE + 5:
            self.move_start = True
        elif x >= self.end + MARGIN_SLIDER_SIDE and x <= self.end + MARGIN_SLIDER_SIDE + 5:
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
        if x >= self.start + MARGIN_SLIDER_SIDE and x <= self.start + MARGIN_SLIDER_SIDE + 5 or self.move_start:
            self.root.config(cursor='hand2')
        elif x >= self.end + MARGIN_SLIDER_SIDE and x <= self.end + MARGIN_SLIDER_SIDE + 5 or self.move_end:
            self.root.config(cursor='hand2')
        else:
            self.root.config(cursor='')

        x -= MARGIN_SLIDER_SIDE
        if self.move_start:
            if x <= 480 and x > 0:
                if x - 2 > self.end:
                    return 
                self.start = x - 2
                if self.start < 0:
                    self.start = 0
                elif self.start > 480:
                    self.start = 480
                elif self.start + 5 > self.end:
                    self.start = self.end - 5
                self.draw_start()
                self.display(self.start)
        elif self.move_end:
            if x <= 490 and x > 0:
                if self.start + 5 > x - 2:
                    return
                self.end = x - 2
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
        if not url.startswith("http") or "svtplay" not in url:
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

    def extract(self):
        def use_extraction():
            print("starting extraction")
            self.check_extraction_thread()
            self.load_audio()

        global extraction_thread
        extraction_thread = threading.Thread(target=use_extraction)
        extraction_thread.start()

    def check_extraction_thread(self):
        if extraction_thread.is_alive():
            self.root.after(20, self.check_extraction_thread)
        else:
            self.download_completed = True
            self.progress_download.pack_forget()
            self.lbl = Label(self.videoFrame, text="Downloading of video has been completed")
            self.lbl.pack()
            self.check_if_both_is_completed()
            print("done extraction audio") # set flag for loading intro to true

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
            self.init_play_bar()
            self.display(self.start)

    # will check if this thread is done, (for future impl of loadingbar)
    def check_submit_thread(self):
        if submit_thread.is_alive():
            self.root.after(20, self.check_submit_thread)
        else:
            self.extract()
            print("done loading video")
            #progressbar.stop()

    # Will only display first frame of the video atm
    def display(self, seconds):
        ret, frame = self.vid.get_frame(seconds)
        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.canvas.delete("all")
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
