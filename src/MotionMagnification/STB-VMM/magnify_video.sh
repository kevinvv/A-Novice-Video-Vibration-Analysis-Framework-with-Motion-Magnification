#!/bin/bash

#This simple script runs the motion magnification pipeline end to end
#Usage example: sh magnify_video.sh -mag 20 -i ./../demo_vid_IQS/14_25Hz_400mV_2.mp4 -s ./../demo_vid_IQS -m ckpt/ckpt_e35.pth.tar -o 14_25Hz_400mV_2 -c

set -e

print_usage() {
  printf "Usage: 
  
  The following arguments must be provided:
  -mag (magnification factor): Video magnification factor (default 20)
  -i (input file): Path pointing to target video (required)
  -s (save dir): Path to a directory to store result files (required)
  -m (model checkpoint): Path to the last model checkpoint (required)
  -o (output): Output project name (required)
  -mod (mode): static(default)/dynamic (params default)
  -f (framerate): Framerate of the input video (default 60)
  -c (cuda): Activates cuda (default cpu)

// added this 
  -ol (output location): used to overwrite the output locationn to work with a wrapper

  "
}

mag_factor='20'
cuda_flag='cpu'
framerate='60'
#input=''
mode='static'
#model_ckpt=''
#output=''
#save_dir=''

while test $# -gt 0; do
        case "$1" in
            -mag)
                shift
                mag_factor=$1
                shift
                ;;
            -c)
                shift
                cuda_flag='cuda'
                ;;
            -f)
                shift
                framerate=$1
                shift
                ;;
            -i)
                shift
                input=$1
                shift
                ;;
            -mod)
                shift
                mode=$1
                shift
                ;;
            -m)
                shift
                model_ckpt=$1
                shift
                ;;
            -o)
                shift
                output=$1
                shift
                ;;
            -s)
                shift
                save_dir=$1
                shift
                ;;
            -ol)
                shift
                output_location=$1
                shift
                ;;
            *)
                echo "$1 is not a recognized flag!"
                print_usage
                return 1;
                ;;
        esac
done 

#Check if required arguments are defined
if [ -z "$input" ] || [ -z "$model_ckpt" ] || [ -z "$output" ] || [ -z "$save_dir" ]; then
    print_usage
    exit 1;
fi

#Convert video to frames
rm -rf "$save_dir"/"$output"_original
rm -rf "$save_dir"/"$output"_mag
mkdir "$save_dir"/"$output"_original
ffmpeg -i "$input" "$save_dir"/"$output"_original/frame_%06d.png

#Reshape frames to be divisible by 64
echo "Reshaping frames..."
num_jobs="\j"  # The prompt escape for number of jobs currently running
max_procs=120 # Change to increase/decrease the concurrent reshaping calculations
for i in "$save_dir"/"$output"_original/*.png; do
    while (( ${num_jobs@P} > $max_procs )); do
        wait -n
    done
    # TODO: had to change this can it be better?
    python3 src/MotionMagnification/STB-VMM/utils/auto_pad.py -i "$i" -d 64 -o "$i" &
done

#Count frames
ls "$save_dir"/"$output"_original|wc -l
num_data=$(($(ls "$save_dir"/"$output"_original|wc -l)-1))

#Magnify frames
# TODO: had to change execution location can it be better?
python3 src/MotionMagnification/STB-VMM/run.py -j4 -b1 --load_ckpt "$model_ckpt" --save_dir "$save_dir"/"$output"_mag --video_path "$save_dir"/"$output"_original/frame --num_data "$num_data" --mode "$mode" --mag "$mag_factor" --device "$cuda_flag"

#Format magnified frames to mp4
# TODO: make scale dynamic
ffmpeg -y -r "$framerate" -i "$save_dir"/"$output"_mag/STBVMM_"$mode"_%06d.png -c:v libx264 -pix_fmt yuv420p -profile:v high -vf scale=640:420 -preset slow -crf 23 -an "$output_location"

exit 0;
