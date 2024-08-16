import sys

from src.utils import setcwd_to_file_location
from src.experimentDataManager import ExperimentDataManager
from src.PreProcessing import PreProcessing
from src.MotionMagnificationManager import MotionMagnificationManager, VMM
from src.PostProcessing import PostProcessing
from src.Evaluate import Evaluate

def main():

    setcwd_to_file_location(__file__)

    input_location = 'resources/input/'
    edm = ExperimentDataManager(input_location)

    processed_location = 'processed'
    preprocess_resolution = [640,420] 
    preprocess_extension = '.mp4'
    prep = PreProcessing() # Includes preperation and preprocessing

    magnified_location = 'magnified'
    MFS = [3,5,10]
    VMMS = [VMM.WUEB, VMM.LB, VMM.STB]
    mm = MotionMagnificationManager()

    merged_location = 'merged'
    postp = PostProcessing()
    
    evaluted_location = 'evaluated'
    evaluate = Evaluate()

    print(f'The following expiriments are found: \n {edm.experiments_info}')        
    print('Start processing experiments that are not processed yet:')
    
    for experiment in edm.to_process:        
        # prep.process(input_location, experiment, processed_location, preprocess_resolution,preprocess_extension)
        # mm.process(str.replace(input_location,'input',processed_location), experiment, magnified_location, MFS, VMMS)        
        evaluate.process(str.replace(input_location,'input',processed_location), experiment, processed_location, evaluted_location)
        evaluate.process(str.replace(input_location,'input',magnified_location), experiment, magnified_location ,evaluted_location)    
        postp.process(str.replace(input_location,'input',processed_location), experiment, merged_location, MFS)



if __name__ == "__main__":
    main()