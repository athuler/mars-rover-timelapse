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
    all_images: list,
    video_name: str,
    min_aspect_ratio: float,
    fps: float,
):
    # Make List of Images
    images = []
    widths = []
    heights = []
    for file in all_images:
        im = Image.open(os.path.join(TEMP_DIRECTORY, file))
        width, height = im.size
        if width/height > min_aspect_ratio:
            images.append(file)
            widths.append(width)
            heights.append(height)
    
    if images == []:
        print("ERROR: No images found")
        return


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
    print("Creating video...")
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
    print(filename)


def save_image(
    image_url: str,
    image_id: int,
    force_download: bool,
    rover: str,
    camera: str,
):
    filename = f"{rover}-{camera}-{image_id}.jpg"
    full_filename = f"{TEMP_DIRECTORY}/{filename}"

    # Check if Image Already Exists
    if os.path.isfile(full_filename) and force_download == False:
        return filename

    # Download & Save Image
    r = requests.get(image_url, stream = True)
    if r.status_code == 200:
        os.makedirs(os.path.dirname(full_filename), exist_ok = True)
        with open(full_filename, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
    return filename


def process_sol(
    sol: int,
    rover: str,
    force_download: bool,
    camera: str,
    key: str,
):
    
    if key != "":
        API_KEY = key
    elif "NASA_API_KEY" in os.environ:
        API_KEY = os.environ["NASA_API_KEY"]
    else:
        raise ValueError("Missing NASA API Key!")


    params = {
        "api_key": API_KEY,
        "sol": sol,
        "camera": camera,
    }

    # Send request for a day
    r = requests.get(f"{BASE_URL}/{rover}/photos", params=params) 
    if r.status_code != 200:
        raise ValueError("Error sending request!", r.text)
    r_json = r.json()["photos"]

    # Process rate limit headers
    if "X-RateLimit-Remaining" in r.headers:
        ratelimit_remaining = int(r.headers["X-RateLimit-Remaining"])
        if ratelimit_remaining < 250:
            print(f"WARNING: {ratelimit_remaining} API requests remaining in your limit.")
    else:
        print(f"WARNING: Unknown number of API requests remaining in your limit")


    # Process Images
    images = []
    for photo in r_json:
        images.append(save_image(
            image_url = photo["img_src"],
            image_id = photo["id"],
            force_download = force_download,
            rover = rover,
            camera = camera,
        ))
    return images


def main(
    rover: str,
    sol_start: int,
    sol_end: int,
    min_aspect_ratio: float,
    force_download: bool,
    fps: float,
    keep_temp: bool,
    camera: str,
    key: str,
):
    # Check end sol is in the future
    assert sol_start <= sol_end

    current_sol = sol_start

    # Download Images
    images = []
    while(current_sol <= sol_end):
        print(f"Processing SOL {current_sol}...")
        images.extend(process_sol(
            sol = current_sol,
            rover = rover,
            force_download = force_download,
            camera = camera,
            key = key,
        ))
        current_sol += 1
    
    # Make Video
    make_video(
        all_images = images,
        video_name = f"{rover}-{camera}-SOL{sol_start}-{sol_end}-{fps}fps-{min_aspect_ratio}",
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
        choices = ["perseverance", "curiosity"], # See README about why opportunity and spirit aren't options
        required = True,
        help = "Name of rover",
    )
    parser.add_argument(
        "--sol_start",
        type = int,
        required = True,
        help = "Start sol for timelapse",
    )
    parser.add_argument(
        "--sol_end",
        type = int,
        required = True,
        help = "End sol for timelapse",
    )
    parser.add_argument(
        "--min_aspect_ratio",
        type = float,
        default = 0,
        help = "Minimum Aspect Ratio of Images to Consider",
    )
    parser.add_argument(
        "--fps",
        type = float,
        default = 2.0,
        help = "Frames Per Second (FPS) of the generated timelapse",
    )
    parser.add_argument(
        "--camera",
        type = str,
        default = "NAVCAM_LEFT",
        help = "Camera on the rover",
    )
    parser.add_argument(
        "--key",
        type = str,
        default = "",
        help = "NASA API Key",
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
        camera = args.camera,
        key = args.key,
    )