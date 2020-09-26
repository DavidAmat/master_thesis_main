import pandas as pd
import numpy as np
import os
import sys
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
import tqdm
import cv2
import keras

# ..............................................................................................
# ..............................................................................................

#                           Used Generator

# ..............................................................................................
# ..............................................................................................

from paths import *

class DataGenerator_subimgs(keras.utils.Sequence):
    def __init__(self, df, scaling, x_col, y_col=None, batch_size=10, num_classes=None, shuffle=True,
                num_subimgs = 10, labels = {}):
        self.batch_size = batch_size
        self.df = df.copy()
        self.labels = labels
        self.df["idx"] =  np.arange(0, self.df.shape[0])
        self.df.set_index("idx", inplace=True)
        self.scaling = scaling
        self.indices = self.df.index.tolist()
        self.num_classes = num_classes
        self.shuffle = shuffle
        self.x_col = x_col
        self.y_col = y_col
        self.dim = (int(x_col / scaling), int(y_col / scaling), 1) #one input channel
        self.on_epoch_end()
        self.num_subimgs = num_subimgs

    def __len__(self):
        return len(self.indices) // self.batch_size

    def __getitem__(self, index):
        idx = self.indices[index * self.batch_size:(index + 1) * self.batch_size]
        batch = [self.indices[k] for k in idx]
        
        X, y = self.__get_data(batch)
        return X, y

    def on_epoch_end(self):
        pass

    def __get_data(self, batch):
        
        # Number of subimgs:
        self.dim = (int(self.x_col / self.scaling), int(self.y_col / (self.scaling*self.num_subimgs)), 1) 
        
        # Prepare the output
        X = np.empty((self.batch_size * self.num_subimgs, *self.dim))
        y = np.empty((self.batch_size * self.num_subimgs, self.num_classes), dtype=int)
        
        # Get the list of image files and corresponding artists
        df_imgs_files = self.df.iloc[batch]
        
        list_imgs = list(df_imgs_files["tr"])
        list_art = list(df_imgs_files["art"])
        
        for ii in range(len(list_imgs)):
            
            # Read image using cv2
            path_img = os.path.join(PATH_DATA, list_imgs[ii])
            img = cv2.cvtColor(cv2.imread(path_img), cv2.COLOR_BGR2GRAY)
            img = np.round(img / 255.,5)
            img = cv2.resize(img, (self.y_col, self.x_col))
            #img = cv2.resize(img, (self.dim[1], self.dim[0]))
            
            # Crop the images into 10 chunks
            
            y_subimgs = int(np.floor(self.y_col / self.num_subimgs))
            positions_cut_img = np.arange(0, self.y_col, y_subimgs)
            for jj in range(len(positions_cut_img) - 1):
                subimg = img[:,positions_cut_img[jj]:positions_cut_img[jj+1]]
            
                # Expand dims
                subimg = np.expand_dims(subimg, axis = 2) # add the dimension of the channel 
            
                # Put it into X matrix
                X[ii*self.num_subimgs + jj,] = subimg
                y[ii*self.num_subimgs + jj] = self.labels[list_art[ii]]

        return X, y

    
    
# ..............................................................................................
# ..............................................................................................

#                           Old generator

# ..............................................................................................
# ..............................................................................................    
    
class DataGenerator(keras.utils.Sequence):
    def __init__(self, df, scaling, x_col, y_col=None, batch_size=10, num_classes=None, shuffle=True):
        self.batch_size = batch_size
        self.df = df
        self.indices = self.df.index.tolist()
        self.num_classes = num_classes
        self.shuffle = shuffle
        self.x_col = x_col
        self.y_col = y_col
        self.dim = (int(x_col / scaling), int(y_col / scaling), 1) #one input channel
        self.on_epoch_end()

    def __len__(self):
        return len(self.indices) // self.batch_size

    def __getitem__(self, index):
        idx = self.indices[index * self.batch_size:(index + 1) * self.batch_size]
        batch = [self.indices[k] for k in idx]
        
        X, y = self.__get_data(batch)
        return X, y

    def on_epoch_end(self):
        pass

    def __get_data(self, batch):
        X = np.empty((self.batch_size, *self.dim))
        y = np.empty((self.batch_size, self.num_classes), dtype=int)
        
        # Get the list of image files and corresponding artists
        df_imgs_files = self.df.iloc[batch]
        
        list_imgs = list(df_imgs_files["tr"])
        list_art = list(df_imgs_files["art"])
        
        for ii in range(len(list_imgs)):
            
            # Read image using cv2
            path_img = os.path.join(PATH_DATA, list_imgs[ii])
            img = cv2.cvtColor(cv2.imread(path_img), cv2.COLOR_BGR2GRAY)
            img = np.round(img / 255.,5)
            img = cv2.resize(img, (self.y_col, self.x_col))
            img = cv2.resize(img, (self.dim[1], self.dim[0]))
            img = np.expand_dims(img, axis = 2) # add the dimension of the channel 
            
            # Put it into X matrix
            X[ii,] = img
            y[ii] = labels[list_art[ii]]

        return X, y