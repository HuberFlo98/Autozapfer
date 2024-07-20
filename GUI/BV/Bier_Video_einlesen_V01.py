#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import time
from PIL import Image, ImageTk
from tkinter import ttk
import cv2

#define constants
CAMERA_RECHTS = 3
CAMERA_LINKS = 1

#define variables
cancel_auto = True      #break auto mode

def cancel_automode():
    global cancel_auto
    cancel_auto = False
def reset_cancel():
    global cancel_auto
    cancel_auto = True

def linearmotor_einfahren():
    """Hier muss die Funktion der Aktorik übergeben werden"""
    print("Linearmotor fährt ein")
    
def zapfhahn_aus():
    """Hier muss die Funktion an die Aktorik übergeben werden"""
    print("Zapfhahn aus")
    print("Licht aus")

def compute_trimmed_mean(data, trim_percent):

    # Sortieren der Daten
    sorted_data = np.sort(data)

    # Anzahl der Datenpunkte, die entfernt werden sollen
    trim_size = int(len(sorted_data) * trim_percent)

    # Entfernen der Datenpunkte
    trimmed_data = sorted_data[trim_size:-trim_size]

    # Berechnen des Mittelwerts
    trimmed_mean = np.mean(trimmed_data)

    return trimmed_mean

prev_time=0

def fuellstandserkennung_tilted(image,cam_sel, lbl, cam_frame, modebg, button_links,button_rechts, statebt, manualbt, label_feedback, Einfahren_Motor , Stop_Motor,Zapfhahn_aus,tilted_val):
    print("Begin fuellstandserkennung_tilted")
    # Bildvorverarbeitung
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (13, 13), 0)
    edges = cv2.Canny(blurred, 50, 150)

    # Horizontale Linien erkennen
    lines = cv2.HoughLinesP(edges, rho=2, theta=np.pi/180, threshold=10, minLineLength=40, maxLineGap=10)
    horizontal_lines = []
    
    # Filtern der horizontalen Linien
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
            if np.abs(angle) < 20 or np.abs(angle - 180) < 20:
                #horizontal_lines.append(line)
                if 35 < y1 < 400 and 35 < y2 < 400:
                    horizontal_lines.append(line)

    # Zeichnen der horizontalen Linien
    for line in horizontal_lines:
        x1, y1, x2, y2 = line[0]
        cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 3)

    # Mittelwert der y-Koordinaten der Linien berechnen (68 bis 200)
    if len(horizontal_lines) > 0:
        
        y_coords_1 = [line[0][1] for line in horizontal_lines if 20 <= line[0][1] <= 400]
        try:
            
            #trim_percent = 0  # 10% der Daten werden abgeschnitten
            mean_y_1 = int(np.mean(y_coords_1))
            
            # Zeichnen des roten Strichs basierend auf dem Mittelwert der y-Koordinaten (68 bis 200)
            cv2.line(image, (0, mean_y_1), (image.shape[1], mean_y_1), (0, 0, 255), 3)
            
            # Mittelwert ausgeben (68 bis 200)
           
            print("Mittelwert der y-Koordinaten tilted:", mean_y_1)
            
                        
            """Hier kann man den mean_y_1 Wert ändern, um den maximalen Wert beim schiefen einschenken zu bestimmen"""
            #Export braucht hier ca. 100
            if mean_y_1 < tilted_val:
                start = time.time()
            else:
                start = 0
            while mean_y_1 < tilted_val:
                if time.time() - start > 1:
                    ''' Zurück in Ansteuerung, um Motor einzufahren'''
                    print("Ende fuellstandserkennung_tilted")
                    Einfahren_Motor(1)
                    return 1
        except:
            mean_y_1 = 0

    #cv2.imshow("Kanten", edges)
    #cv2.imshow("Ergebnis", image)
    cv2.waitKey(10)
    return horizontal_lines

#def puffer(cam_sel, lbl, cam_frame, modebg, button_links,button_rechts, statebt, manualbt, label_feedback, Einfahren_Motor , Stop_Motor,Zapfhahn_aus):
#    time.sleep(2)
#    video_gerade(cam_sel, lbl, cam_frame, modebg, button_links,button_rechts, statebt, manualbt, label_feedback, Einfahren_Motor , Stop_Motor,Zapfhahn_aus)   
    
def fuellstandserkennung_gerade(image):
    
    # Bildvorverarbeitung
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (11, 11), 0)
    edges = cv2.Canny(blurred, 50, 150)

    # Horizontale Linien erkennen
    lines = cv2.HoughLinesP(edges, rho=2, theta=np.pi/180, threshold=10, minLineLength=70, maxLineGap=20)
    horizontal_lines = []
    
    # Filtern der horizontalen Linien
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
            if np.abs(angle) < 13 or np.abs(angle - 180) < 13:
                #horizontal_lines.append(line)
                if 68 < y1 < 400 and 68 < y2 < 400:
                    horizontal_lines.append(line)

    # Zeichnen der horizontalen Linien
    for line in horizontal_lines:
        x1, y1, x2, y2 = line[0]
        cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 3)
        
    # Mittelwert der y-Koordinaten der Linien berechnen (68 bis 200)
    if len(horizontal_lines) > 0:
        
        y_coords_1 = [line[0][1] for line in horizontal_lines if 68 <= line[0][1] <= 130]
        try:
            
            #trim_percent = 0  # 10% der Daten werden abgeschnitten
            mean_y_1 = int(np.mean(y_coords_1))
            
            # Zeichnen des roten Strichs basierend auf dem Mittelwert der y-Koordinaten (68 bis 200)
            cv2.line(image, (0, mean_y_1), (image.shape[1], mean_y_1), (0, 0, 255), 3)
            
            # Mittelwert ausgeben (68 bis 200)
            
            print("Mittelwert der y-Koordinaten gerade:", mean_y_1)
            
            #Hier wird der maximale y-Wert für die Kante angegeben !Achtung! wenn dieser <80 wird, schäumt das Bier über
            #Bei Export brauchen wir ca. 90
            if mean_y_1 < 85: 
                    print("Stop tapping")
                    return 1
        except:
            mean_y_1 = 0

    # Mittelwert der y-Koordinaten der Linien berechnen (200 bis 500)
    if len(horizontal_lines) > 0:
        y_coords_2 = [line[0][1] for line in horizontal_lines if 200 <= line[0][1] <= 400]
        try:
            trim_percent = 0.1  # 10% der Daten werden abgeschnitten
            mean_y_2 = int(compute_trimmed_mean(y_coords_2, trim_percent))
            # Zeichnen des blauen Strichs basierend auf dem Mittelwert der y-Koordinaten (200 bis 500)
            cv2.line(image, (0, mean_y_2), (image.shape[1], mean_y_2), (255, 0, 0), 3)
            # Mittelwert ausgeben (200 bis 500)
            #print("Mittelwert der y-Koordinaten (200 bis 500):", mean_y_2)
        except:
            mean_y_2 = 0

    #cv2.imshow("Kanten", edges)
    #cv2.imshow("Ergebnis", image)
    cv2.waitKey(10)
    return horizontal_lines

def video_tilted(cam_sel,  Offbt, bt_logoff, lbl, cam_frame, modebg, button_links,button_rechts, statebt, manualbt, label_feedback, Einfahren_Motor, Stop_Motor ,Zapfhahn_aus, tilted_val):
    print("Begin video_tilted")
    #define vars
    video_source = None
    returnvalue = 0
    #define style for buttons
    style = ttk.Style()
    style.configure("Menu.TButton", font=("Calibri",12), anchor="center")
    #print info
    label_feedback.place(x=50, y=390, height=30)
    label_feedback.config(text="Automatic mode started!")
    modebg.update()
    #define Button for canceling auto mode
    button_break = ttk.Button(cam_frame, text="Cancel", style="Menu.TButton",command=cancel_automode)
    button_break.place(x=196, y=380, height=70, width=120)
    #disalbe buttons while faceid is running
    button_links.config(state="disabled")
    button_rechts.config(state='disabled')
    if statebt is not None:        
        statebt.config(state='disabled')
    manualbt.config(state='disabled')
    # Video abspielen
    if cam_sel == "rechts":
        video_source = CAMERA_RECHTS
    elif cam_sel=="links":
        video_source = CAMERA_LINKS
    #place labele for showing video
    lbl.place(x=0,y=0)
    cap = cv2.VideoCapture(video_source)
    #cap = cv2.VideoCapture('Einschenken_verdreht_bier_005.avi')

    while True:
        ret, frame = cap.read()
        if not ret:
            print("No Cam found.")
            label_feedback.place(x=50, y=390, height=30)
            label_feedback.config(text="No camera found...")
            modebg.update()
            time.sleep(1)
            cancel_automode()
        # Cancel Button
        if cancel_auto == False:
            print("Abbruch Automatikmodus, video_tilted_cancel_auto")
            returnvalue = 1
            Zapfhahn_aus(1)
            label_feedback.place(x=50, y=390, height=30)
            label_feedback.config(text="cancelling...")
            modebg.update()
            Einfahren_Motor(1)
            time.sleep(10)
            Stop_Motor(1)
            label_feedback.config(text="Tapping finished!")   
            break
        rotated_frame1 = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        if cam_sel == "rechts":
            #Hier wird ein durchsichtiges Polygon erstellt, welches verhindert, dass der Hintergrund komplett schwarz wird
            pts = np.array([[435,0],[0,340],[0,0]], dtype=np.int32)
            mask = np.zeros_like(rotated_frame1)
            cv2.fillPoly(mask, [pts], (255,255,255))
            rotated_frame = cv2.bitwise_and(rotated_frame1, mask)
        elif cam_sel =="links":
            #Hier wird ein durchsichtiges Polygon erstellt, welches verhindert, dass der Hintergrund komplett schwarz wird
            pts = np.array([[75,0],[500,380],[500,0]], dtype=np.int32)
            mask = np.zeros_like(rotated_frame1)
            cv2.fillPoly(mask, [pts], (255,255,255))
            rotated_frame = cv2.bitwise_and(rotated_frame1, mask)
            
        outputframe = rotated_frame
        
        #Display the video in tkinter
        dimensions = outputframe.shape
        scale_factor = dimensions[1] / cam_frame.winfo_width()
        new_width = int(dimensions[1] / scale_factor)
        new_height = int(dimensions[0] / scale_factor)
        resized_frame = cv2.resize(outputframe,(new_width,new_height)) #adapt image size to frame size of gui
        resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(resized_frame)
        tkinter_image = ImageTk.PhotoImage(pil_image)
        lbl.config(image=tkinter_image)
        lbl.image = tkinter_image
        cam_frame.update()
        
        # Funktion für die Kantenerkennung aufrufen
        val=fuellstandserkennung_tilted(rotated_frame,cam_sel, lbl, cam_frame, modebg, button_links,button_rechts, statebt, manualbt, label_feedback, Einfahren_Motor , Stop_Motor,Zapfhahn_aus, tilted_val)
        if val==1:
            break
         
    # Release handle to the webcam
    button_links.config(state='normal')
    button_rechts.config(state='normal')
    if statebt is not None:
       statebt.config(state='normal')
    manualbt.config(state='normal')
    reset_cancel()
    lbl.place_forget()  #dont show label anymore
    button_break.place_forget()
    cap.release()
    cv2.destroyAllWindows()
    print("Ende video_tilted")
    return returnvalue
    

#def video_gerade(cam_sel, lbl, cam_frame, modebg, button_links,button_rechts, statebt, manualbt, label_feedback, Einfahren_Motor , Stop_Motor,Zapfhahn_aus):
def video_gerade(cam_sel, Offbt, bt_logoff, lbl, cam_frame, modebg, button_links,button_rechts, statebt, manualbt, label_feedback, Einfahren_Motor , Stop_Motor,Zapfhahn_aus):
    print("Begin video gerade")
    #define vars
    video_source = None
    returnvalue = 0
    #define style for buttons
    style = ttk.Style()
    style.configure("Menu.TButton", font=("Calibri",12), anchor="center")
    #define Button for canceling auto mode
    button_break = ttk.Button(cam_frame, text="Cancel", style="Menu.TButton",command=cancel_automode)
    button_break.place(x=196, y=380, height=70, width=120)
    #disalbe buttons while faceid is running
    button_links.config(state="disabled")
    button_rechts.config(state='disabled')
    if statebt is not None:        
        statebt.config(state='disabled')
    manualbt.config(state='disabled')
    # Video abspielen
    if cam_sel == "rechts":
        video_source = CAMERA_RECHTS
    else:
        video_source = CAMERA_LINKS
    #place labele for showing video
    lbl.place(x=0,y=0)
    cap = cv2.VideoCapture(video_source)
    #cap = cv2.VideoCapture('Einschenken_verdreht_bier_004.avi')

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Kein Video oder Kamera gefunden.")
            break
    
        if cancel_auto == False:
            print("Abbruch Automtaikmodus")
            returnvalue = 1
            Zapfhahn_aus(1)
            label_feedback.place(x=50, y=390, height=30)
            label_feedback.config(text="cancelling...")
            modebg.update()
            Einfahren_Motor(1)
            time.sleep(10)
            Stop_Motor(1)
            label_feedback.config(text="Tapping finished!")                       
            break
        rotated_frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        outputframe = rotated_frame
        
        #Display the video in tkinter
        dimensions = outputframe.shape
        scale_factor = dimensions[1] / cam_frame.winfo_width()
        new_width = int(dimensions[1] / scale_factor)
        new_height = int(dimensions[0] / scale_factor)
        resized_frame = cv2.resize(outputframe,(new_width,new_height)) #adapt image size to frame size of gui
        resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(resized_frame)
        tkinter_image = ImageTk.PhotoImage(pil_image)
        lbl.config(image=tkinter_image)
        lbl.image = tkinter_image
        cam_frame.update()
        
        # Funktion für die Kantenerkennung aufrufen
        val=fuellstandserkennung_gerade(rotated_frame)
        #fuellstandserkennung_tilted(rotated_frame)
        if val==1:
            #zapfhahn_aus()
            Zapfhahn_aus(1)
            label_feedback.place(x=50, y=390, height=30)
            label_feedback.config(text="cancelling...")
            modebg.update() 
            Einfahren_Motor(1)
            time.sleep(5)
            Stop_Motor(1)
            label_feedback.config(text="Tapping finished!")
            modebg.update() 
            break
    # print info
    label_feedback.config(text = "Automatic mode finished!")
    # Release handle to the webcam
    button_links.config(state='normal')
    button_rechts.config(state='normal')
    if statebt is not None:
        statebt.config(state='normal')
    manualbt.config(state='normal')
    reset_cancel()
    time.sleep(2)
    lbl.place_forget()  #dont show label anymore
    button_break.place_forget()
    cap.release()
    cv2.destroyAllWindows()
    return returnvalue


#video_tilted()