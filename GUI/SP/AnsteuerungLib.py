#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Projektarbeit Autozapfer 
Ansteuerung.py
Daniel Lechner, Matias Moos, Sam Müller
'''
import BV.Bier_Video_einlesen_V01 as AC
import Jetson.GPIO as GPIO
import time
import sys
sys.path.append('../')

from UserManagement.UserLib import inc_promille




#Pin Assignment
ZAPFHAHN1 = 29
ZAPFHAHN2 = 31
MAGNETVENTIL1 = 40
MAGNETVENTIL2 = 37
AUSFAHREN_MOTOR1 = 31
EINFAHREN_MOTOR1 = 33
AUSFAHREN_MOTOR2 = 35
EINFAHREN_MOTOR2 = 37
LED1 = 11
LED2 = 13

def init_GPIO():  
    #Set Pin Mode
    GPIO.cleanup()
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(ZAPFHAHN1, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(ZAPFHAHN2, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(MAGNETVENTIL1, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(MAGNETVENTIL2, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(AUSFAHREN_MOTOR1, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(EINFAHREN_MOTOR1, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(AUSFAHREN_MOTOR2, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(EINFAHREN_MOTOR2, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(LED1, GPIO.OUT, initial=GPIO.LOW)   
    GPIO.setup(LED2, GPIO.OUT, initial=GPIO.LOW)
    GPIO.output([LED1, LED2], GPIO.LOW)
    print("GPIO Init")


#Function Declarations
    
def SetHigh_Zapfhahn1(event):
    time.sleep(0.01)
    GPIO.output(ZAPFHAHN1, GPIO.HIGH)
    print("Zapfhahn1 HIGH")

def SetLow_Zapfhahn1(event):
    time.sleep(0.01)
    GPIO.output(ZAPFHAHN1, GPIO.LOW)
    print("Zapfhahn1 LOW")
    
def SetHigh_Zapfhahn2(event):
    time.sleep(0.01)
    GPIO.output(ZAPFHAHN2, GPIO.HIGH)
    print("Zapfhahn2 HIGH")

def SetLow_Zapfhahn2(event):
    time.sleep(0.01)
    GPIO.output(ZAPFHAHN2, GPIO.LOW)
    print("Zapfhahn2 LOW")
    
def SetHigh_Ausfahren_Motor1(event):
    GPIO.output(AUSFAHREN_MOTOR1, GPIO.HIGH)
    print("Motor 1 Ausfahren HIGH")

def SetLow_Ausfahren_Motor1(event):
    GPIO.output(AUSFAHREN_MOTOR1, GPIO.LOW)
    print("Motor 1 Ausfahren LOW")
    
def SetHigh_Ausfahren_Motor2(event):
    GPIO.output(AUSFAHREN_MOTOR2, GPIO.HIGH)
    print("Motor2 Ausfahren HIGH")

def SetLow_Ausfahren_Motor2(event):
    GPIO.output(AUSFAHREN_MOTOR2, GPIO.LOW)
    print("Motor 2 Ausfahren Low")

def SetHigh_Einfahren_Motor1(event):
    GPIO.output(EINFAHREN_MOTOR1, GPIO.HIGH)
    print("Motor 1 Einfahren High")

def SetLow_Einfahren_Motor1(event):
    GPIO.output(EINFAHREN_MOTOR1, GPIO.LOW)
    print("Motor 1 Einfahren Low")
    
def SetHigh_Einfahren_Motor2(event):
    GPIO.output(EINFAHREN_MOTOR2, GPIO.HIGH)
    print("Motor 2 Einfahren High")

def SetLow_Einfahren_Motor2(event):
    GPIO.output(EINFAHREN_MOTOR2, GPIO.LOW)
    print("Motor 2 Einfahren Low")
    
def SetHigh_MagnetVentil1(event):
    #P1 wird geöffnet
    GPIO.output(MAGNETVENTIL1, GPIO.HIGH)

def SetLow_MagnetVentil1(event):
    #P2 wird geöffnet
    GPIO.output(MAGNETVENTIL1, GPIO.LOW)
    
def SetHigh_MagnetVentil2(event):
    #P1 wird geöffnet
    GPIO.output(MAGNETVENTIL2, GPIO.HIGH)

def SetLow_MagnetVentil2(event):
    #P2 wird geöffnet
    GPIO.output(MAGNETVENTIL2, GPIO.LOW)

def SetHigh_LED1(event):
    time.sleep(0.01)
    GPIO.output(LED1, GPIO.HIGH)
    print("LED1 HIGH")

def SetLow_LED1(event):
    time.sleep(0.01)
    GPIO.output(LED1, GPIO.LOW)
    print("LED1 LOW")
    
def SetHigh_LED2(event):
    time.sleep(0.01)
    GPIO.output(LED2, GPIO.HIGH)
    print("LED2 HIGH")

def SetLow_LED2(event):
    time.sleep(0.01)
    GPIO.output(LED2, GPIO.LOW)
    print("LED2 LOW")

def SetHigh_ALL(event):
    time.sleep(0.01)
    GPIO.output([LED1, LED2], GPIO.HIGH)
    print("ALL HIGH")

def SetLow_ALL(event):
    time.sleep(0.01)
    GPIO.output([LED1, LED2], GPIO.LOW)
    print("ALL LOW")
    
    
    
def autobier1(root, tilted_val, lbl_user, lbl_score, Offbt, bt_logoff, lbl, cam_frame, modebg, button_links,button_rechts,manualbt,label_feedback,statebt=None):
    print("Automatikmodus Bier1")
    if tilted_val <= 45:
        tilted_val = 45
    print("Tilted_val1: " + str(tilted_val))
    #def vars
    state_tilted = 0   #state=0: Einschenkvorgang tilted ok; state=1: Einschenkvorgang tilted abgebrochen
    state_gerade = 0
    print("Automatikmodus gestartet")
    #Sperren des Ausschaltens
    Offbt.config(state="disabled")
    bt_logoff.config(state="disabled")
    root.update()
    #Glas kippen -> Motor vollständig ausfahren
    SetLow_Ausfahren_Motor1(1)
    time.sleep(10)
    #Ausfahren beenden
    SetHigh_Ausfahren_Motor1(1)
    # LED1 an 
    SetHigh_LED1(1)
    #Zapfhahn auf
    SetLow_Zapfhahn1(1)   
    #Starte Videoverarbeitung
    state_tilted=AC.video_tilted("links", Offbt, bt_logoff, lbl, cam_frame, modebg, button_links, button_rechts, statebt, manualbt, label_feedback, SetLow_Einfahren_Motor1, SetHigh_Einfahren_Motor2, SetHigh_Zapfhahn1, tilted_val)
    if state_tilted==0:
        #SetLow_Einfahren_Motor1(1)
        # Puffer für Unterscheidung der Max-Werte von tilted und gerade
        time.sleep(2.4)
        state_gerade=AC.video_gerade("links", Offbt, bt_logoff, lbl, cam_frame, modebg, button_links, button_rechts, statebt, manualbt, label_feedback, SetLow_Einfahren_Motor1, SetHigh_Einfahren_Motor2, SetHigh_Zapfhahn1)
        if state_gerade == 0:
            SetHigh_Zapfhahn1(1)
            inc_promille(lbl_user, lbl_score)
    SetHigh_Einfahren_Motor1(1)
    SetLow_LED1(1)
    #Aufheben der Sperrung des Ausschaltens
    Offbt.config(state="normal")
    bt_logoff.config(state="normal")
    return


def autobier2(root, tilted_val, lbl_user, lbl_score, Offbt, bt_logoff, lbl, cam_frame, modebg, button_links,button_rechts,manualbt,label_feedback,statebt=None):
    print("Automatikmodus Bier2")
    if tilted_val <= 0:
        tilted_val = 45
    print("Tilted_val2: " + str(tilted_val))
    #def vars
    state_tilted = 0   #state=0: Einschenkvorgang tilted ok; state=1: Einschenkvorgang tilted abgebrochen
    state_gerade = 0
    print("Automatikmodus gestartet")
    #Sperren des Ausschaltens
    Offbt.config(state="disabled")
    bt_logoff.config(state="disabled")
    root.update()
    #Glas kippen -> Motor vollständig ausfahren
    SetLow_Ausfahren_Motor2(1)
    time.sleep(10)
    #Ausfahren beenden
    SetHigh_Ausfahren_Motor2(1)
    #Zapfhahn auf
    # LED2 an 
    SetHigh_LED2(1)
    SetLow_Zapfhahn2(1)   
    #Starte Videoverarbeitung
    state_tilted=AC.video_tilted("rechts", Offbt, bt_logoff, lbl, cam_frame, modebg, button_links, button_rechts, statebt, manualbt, label_feedback, SetLow_Einfahren_Motor2, SetHigh_Einfahren_Motor2, SetHigh_Zapfhahn2, tilted_val)
    if state_tilted==0:
        SetLow_Einfahren_Motor2(1)
        # Puffer für Unterscheidung der Max-Werte von tilted und gerade
        time.sleep(2)
        state_gerade=AC.video_gerade("rechts", Offbt, bt_logoff, lbl, cam_frame, modebg, button_links, button_rechts, statebt, manualbt, label_feedback, SetLow_Einfahren_Motor2, SetHigh_Einfahren_Motor2, SetHigh_Zapfhahn2)
        if state_gerade == 0:
            SetHigh_Zapfhahn2(1)
            inc_promille(lbl_user, lbl_score)
    SetHigh_Einfahren_Motor2(1)
    SetLow_LED2(1)
    # Aufhaben der Sperrung zum Ausschalten
    Offbt.config(state="normal")
    bt_logoff.config(state="normal")
    return
    
