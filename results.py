import os
import json
import sys
import re
import pandas as pd
import math

experiment_name = 'tuning-ctrl'
input_location = 'resources/evaluated/'

df = pd.DataFrame()

for root, subdirs, files in os.walk(f'{input_location}{experiment_name}'):
    if subdirs == [] or ['.ipynb_checkpoints'] == subdirs:        


        for file in files:
            
            input = f'{root}/{file}'            
                   
            _, file_extension = os.path.splitext(file)

            print(file_extension)
            
            if file_extension == '.json':

                fileinfo = str.split(file,'_')
                

                offset = 1           
                    

                path = input
                experiment = fileinfo[0]
                if offset == 1:
                    experiment = f'{experiment}-{fileinfo[1]}'
                fps_original = re.sub('\D', '', fileinfo[1+offset])
                fps_video = fileinfo[2+offset]
                resolution = fileinfo[3+offset]
                if '@' in file:
                    method = fileinfo[4+offset].split('@')[0]
                    magnification_factor = fileinfo[4+offset].split('@')[1].split('.')[0]
                else:
                    method = 'none'
                    magnification_factor = 'none'
            
                with open(input, "r") as filedata:
                    for line in filedata:
                        data = json.loads(line)

                ux = data['upperx']
                lx = data['lowerx']

                uy = data['uppery']
                ly = data['lowery']

                ffthx = data['freqsx'][0]
                ffthy = data['freqsy'][0]

                new = pd.DataFrame([{
                    'path':input,
                    'experiment':experiment,
                    'fps_original':fps_original,
                    'fps_video':fps_video,
                    'resolution':resolution,
                    'method':method,
                    'magnification factor': magnification_factor,
                    'dup': round(ux,2),
                    'dlx': round(lx,2),
                    'duy': round(uy,2),
                    'dlx': round(ly,2),
                    'fft x': round(ffthx,2),
                    'fft y': round(ffthy,2)
                }])           
                
                df = pd.concat([df,new])             
            
df.to_csv(f'{experiment_name}_experiment_data.csv')

                    