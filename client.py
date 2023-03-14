#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 20 14:14:07 2023

@author: shree
"""

from socket import socket, AF_INET, SOCK_STREAM, gaierror
import cv2
import pickle
import struct
import os
import converter
import hasher
from joblib import dump, load

def save_data(hashbin, im_list, bgr_avg):
    dump(hashbin, 'hash.joblib')
    dump(im_list, 'imarray.joblib')
    dump(im_list, 'bgravg.joblib')

def load_data():
    return load('hash.joblib'), load('imarray.joblib'), load('bgravg.joblib')


def retrieve():
    global data, HEADER_SIZE
    # first we receive the header (size of the pickle file)
    while len(data) < HEADER_SIZE:
        # the smaller the size of datapacket, the longer it takes to receive
        packet = client.recv(2**10)
        if not packet:
            print('noooooo')
            break
        data += packet
    
    msg_size = struct.unpack("Q", data[:HEADER_SIZE])[0]
    data = data[HEADER_SIZE:]
    
    while len(data) < msg_size:
        data += client.recv(2**10)
        
    pickle_data = data[:msg_size]
    data  = data[msg_size:] # the remainder of data received is stored for the next loop 
    
    return pickle.loads(pickle_data)

def feed_generator(host_ip, port, glob_vars):
    global data, HEADER_SIZE, client
    while True:
        try:
############# SERVER STUFF ##################
            
            glob_vars["message"] = "Connecting..."
        
            client = socket(AF_INET, SOCK_STREAM)
            client.connect((host_ip, port)) 
            
            data = b""  # creates an empty data packet
            
            HEADER_SIZE = struct.calcsize("Q")
            
            glob_vars["message"] = "Connected!"
            
############# VIDEO STUFF #####################
            
        
            tile_size = 20
            
            if all(x in os.listdir() for x in ['hash.joblib', 'imarray.joblib', 'bgravg.joblib']):
                hashbin, im_list, bgr_avg = load_data()
            else:
                im_list = hasher.create_imarray(tile_size, 'subimages')
                bgr_avg, hashbin = hasher.main(im_list)
                save_data(hashbin, im_list, bgr_avg)
            
            image = retrieve()
            converter.init(image.shape[0], image.shape[1], im_list, bgr_avg, hashbin, w_size=1)
            
            yield b'--frame\r\n'
        
            while True:
                image = retrieve()
                converter.convert(image)
            
                frame = cv2.imencode('.bmp', converter.result_image)[1].tobytes()
                
                yield b'Content-Type: image/bmp\r\n\r\n' + frame + b'\r\n--frame\r\n'
        except gaierror:
            glob_vars["message"] = "Incorrect details"