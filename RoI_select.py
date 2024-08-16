import cv2
import argparse
import os
import sys
import numpy as np


def main(experiment):

    for root, subdirs, files in os.walk(f'resources/input/{experiment}'):
            
        if subdirs == [] or ['.ipynb_checkpoints'] == subdirs:     
            for file in files:                  

                _, file_extension = os.path.splitext(file)

                if file_extension != '.mp4' and file_extension != '.MP4':                    
                    continue

                print(file)
                     
                file = f'{root}/{file}'

                cap = cv2.VideoCapture(file)
                _, old_frame = cap.read()
                old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)

                # hand select ROI
                info = "Click and drag a square around the region of intrest. Press enter when done. ()"
                bbox = cv2.selectROI(img=old_frame, showCrosshair=True, windowName=info)
                cv2.destroyAllWindows()
                cv2.waitKey(1)
                x, y, w, h = bbox

                feature_params = dict(maxCorners=1, qualityLevel=0.3, minDistance=7, blockSize=7)
                roi_mask = np.zeros_like(old_gray)
                roi_mask[y:y+h, x:x+w] = 255

                point_old = cv2.goodFeaturesToTrack(old_gray, mask=roi_mask, **feature_params)

                if point_old is None:
                    print("Unable to determine tracking features, please adjust bounding box if you want it to be usefull :D.")                    

                # print(x,y,w,h)
                with open(f"{root}/roi.roi", "w") as text_file:
                    text_file.write(f"{x} {y} {w} {h}")

                with open(f"{root}/roi.roi") as file:
                    for line in file:
                        print(line.rstrip())

                cap.release() 
            

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Eulerian Video Magnification for colors and motions magnification"
    )

    parser.add_argument(
        "--experiment_name",
        "-en",
        type=str,
        help="Name of experiment to select RoI of",
        required=True
    )

    args = parser.parse_args()


    main(args.experiment_name)