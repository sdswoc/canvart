#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 11:14:54 2023

@author: shree
"""

import cv2
import hasher
import converter
import moviepy.editor as mpy
import os
import numpy as np
from joblib import dump, load
import sys
import shutil

def save_data(hashbin, imarray, bgr_avg):
    dump(hashbin, 'data/hash.joblib')
    dump(imarray, 'data/imarray.joblib')
    dump(imarray, 'data/bgravg.joblib')

def load_data():
    return load('data/hash.joblib'), load('data/imarray.joblib'), load('data/bgravg.joblib')

def create_video(path):
    global im_list, bgr_avg, hashbin, window_size, tile_size

    window_size = 20
    tile_size = 20

    vidcap = cv2.VideoCapture(path)   
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    audio = mpy.VideoFileClip(path).audio

    success = True
    i = 0
    success, image = vidcap.read()
    converter.init(image.shape[0]//window_size, image.shape[1]//window_size,
                   im_list, bgr_avg, hashbin, window_size)
    
    shutil.rmtree('temp/')
    os.makedirs('temp/')
    
    while success:
        converter.convert(image)
        cv2.imwrite(f'temp/{i}.png', converter.result_image)
        i += 1
        success, image = vidcap.read()

    clip = mpy.ImageSequenceClip([f'temp/{x}.png' for x in range(i)], fps=30)

    clip.audio = audio
    clip.write_videofile(f"{path[:-4]}_new.mp4", fps=fps)
    
def create_photos(paths):
    global im_list, bgr_avg, hashbin
    
    result = []
    photos = [cv2.imread(path) for path in paths]
    for photo in photos:
        converter.init(photo.shape[0]//window_size, photo.shape[1]//window_size,
                       im_list, bgr_avg, hashbin, window_size)
        converter.convert(photo)
        photos.append(converter.result_image.copy())
        
    return result

def feed_generator(glob_vars):
    global im_list, bgr_avg, hashbin, window_size, tile_size
    
    ################# SERVER STUFF #####################
    while True:
        try:
            glob_vars["connected"] = "True"
            
            ################# VIDEO STUFF #####################
            
            window_size = 10
            tile_size = 20
            
            if all(x in os.listdir('data') for x in ['hash.joblib', 'imarray.joblib', 'bgravg.joblib']):
                hashbin, im_list, bgr_avg = load_data()
            else:
                im_list = hasher.create_imarray(tile_size, 'subimages')
                bgr_avg, hashbin = hasher.main(im_list)
                save_data(hashbin, im_list, bgr_avg)
                
            video = cv2.VideoCapture(0)
            showing, image = video.read()
            
            converter.init(image.shape[0]//window_size, image.shape[1]//window_size,
                           im_list, bgr_avg, hashbin, window_size)
            
            yield b'--frame\r\n'
                    
            while True:
                
                image = video.read()[1]
                small_image = converter.convert(image)    
                
                send(small_image, client)
                
                frame = cv2.imencode('.bmp', converter.result_image)[1].tobytes()
                
                yield b'Content-Type: image/bmp\r\n\r\n' + frame + b'\r\n--frame\r\n'
        except ConnectionResetError:
            image = cv2.imread("/images/client disconnected.png")
                        
            frame = cv2.imencode('.bmp', image)[1].tobytes()
            yield b'Content-Type: image/bmp\r\n\r\n' + frame + b'\r\n--frame\r\n'