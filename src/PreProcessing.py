import os
import time
import json
from subprocess import Popen
import shutil

class PreProcessing(object):
        
    def process(self, input_location, experiment, processed_location, resolution_new, extension_new):        
    
        for root, subdirs, files in os.walk(f'{input_location}{experiment}'):
            if subdirs == [] or ['.ipynb_checkpoints'] == subdirs:                               
                for file in files:
                    print(root,file)
                    
                    isvideo, extension = self.get_check_extension(file)     
                                  
                    if not isvideo: continue   

                    self.generate_video_metadata(root, file)    
                    filename_new, fps, resolution_old, extension_old = self.generate_rename_video(root, file, extension, input_location)     
                    self.transform_video(processed_location, filename_new, fps, root, resolution_old, resolution_new, extension_old, extension_new)
    

    def get_check_extension(self, file):
        """ only .mp4 and mov supported"""

        extensions = ['.mp4', '.MP4', '.mov', '.MOV']
        _, file_extension = os.path.splitext(file)
            
        return file_extension in extensions, file_extension    

    def generate_video_metadata(self, root, file):
        os.popen(f'ffprobe -v quiet -print_format json -show_format -show_streams "{root}/{file}" > "{root}/{file}.json"')
        time.sleep(1)

    def file_exists(self, file):

        if os.path.isfile(file):
            print(f'file already exists skipping: {file}')
            return True

        return False   
                    

    def generate_rename_video(self, root, file, extension, input_location):
        
        prefix = str.replace(root, input_location, '')
        prefix = str.replace(prefix,'/', '_')
                
        with open(f'{root}/{file}.json') as f:
            d = json.load(f)['streams']                    

            for x in d:
                if x['codec_type'] == 'video':
                    fps = x['r_frame_rate']
                    fps_name = str.replace(fps,'/','-')   
                    width = x['width']
                    height = x['height']  
                    
                    if height > width:
                        height, width = width, height                                    

                    resolution = f"{width}x{height}"                                               
                    break

        suffix = f'{fps_name}_{resolution}'
                
        filename_new = f'{prefix}_{suffix}{extension}'                
        os.rename(f'{root}/{file}',f'{root}/{filename_new}')
        os.rename(f'{root}/{file}.json',f'{root}/{filename_new}.json')

        return filename_new, fps, [width, height], extension
    

    def transform_video(self, processed_location, filename_new, fps, root, ro, rn, eo, en):

        processed_location = str.replace(root,'input', processed_location)

        if not os.path.exists(processed_location):
            os.makedirs(processed_location)
        
        filename_processed = str.replace(f'{processed_location}/{filename_new}', f'{ro[0]}x{ro[1]}',f'{rn[0]}x{rn[1]}')        
        filename_processed = str.replace(filename_processed, eo, en)

        if self.file_exists(filename_processed):
            return filename_processed

        if ro == rn:
            shutil.copy(f"{root}/{filename_new}", filename_processed)
            print('copying')
        else:        
            print('processing')
            Popen(f'ffmpeg -y -r {fps} -i {root}/{filename_new} -c:v libx264 -profile:v high -vf scale=-{rn[0]}:{rn[1]} -preset slow -crf 23 -an {filename_processed}', shell=True).wait()               

