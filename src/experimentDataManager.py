import os
import sys

class ExperimentDataManager(object):

    input_location = ''
    experiments = []
    experiments_info = {}
    to_process = []

    def __init__(self, input_location) -> None:
        self.input_location = input_location
        self.get_experiments(self.input_location)
        self.get_data_experiments(self.experiments)
        self.to_process = self.get_experiments_to_process(self.experiments_info)

    def get_experiments(self, experiment_folder:str):
        self.experiments = os.listdir(experiment_folder)

        if '.DS_Store' in self.experiments:
            self.experiments.remove('.DS_Store')
            
        if '.ipynb_checkpoints' in self.experiments:
            self.experiments.remove('.ipynb_checkpoints')
    
        if len(self.experiments) <= 0:
            sys.exit('No experiments found, please add them into the input folder')
        else:
            print(f'Loaded {len(self.experiments)} experiment(s)')

    def get_data_experiments(self, experiments):
        """for now only checks for isprocessed file"""

        for experiment in experiments:

            # experiment should be folder
            if os.path.isdir(os.path.join(self.input_location, experiment)):

                isproccessed = False            

                if os.path.isfile(f'{self.input_location}{experiment}/isproccessed.check'):     
                    isproccessed = True

                self.experiments_info[experiment] = {'isproccessed':isproccessed}

    def get_experiments_to_process(self, experiments):
        to_process = []

        for i in experiments:
            if experiments[i]['isproccessed'] == False:
                to_process.append(i)

        return to_process

                

