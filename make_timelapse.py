import os
import json
import shutil
import requests
import argparse
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.nasa.gov/mars-photos/api/v1/rovers"
TEMP_DIRECTORY = "temp"


def save_image(
    image_url: str,
    image_id: int,
):
    filename = f"{TEMP_DIRECTORY}/{image_id}.jpg"

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

    # Explore results
    for photo in r:
        save_image(
            image_url = photo["img_src"],
            image_id = photo["id"],
        )


def main(
    rover: str,
    sol_start: int,
    sol_end: int,
):
    assert sol_start <= sol_end

    current_sol = sol_start

    while(current_sol <= sol_end):
        process_sol(
            sol = current_sol,
            rover = rover,
        )
        current_sol += 1

    



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
    args = parser.parse_args()

    # Start application
    main(
        rover = args.rover,
        sol_start = args.sol_start,
        sol_end = args.sol_end,
    )