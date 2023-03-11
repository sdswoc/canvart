#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 20 12:57:44 2023

@author: shree
"""
import struct
import cv2
import pickle
import hasher
import converter
import os
from joblib import dump, load
from socket import socket, AF_INET, SOCK_STREAM
import psutil
import sys

def get_ips():
    ips = dict()
    for interface, snics in psutil.net_if_addrs().items():
        for snic in snics:
            if snic.family == AF_INET and interface:
                ips[interface] = snic.address
    return ips

def save_data(hashbin, imarray, bgr_avg):
    dump(hashbin, 'hash.joblib')
    dump(imarray, 'imarray.joblib')
    dump(imarray, 'bgravg.joblib')

def load_data():
    return load('hash.joblib'), load('imarray.joblib'), load('bgravg.joblib')

def send(array, client):
    pickle_data = pickle.dumps(array)
    
    # size of pickle is stored in a long long int (represented by Q)
    message = struct.pack("Q", len(pickle_data)) + pickle_data
    client.sendall(message)


def feed_generator(glob_vars):
    ################# SERVER STUFF #####################
    while True:
        try:
            ips = get_ips()
            
            server_socket = socket(AF_INET, SOCK_STREAM)
            
            for key in ips.keys():
                if key.startswith('wlp'):
                    glob_vars["host_ip"] = ips[key]
                    break
            else:
                glob_vars["host_ip"] = '127.1.1.1'
                
            server_socket.bind((glob_vars["host_ip"], 0))
        
            glob_vars["port"] = server_socket.getsockname()[1]
        
            server_socket.listen(4)
            
            print('Listening', file=sys.stderr)
            
            client, addr = server_socket.accept()
            print(f'Connected to: {addr}', file=sys.stderr)
            glob_vars["connected"] = "True"
            
            ################# VIDEO STUFF #####################
            
            window_size = 20
            tile_size = 20
            
            if all(x in os.listdir() for x in ['hash.joblib', 'imarray.joblib', 'bgravg.joblib']):
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