#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 23:39:28 2023

@author: shree

"""
import numpy as np
import cv2
import PIL
from matplotlib import pyplot as plt
import hasher

# can be optimised by creating a global "temporary" variable so that memory doesn't
# have to be created and freed repeatedly
def shift_colour(image, dB, dG, dR):
    """
    Parameters
    ----------
    image : np.array
        numpy array representing image in bgr space
    dB : float
        change in blue value
    dG : float
        change in green value
    dR : float
        change in red value

    Returns
    -------
    image : np.array
        modified image shifted by given colour values

    """
    
    image = image.copy()
    image[:, :, 0] = np.clip(image[:, :, 0] + dB, 0, 255)
    image[:, :, 1] = np.clip(image[:, :, 1] + dG, 0, 255)
    image[:, :, 2] = np.clip(image[:, :, 2] + dR, 0, 255)
    return image

def window_down(image, window_size):
    """
    Parameters
    ----------
    image : np.array
        the image to be tiled

    window_size : int
        size of tile

    Returns
    -------
    numpy tensor representing the scaled image

    """
    if window_size == 1:
        return image
    # for some unknown reason, here opencv wants dimensions in reverse. WATCH OUT!
    return cv2.resize(image, dsize=(image.shape[1]//window_size,
                                    image.shape[0]//window_size),
                      interpolation=cv2.INTER_CUBIC)

def convert(image):
    
    # the array to contain `result_image` is constant globally so memory doesn't
    # have to be reallocated each loop
    
    image = window_down(image, window_size)
    
    for i in range(height):
        for j in range(width):
            b, g, r = image[i, j]
            # dB, dG, dR = image[i, j] - bgr_avg[hashbin[g, b, r]]
            result_image[i*tile_size: (i+1)*tile_size, j*tile_size: (j+1)*tile_size] = im_list[hashbin[g, b, r]] 
            # result_image[i*tile_size: (i+1)*tile_size, j*tile_size: (j+1)*tile_size] = shift_colour(im_list[hashbin[g, b, r]], dB, dG, dR) 
            # okay idk why but due to some very weird bug i have to look at index gbr, not bgr
    
    return image

def init(h, w, i_list, avg, h_bin, w_size):
    global height, width, im_list, bgr_avg, hashbin, result_image, window_size, tile_size
    
    height, width, im_list, bgr_avg, hashbin, window_size = h, w, i_list, avg, h_bin, w_size
    tile_size = im_list.shape[1]
    
    # we create an empty rgb image to be filled using the hashbin we've created
    result_image = np.zeros((height*tile_size, width*tile_size, 3), np.uint8)