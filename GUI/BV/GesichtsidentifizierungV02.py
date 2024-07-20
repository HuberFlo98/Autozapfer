#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 31 15:28:27 2023

@author: autozapfer
"""
import cv2
import face_recognition
import os
import numpy as np
import math
from PIL import Image, ImageTk
import sqlite3
import time
from tkinter import ttk



# Helper
def face_confidence(face_distance, face_match_threshold=0.6):
    range = (1.0 - face_match_threshold)
    linear_val = (1.0 - face_distance) / (range * 2.0)

    if face_distance > face_match_threshold:
        return str(round(linear_val * 100, 2)) + '%'
    else:
        value = (linear_val + ((1.0 - linear_val) * math.pow((linear_val - 0.5) * 2, 0.2))) * 100
        return str(round(value, 2)) + '%'


class FaceRecognition:
    face_locations = []
    face_encodings = []
    face_names = []
    known_face_encodings = []
    known_face_names = []
    process_current_frame = True
    face_recognised = False
    image_taken = False
    cancel = False
    facecam_index = 0

    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        if not os.listdir("BV/known_faces")==[]:
            self.encode_faces()

    def encode_faces(self):
        for image in os.listdir("BV/known_faces"):
            face_image = face_recognition.load_image_file(f"BV/known_faces/{image}")
            face_encoding = face_recognition.face_encodings(face_image)[0]

            self.known_face_encodings.append(face_encoding)
            self.known_face_names.append(image)
        print(self.known_face_names)
        
    def add_faces(self, new_face_name):
        if os.path.exists('BV/known_faces/' + new_face_name):           
            face_image = face_recognition.load_image_file('BV/known_faces/' + new_face_name)
            face_encoding = face_recognition.face_encodings(face_image)[0]
            self.known_face_encodings.append(face_encoding)
            self.known_face_names.append(new_face_name)                   
        else:
            print("Bild-Datei existiert nicht!")
        #remove from lists
    def remove_faces(self, old_face_name):
        try:
            index = self.known_face_names.index(old_face_name)
            self.known_face_encodings.pop(index)
            self.known_face_names.pop(index)
        except:
            print("Bild konnte nicht aus Listen gelöscht werden!")
        #cancel faceid or face registration
    def cancel_faceid(self):
        self.cancel = True
        #set that picture was taken
    def picture_taken(self):
        self.image_taken = True

    def run_recognition(self, lbl, facereg_frame, modebg, username_entry, password_entry, button_faceid, bt_logoff, button_login, button_guestlogin, button_delete, button_register, label_feedback):
        style = ttk.Style()
        style.configure("Menu.TButton", font=("Calibri",12), anchor="center")
        if self.known_face_encodings==[]:
            label_feedback.place(x=50, y=250, height=30)
            label_feedback.config(text="No User registrated")
            return
        button_break = ttk.Button(facereg_frame, text="Cancel", style="Menu.TButton",command=self.cancel_faceid)
        button_break.place(x=196, y=380, height=70, width=120)
        #disalbe buttons while faceid is running
        button_faceid.config(state='disabled')
        button_login.config(state='disabled')
        button_guestlogin.config(state='disabled')
        bt_logoff.config(state='disabled')
        button_delete.config(state='disabled')
        button_register.config(state='disabled')
        #place labele for showing video
        lbl.place(x=0,y=0)
        video_capture = cv2.VideoCapture(self.facecam_index)

#        if not video_capture.isOpened(): Crashes Application --> other solution is preferred
#            sys.exit('Video source not found...')

        while self.face_recognised == False:
            ret, frame = video_capture.read()
            if not ret:
                print("Video Source not found")
                self.cancel_faceid()
                label_feedback.place(x=50, y=250, height=30)
                label_feedback.config(text="No camera found!")
                modebg.update()
                break

            # Only process every other frame of video to save time
            if self.process_current_frame:
                # Resize frame of video to 1/4 size for faster face recognition processing
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

                # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
                #rgb_small_frame = small_frame[:, :, ::-1]
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

                # Find all the faces and face encodings in the current frame of video
                self.face_locations = face_recognition.face_locations(rgb_small_frame)
                self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)

                self.face_names = []
                for face_encoding in self.face_encodings:
                    # See if the face is a match for the known face(s)
                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                    name = "Unknown"
                    confidence = '???'

                    # Calculate the shortest distance to face
                    face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)

                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = self.known_face_names[best_match_index]
                        confidence = face_confidence(face_distances[best_match_index])

                    self.face_names.append(f'{name} ({confidence})')

            self.process_current_frame = not self.process_current_frame

            # Display the results
            for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Create the frame with the name
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)
                if confidence != '???':
                    if(name != "Unknown" and (float(confidence.replace("%","")) > 90.0)):
                        self.face_recognised = True
                        corrected_name = name.replace(".jpg","")
                        corrected_name = corrected_name.replace(confidence,"")
                        corrected_name = corrected_name.replace("()","")
                        corrected_name = corrected_name.replace(" ","")
                        conn = sqlite3.connect('user.db')
                        c=conn.cursor()
                        c.execute("SELECT password FROM users WHERE username=?", (corrected_name,))
                        password = c.fetchone()
                        if password is not None:
                            username_entry.insert(0,corrected_name)
                            password_entry.insert(0,password)
                            modebg.update()
                            facereg_frame.update()
                            self.face_recognised = True
                            break
                        else:
                            print("Couldnt find user in user.db")
                        conn.commit()
                        conn.close()
            #Display the video in tkinter
            dimensions = frame.shape
            scale_factor = dimensions[1] / facereg_frame.winfo_width()
            new_width = int(dimensions[1] / scale_factor)
            new_height = int(dimensions[0] / scale_factor)
            resized_frame = cv2.resize(frame,(new_width,new_height)) #adapt image size to frame size of gui
            resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(resized_frame)
            tkinter_image = ImageTk.PhotoImage(pil_image)
            lbl.config(image=tkinter_image)
            lbl.image = tkinter_image
            facereg_frame.update()
            # Cancel Button
            if self.cancel == True:
                break

        # Release handle to the webcam
        bt_logoff.config(state='normal')
        button_login.config(state='normal')
        button_guestlogin.config(state='normal')
        button_delete.config(state='normal')
        button_register.config(state='normal')
        if self.cancel == True:
            button_faceid.config(state="normal")
        self.face_recognised = False
        self.process_current_frame = True
        self.face_encodings = []
        self.face_locations = []
        self.face_names = []
        self.cancel = False
        time.sleep(2)
        lbl.place_forget()  #dont show label anymore
        button_break.place_forget()
        video_capture.release()
        cv2.destroyAllWindows()

    def take_picture(self, lbl, picture_frame, modebg, button_picture, button_register, button_userlogin, entry_username, entry_password, entry_weight, label_feedback):
        #check if username is not empty
        #read username
        username=entry_username.get()
        password=entry_password.get()
        weight=entry_weight.get()
        if username == "":
            label_feedback.place(x=50, y=290, height=30)
            label_feedback.config(text="First Input a name before taking the picture!")
            return
        if password == "":
            label_feedback.place(x=50, y=290, height=30)
            label_feedback.config(text="First Input a password before taking the picture")
            return
        try:
            if not weight.isdigit():    #if weight is not a interger, return, except for if the iniput is that scary, that isdigit breaks
                label_feedback.place(x=50, y=290, height=30)
                label_feedback.config(text="For weight only a integer value is valid!")
                return
        except:
            label_feedback.place(x=50, y=290, height=30)
            label_feedback.config(text="For weight only a integer value is valid!")
            return
        if int(weight) <= 0:
            label_feedback.place(x=50, y=290, height=30)
            label_feedback.config(text="Only weights greater than 0 are allowed!")
        #check if user already exists
        conn = sqlite3.connect('user.db')
        c=conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        if c.fetchone():
              label_feedback.place(x=50, y=290, height=30)
              label_feedback.config(text="User already exists")
              conn.commit()
              conn.close()
              return
        else:
              conn.commit()
              conn.close()

        #create buttons for canceling and takitn picture
        button_break = ttk.Button(picture_frame, text="Cancel", style="Menu.TButton", command=self.cancel_faceid)
        button_break.place(x=126, y=380, height=70, width=120)
        button_takepicture = ttk.Button(picture_frame, text="Take Picture", style="Menu.TButton", command=self.picture_taken)
        button_takepicture.place(x=266, y=380, height=70, width=120)
        #disable buttons while video is running
        button_picture.config(state="disabled")
        button_register.config(state="disabled")
        button_userlogin.config(state="disabled")
      
        #place label for showing video
        lbl.place(x=0,y=0)
        #open video source
        camera = cv2.VideoCapture(self.facecam_index)
        #exit if video source was not found
#        if not camera.isOpened():
#            sys.exit('Video source not found...')

        while self.image_taken == False:
            ret, frame = camera.read()
            if not ret:
                print("Video Source not found")
                self.cancel_faceid()
                label_feedback.place(x=50, y=290, height=30)
                label_feedback.config(text="No camera found!")
                modebg.update()
                break
            #frame = frame[:, :, ::-1]
            # Display the resulting image
            dimensions = frame.shape
            scale_factor = dimensions[1] / picture_frame.winfo_width()
            new_width = int(dimensions[1] / scale_factor)
            new_height = int(dimensions[0] / scale_factor)
            resized_frame = cv2.resize(frame,(new_width,new_height)) #adapt image size to frame size of gui            
            resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(resized_frame)
            tkinter_image = ImageTk.PhotoImage(pil_image)
            lbl.config(image=tkinter_image)
            lbl.image = tkinter_image
            picture_frame.update()
            if self.cancel == True:
                break
        #take picture
        if self.cancel == False:
            ret, frame = camera.read()
            #check if picture was taken
            if not ret:
                print("error while taking picture")
            else:              
                #save picture as jpg
                cv2.imwrite("/home/autozapfer/Dokumente/Software/GUI/BV/known_faces/" + username + ".jpg", frame)
                #check if face gets recognised
                if os.path.exists('BV/known_faces/' + username + ".jpg"):
                    try:    #check if face is recognised on picture, otherwise take new one
                        face_image = face_recognition.load_image_file('BV/known_faces/' + username + ".jpg")
                        face_encoding = face_recognition.face_encodings(face_image)[0]
                    except:
                        #if user gets not recognised, delete picture, a new picture has to be taken
                        picture_path = '/home/autozapfer/Dokumente/Software/GUI/BV/known_faces/' + username + '.jpg'
                        os.remove(picture_path)
                        label_feedback.place(x=50, y=290, height=30)
                        label_feedback.config(text="No face was recognised in picture!, take a new picture")
                        self.image_taken = False
                #show taken picture
                dimensions = frame.shape
                scale_factor = dimensions[1] / picture_frame.winfo_width()
                new_width = int(dimensions[1] / scale_factor)
                new_height = int(dimensions[0] / scale_factor)
                resized_frame = cv2.resize(frame,(new_width,new_height)) #adapt image size to frame size of gui            
                resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(resized_frame)
                tkinter_image = ImageTk.PhotoImage(pil_image)
                lbl.config(image=tkinter_image)
                lbl.image = tkinter_image
                picture_frame.update()          
        # Release handle to the webcam
        #if no picture was taken, a registration must not be possible
        if self.image_taken == True:
            button_register.config(state="normal")
        button_userlogin.config(state="normal")
        self.image_taken = False
        self.cancel = False
        time.sleep(2)
        lbl.place_forget()  #dont show label anymore
        button_break.place_forget()
        button_takepicture.place_forget()
        camera.release()
        cv2.destroyAllWindows()        
        
if __name__ == '__main__':
    fr = FaceRecognition()
    fr.run_recognition()
