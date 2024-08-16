from subprocess import Popen
import os
from enum import Enum
# import shutil

class VMM(Enum):
    WUEB = 'wueb'
    LB = 'lb'
    STB = 'stb'


class MotionMagnificationManager(object):

    entrypoint_prefix = 'src/MotionMagnification/'

    def process(self, input_location, experiment, output_location, MFS, VMMS):       
            
        for root, subdirs, files in os.walk(f'{input_location}{experiment}'):
            
            if subdirs == [] or ['.ipynb_checkpoints'] == subdirs:     
                
                for file in files:                      

                    print(root, file)
                    input = f'{root}/{file}'

                    magnified_location = str.replace(root, 'processed','magnified')

                    if not os.path.exists(magnified_location):
                        os.makedirs(magnified_location)

                    for vmm in VMMS:

                        if vmm == VMM.WUEB:

                            self.magnification_helper(MFS, self.execute_WUEB, input, output_location)                            

                        elif vmm == VMM.LB:
                            

                            self.magnification_helper(MFS, self.execute_LB, input, output_location)                                                    

                        elif vmm == VMM.STB:  

                            self.magnification_helper(MFS, self.execute_STB, input, output_location)                            
                        
                        else:
                            print('not a valid method')
                    

    def magnification_helper(self, MFS, method, input_location, output_location):

        for mf in MFS:                    
            output = method(input_location, mf, output_location)                        
            print(f'File at: {output}')


    def generate_model_entrypoint_location(self, suffix):
        return f'{self.entrypoint_prefix}{suffix}'
    

    def generate_output_path(self, input, output, MF, MMM):
        output = str.replace(input, 'processed', output)
        output = str.replace(output, '.mp4', f'_{MMM.value}@{MF}.mp4') 
        return output

    def file_exists(self, file):

        if os.path.isfile(file):
            print(f'file already exists skipping: {file}')
            return True

        return False    

    def execute_WUEB(self, input_location, MF, output_location, entrypoint_suffix = f'WUEB-VMM/evm.py'):                

        entrypoint = self.generate_model_entrypoint_location(entrypoint_suffix)
        output_location = self.generate_output_path(input_location, output_location, MF, VMM.WUEB)
        
        if self.file_exists(output_location):
            return output_location    
        
        mode = 'laplacian' # this is the motion option
        lc = 264
        lo = 0.4 # frequency cutoff low
        ho= 24  # frequency cutoff high

        Popen(f'python3 {entrypoint} -v={input_location} -a{MF} \
            -s{output_location} -m={mode} --lambda_cutoff={lc} \
            --low_omega={lo} --high_omega={ho} ', shell=True).wait()  
        return output_location          
        

    def execute_LB(self, input_location, MF, output_location, entrypoint_suffix = f'LB-VMM/main.py'):

        entrypoint = self.generate_model_entrypoint_location(entrypoint_suffix)
        output_location = self.generate_output_path(input_location, output_location, MF, VMM.LB)

        if self.file_exists(output_location):
            return output_location

        method = 'amplify'
        checkpoint = 'src/MotionMagnification/LB-VMM/20191204-b4-r0.1-lr0.0001-05.pt'       
        
        print(f'python3 {entrypoint} {method} {checkpoint} \
              {input_location} {output_location} --amplification={MF}')

        Popen(f'python3 {entrypoint} {method} {checkpoint} \
              {input_location} {output_location} --amplification={MF}',
                shell=True).wait()           

        return output_location    
        

    def execute_STB(self, input_location, MF, output_location, entrypoint_suffix = f'STB-VMM/magnify_video.sh'):

        entrypoint = self.generate_model_entrypoint_location(entrypoint_suffix)
        output_location = self.generate_output_path(input_location, output_location, MF, VMM.STB)

        if self.file_exists(output_location):
            return output_location

        checkpoint = 'src/MotionMagnification/STB-VMM/ckpt/ckpt_e49.pth.tar'

        o = 'thisisoverhead'
        s = 'resources/temp/'

        fps = 50 # TODO: this should be dynamic

        # -c is to activate cuda
        Popen(f'bash {entrypoint} -mag {MF} -i {input_location} \
              -m {checkpoint} -o {o} -s {s} -f {fps} -ol {output_location} -c',
              shell=True).wait()
        
        return output_location


        