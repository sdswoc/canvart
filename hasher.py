#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 19 22:32:10 2023

@author: shree
"""

import PIL
import numpy as np
import os
import cv2
from scipy.spatial import KDTree

def center_crop(image, resize_dim):

    height, width, _ = image.shape
    if height>width:
        image = image[round(height/2 - width/2): round(height/2 + width/2), :]
    else:
        image = image[:, round(width/2 - height/2): round(width/2 + height/2)]

    image  = cv2.resize(image, dsize=(resize_dim, resize_dim), interpolation=cv2.INTER_CUBIC)
    return image

def create_imarray(tile_size, directory):

    # load all jpg images in an array of bgr
    im_list = filter(lambda x: x.lower().endswith('.jpg') or x.lower().endswith('.jpeg'), os.listdir(directory))
    im_list = map(lambda x: center_crop(np.array(PIL.Image.open(f'{directory}/{x}')), tile_size), im_list)
    im_list = np.array(list(im_list))[:,:,:,::-1]

    return im_list

def create_hashbin(bgr_avg):

    tree = KDTree(bgr_avg)
    queries = np.stack(np.meshgrid(np.arange(256), np.arange(256), np.arange(256)), -1).reshape(-1, 3)
    print('hashing begun')

    # p=2 means euclidian distance, 1 would be manhattan. can be toyed around with
    indices = tree.query(queries, p=2)[1]

    print('hashing done')

    # this is a hashbin that contains the index of the image (in im_list)
    # that should be referred for each point in bgr space, hence number of input images
    # must be limited due to 16 bits (keep in mind later)

    return indices.reshape((256, 256, 256))

def main(im_list):
    # get average rgb values of each image
    bgr_avg = im_list.mean(axis=1).mean(axis=1)
    
    hashbin = create_hashbin(bgr_avg)
    
    return bgr_avg, hashbin