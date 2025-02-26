import os
import cv2
import json
import shutil
import requests
import argparse
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.nasa.gov/mars-photos/api/v1/rovers"
TEMP_DIRECTORY = "temp"
OUTPUT_DIRECTORY = "output"


def make_video(
    video_name: str,
    min_aspect_ratio: float,
    fps: float,
):
    # Make List of Images
    images = []
    widths = []
    heights = []
    for file in os.listdir(TEMP_DIRECTORY):
        if file.endswith(".jpg"):
            im = Image.open(os.path.join(TEMP_DIRECTORY, file))
            width, height = im.size
            if width/height > min_aspect_ratio:
                images.append(file)
                widths.append(width)
                heights.append(height)
    print(f"Images selected: {images}")


    # Crop Images
    print("Resizing images...")
    mean_width = int(sum(widths) / len(images))
    mean_height = int(sum(heights) / len(images))
    for file in images:
        im = Image.open(os.path.join(TEMP_DIRECTORY, file))
        # Use Image.LANCZOS instead of Image.ANTIALIAS for downsampling
        im_resized = im.resize((mean_width, mean_height), Image.LANCZOS)
        im_resized.save(os.path.join(TEMP_DIRECTORY, f"_resized_{file}"), 'JPEG', quality=95)

    

    # Create Video
    frame = cv2.imread(os.path.join(TEMP_DIRECTORY, f"_resized_{images[0]}"))
    height, width, layers = frame.shape
    print(f"Video size: {height}x{width}")
    filename = f"{OUTPUT_DIRECTORY}/{video_name}.avi"
    os.makedirs(os.path.dirname(filename), exist_ok = True)
    video = cv2.VideoWriter(
        filename = filename,
        fourcc = cv2.VideoWriter_fourcc(*'DIVX'),
        fps = fps,
        frameSize = (width, height),
    )

    for image in images:
        video.write(cv2.imread(os.path.join(TEMP_DIRECTORY, f"_resized_{image}")))
        #print(f"Added {os.path.join(TEMP_DIRECTORY, image)}")

    video.release()
    cv2.destroyAllWindows()
    print("Video generated successfully!")

def save_image(
    image_url: str,
    image_id: int,
    force_download: bool,
):
    filename = f"{TEMP_DIRECTORY}/{image_id}.jpg"

    # Check if Image Already Exists
    if os.path.isfile(filename) and force_download == False:
        return

    # Download & Save Image
    r = requests.get(image_url, stream = True)
    if r.status_code == 200:
        os.makedirs(os.path.dirname(filename), exist_ok = True)
        with open(filename, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)


def process_sol(
    sol: int,
    rover: str,
    force_download: bool,
):
    camera_name = "NAVCAM_LEFT"

    params = {
        "api_key": os.environ["NASA_API_KEY"],
        "sol": sol,
        "camera": camera_name,
    }

    # Send request for a day
    r = requests.get(f"{BASE_URL}/{rover}/photos", params=params) 
    if r.status_code != 200:
        raise ValueError("Error sending request!", r.text)
    r = r.json()["photos"]

    # Process Images
    images = []
    for photo in r:
        save_image(
            image_url = photo["img_src"],
            image_id = photo["id"],
            force_download = force_download,
        )


def main(
    rover: str,
    sol_start: int,
    sol_end: int,
    min_aspect_ratio: float,
    force_download: bool,
    fps: float,
    keep_temp: bool,
):
    # Check end sol is in the future
    assert sol_start <= sol_end

    current_sol = sol_start

    # Download Images
    while(current_sol <= sol_end):
        print(f"Processing SOL {current_sol}")
        process_sol(
            sol = current_sol,
            rover = rover,
            force_download = force_download,
        )
        current_sol += 1
    
    # Make Video
    make_video(
        video_name = f"{rover}-SOL{sol_start}-{sol_end}-{fps}fps-{min_aspect_ratio}",
        min_aspect_ratio = min_aspect_ratio,
        fps = fps,
    )

    if not keep_temp:
        # Delete Temp Folder
        shutil.rmtree(TEMP_DIRECTORY)

    



if __name__ == "__main__":

    # Parse input arguments
    parser = argparse.ArgumentParser(
        description = "Use the NASA API to create a timelapse of a Mars NASA rover"
    )
    parser.add_argument(
        "--rover",
        type = str,
        choices = ["perseverance"],
        default = "perseverance",
        help = "Name of rover",
    )
    parser.add_argument(
        "--sol_start",
        type = int,
        default = 301,
        help = "Start sol for timelapse",
    )
    parser.add_argument(
        "--sol_end",
        type = int,
        default = 301,
        help = "End sol for timelapse",
    )
    parser.add_argument(
        "--min_aspect_ratio",
        type = float,
        default = 2.0,
        help = "Minimum Aspect Ratio of Images to Consider",
    )
    parser.add_argument(
        "--fps",
        type = float,
        default = 2.0,
        help = "Frames Per Second (FPS) of the generated timelapse",
    )
    parser.add_argument(
        "--force_download",
        action = "store_true",
        help = "Force download of images.",
    )
    parser.add_argument(
        "--keep_temp",
        action = "store_true",
        help = "Keeps the temp folder containing raw images after download.",
    )
    args = parser.parse_args()

    # Start application
    main(
        rover = args.rover,
        sol_start = args.sol_start,
        sol_end = args.sol_end,
        min_aspect_ratio = args.min_aspect_ratio,
        force_download = args.force_download,
        fps = args.fps,
        keep_temp = args.keep_temp,
    )