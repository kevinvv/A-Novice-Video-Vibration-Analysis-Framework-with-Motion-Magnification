import os
import cv2
import sys
import numpy as np
import scipy.stats as stats
import plotly.express as px
import pandas as pd

from tqdm import tqdm
import plotly.graph_objects as go
import json

class Evaluate(object):


    def process(self, input_location, experiment, origin, output_location='evaluated'):

        for root, subdirs, files in os.walk(f'{input_location}{experiment}'):
            if subdirs == [] or ['.ipynb_checkpoints'] == subdirs:                 
                for file in files:

                    input = f'{root}/{file}'

                    evaluate_location = str.replace(root, origin, output_location)                    
                    if not os.path.exists(evaluate_location):
                        os.makedirs(evaluate_location)

                    helping = str.split(root,'/')
                    for help in helping:
                        if 'fps' in help:
                            fps = int(str.replace(help, 'fps',''))
                    

                    df = self.extract_pixel_displacement(evaluate_location, input, fps)                    
                    df.to_csv(f"{evaluate_location}/{file}_pixel_displacement.csv")                

                    upperx, lowerx = self.plot_displacement_over_time(evaluate_location, file, df, 'dx')
                    uppery, lowery = self.plot_displacement_over_time(evaluate_location, file, df, 'dy')
                    nfx10, nfy10 = self.calculate_fft_and_extract_natural_frequency(evaluate_location, file, df, fps)

                    freqsdata = {}
                    freqsdata['upperx'] = upperx
                    freqsdata['lowerx'] = lowerx
                    freqsdata['uppery'] = uppery
                    freqsdata['lowery'] = lowery
                    freqsdata['freqsx'] = nfx10.tolist()
                    freqsdata['freqsy'] = nfy10.tolist()

                    
                    with open(f"{evaluate_location}/{file}_frequency_data.json", "w") as text_file:
                        text_file.write(json.dumps(freqsdata))

                    with open(f"{evaluate_location}/{file}_frequency_x:{round(nfx10[0],2)}Hz-y:{round(nfy10[0],2)}Hz.freq", "w") as text_file:
                        pass                

    def plot_displacement_over_time(self, output_location, file, df, axis, show=False):
        
        upper_limit = df[axis].mean() + 3*df[axis].std()
        lower_limit = df[axis].mean() - 3*df[axis].std()

        upper_outliers = stats.zscore(df[axis]) > 2
        lower_outliers = stats.zscore(df[axis]) < -2

        df.loc[upper_outliers, axis] = np.float32(upper_limit)
        df.loc[lower_outliers, axis] = np.float32(lower_limit)

        fig = px.line(df, x='iteration', y=[axis],labels={'value': 'Displacement', 'variable': 'Axis'},title=f'Movement of Point Over Time')
        fig.update_layout(xaxis_title='iteration'.capitalize(), yaxis_title='Displacement (pixels)', showlegend=True)
        
        if show:
            fig.show()

        fig.write_image(f'{output_location}/{file}_displacement_{axis}.png')

        return upper_limit, lower_limit

    def get_roi(self, root):

        root = str.replace(root,'evaluated','input')

        with open(f"{root}/roi.roi") as file:
            for line in file:        
                x, y, w, h = line.rstrip().split(' ') 
                x, y, w, h = int(y), int(h), int(x), int(w)

        return x, y, w, h


    def extract_pixel_displacement(self,root, input, fps):

        cap = cv2.VideoCapture(input)

        # Set up parameters for ShiTomasi corner detection
        feature_params = dict(maxCorners=1, qualityLevel=0.3, minDistance=7, blockSize=7)

        # Set up parameters for Lucas-Kanade optical flow
        lk_params = dict(winSize=(15, 15), maxLevel=2, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
        
        ret, old_frame = cap.read()
        old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)

        x, y, w, h = self.get_roi(root)

        roi_mask = np.zeros_like(old_gray)
        roi_mask[y:y+h, x:x+w] = 255    

        point_old = cv2.goodFeaturesToTrack(old_gray, mask=roi_mask, **feature_params)

        if point_old is None:
            print("Unable to determine tracking features, please adjust bounding box.")
            cap.release() 
            sys.exit() 

        displacements = []
        iteration = 0

        with tqdm(total=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), desc="Tracking") as pbar:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                point_new, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, point_old, None, **lk_params)

                if point_new is not None and len(point_new) > 0:

                    good_new = point_new[st == 1]
                    good_old = point_old[st == 1]

                    for i, (new, old) in enumerate(zip(good_new, good_old)):                
                        a, b = new.ravel()
                        c, d = old.ravel()
                        displacements.append({'iteration': iteration, 'time': pbar.n / fps, 'id': i, 'x': a, 'y': b, 'dx': a - c, 'dy': b - d})
                    
                    old_gray = frame_gray.copy()
                    point_old = good_new.reshape(-1, 1, 2)
                else:
                    print("Unable to determine tracking features, please adjust bounding box.")
                    break  

                pbar.update(1)
                iteration += 1

        cap.release()

        return pd.DataFrame(displacements)

    def fft_positive_frequencies(self, signal, fps):

        fft = np.fft.fft(signal)
        fft_freq = np.fft.fftfreq(len(signal), d=1/fps)

        fft_positive = fft[:len(signal)//2]
        fft_freq_positive = fft_freq[:len(signal)//2]

        return fft_freq_positive, np.abs(fft_positive)


    def calculate_fft_and_extract_natural_frequency(self, output_location, file, df, fps, show=False):
        
        freqs, fft_dx = self.fft_positive_frequencies(df['dx'], fps)
        _, fft_dy = self.fft_positive_frequencies(df['dy'], fps)        

        top_10_indicesx = np.argsort(fft_dx)[-10:][::-1]    
        top_10_frequenciesx = freqs[top_10_indicesx]        

        top_10_indicesy = np.argsort(fft_dy)[-10:][::-1]    
        top_10_frequenciesy = freqs[top_10_indicesy]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=freqs,y=fft_dy,mode='lines',name='dy',line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=freqs,y=fft_dx,mode='lines',name='dx',line=dict(color='red')))
        fig.update_layout(title='Frequency Spectrum', xaxis_title='Frequency (Hz)', yaxis_title='Amplitude',showlegend=True)

        if show:
            fig.show()

        
        df = pd.DataFrame({'frequency': freqs, 'dx': fft_dx,'dy': fft_dy})        
        df.to_csv(f'{output_location}/{file}_FFT.csv')
        fig.write_image(f'{output_location}/{file}_FFT.png')

        return top_10_frequenciesx, top_10_frequenciesy

                        