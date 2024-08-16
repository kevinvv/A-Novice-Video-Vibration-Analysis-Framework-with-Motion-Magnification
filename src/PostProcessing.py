import os
from subprocess import Popen

from .MotionMagnificationManager import VMM


class PostProcessing(object):

    def process(self, input_location, experiment, output_location, MFS):

        for root, subdirs, files in os.walk(f'{input_location}{experiment}'):
            if subdirs == [] or ['.ipynb_checkpoints'] == subdirs:                 
                for file in files:

                    input = f'{root}/{file}'

                    merged_location = str.replace(root, 'processed',output_location)
                    print(merged_location)
                    if not os.path.exists(merged_location):
                        os.makedirs(merged_location)
                                                                              
                    self.compare_all_mag__one_method_factor(input, MFS)
                    self.compare_one_mag_all_method_factor(input, MFS)
                    

    def compare_all_mag__one_method_factor(self, input, MFS):

        topleft = original = input
        
        m = []

        for method in VMM:

            o = []
            
            output = str.replace(original,'processed','merged')
            output = str.replace(output, '.mp4', f'_{method}@ALL.mp4')

            for mf in MFS:
                m.append(mf)
                temp = str.replace(input,'processed', 'magnified')
                temp = str.replace(temp, '.mp4', f'_{method.value}@{mf}.mp4')
                o.append(temp)     

            
            Popen(f'ffmpeg -r 50 \
                  -i {topleft} -i {o[0]} -i {o[1]} -i {o[2]}\
                  -filter_complex \
                       "[0:v] setpts=PTS-STARTPTS, scale=-1:720, drawtext=text=Original:fontsize=20:x=30:y=30:fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=5 [a0];\
                        [1:v] setpts=PTS-STARTPTS, scale=-1:720, drawtext=text={method.value}@{m[0]}:fontsize=20:x=30:y=30:fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=5 [a1];\
                        [2:v] setpts=PTS-STARTPTS, scale=-1:720, drawtext=text={method.value}@{m[1]}:fontsize=20:x=30:y=30:fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=5 [a2];\
                        [3:v] setpts=PTS-STARTPTS, scale=-1:720, drawtext=text={method.value}@{m[2]}:fontsize=20:x=30:y=30:fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=5 [a3];\
                        [a0][a1][a2][a3] xstack=inputs=4:layout=0_0|w0_0|0_h0|w0_h0[v]"\
                  -map "[v]" {output}', shell=True).wait()           
                    

    def compare_one_mag_all_method_factor(self, input, MFS):
        
        topleft = original = input
                
        m = []

        for mf in MFS:

            o = []

            output = str.replace(original,'processed','merged')
            output = str.replace(output, '.mp4', f'_ALL@{mf}.mp4')

            for method in VMM:

                m.append(method.value)                     
                temp = str.replace(input,'processed', 'magnified')
                temp = str.replace(temp, '.mp4', f'_{method.value}@{mf}.mp4')
                o.append(temp)
            
            Popen(f'ffmpeg -r 50 \
                    -i {topleft} -i {o[0]} -i {o[1]} -i {o[2]}\
                    -filter_complex \
                        "[0:v] setpts=PTS-STARTPTS, scale=-1:720, drawtext=text=Original:fontsize=20:x=30:y=30:fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=5 [a0];\
                            [1:v] setpts=PTS-STARTPTS, scale=-1:720, drawtext=text={m[0]}@{mf}:fontsize=20:x=30:y=30:fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=5 [a1];\
                            [2:v] setpts=PTS-STARTPTS, scale=-1:720, drawtext=text={m[1]}@{mf}:fontsize=20:x=30:y=30:fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=5 [a2];\
                            [3:v] setpts=PTS-STARTPTS, scale=-1:720, drawtext=text={m[2]}@{mf}:fontsize=20:x=30:y=30:fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=5 [a3];\
                            [a0][a1][a2][a3] xstack=inputs=4:layout=0_0|w0_0|0_h0|w0_h0[v]"\
                    -map "[v]" {output}', shell=True).wait()  
                


