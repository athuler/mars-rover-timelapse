# Mars Rover Timelapse
Tool to create timelapses from Mars rover images using the [Mars Rover Photo API](https://github.com/corincerami/mars-photo-api).

![curiosity-FHAZ-SOL340-345-5 0fps-0 0](https://github.com/user-attachments/assets/b2253532-dd05-438a-a6dc-c2845d4ea8ce)

## Installation

1. Clone the repository
2. Install the requirements: `pip install -r requirements.txt`
3. [Sign up for a NASA API Key](https://api.nasa.gov/)
4.
    Create a file named `.env` containing `NASA_API_KEY=<YOUR API KEY>`
    **OR**
    When using the tool, pass the additional parameter `--key <YOUR API KEY>`

## Usage

```sh
python make_timelapse.py \
    --rover perseverance \
    --camera FRONT_HAZCAM_LEFT_A \
    --sol_start 300 \
    --sol_start 310
```

| Argument / Flag | Possible Values   | Description      |
| ------------- | ------------- | ------------- |
| `--rover` | `perseverance`, `curiosity` | **REQUIRED**  Name of the rover from which to download images. |
| `--camera` | [valid camera name](https://github.com/corincerami/mars-photo-api?tab=readme-ov-file#cameras)<br/>ex: `FRONT_HAZCAM_LEFT_A` | **REQUIRED**  Name of the rover from which to download images. |
| `--sol_start` | [SOL calculator](https://solonmars.com/)<br/>ex: `305` | **REQUIRED**  First Mars SOL to include in the timelapse. |
| `--sol_end` | [SOL calculator](https://solonmars.com/)<br/>ex: `315` | **REQUIRED**  Last Mars SOL to include in the timelapse. Must be equal or greater than `sol_start` |
| `--img_perc_start` | integer between `0` and `100` | Trim the start of the timelapse. Must be lower than `img_perc_end`. Defaults to `0`. |
| `--img_perc_end` | integer between `0` and `100` | Trim the end of the timelapse. Must be greater than `img_perc_start`. Defaults to `100`. |
| `--fps` | integer `> 0` | Frames per second of exported video. Default: `2` |
| `--min_aspect_ratio` | float `> 0.0` | Minimum aspect ratio of pictures to include in the timelapse. Default: `0` |
| `--key` | Your NASA API Key | Pass your NASA API Key as an argument if you did not create a `.env` file. **REQUIRED if no `.env` file** |
| `--keep_temp` | N/A | Pass this flag to prevent the deletion of the temporary directory containing the raw and resized images upon completion. On the following runs, images will not be redownloaded unless `--force_download` is passed. |
| `--force_download` | N/A | Pass this flag to force downloading of images that already exist in the temp directory if it exists |



> [!NOTE]  
> The `opportunity` and `spirit` rover images are unavailable as NASA took down the images from their server. You can read more about it on [this](https://github.com/corincerami/mars-photo-api/issues/197) Github issue and [this](https://www.reddit.com/r/Mars/comments/1c7a4kd/due_to_the_website_change_i_can_no_longer_find/) Reddit thread.

## Examples

```bash
python make_timelapse.py \
    --sol_start 0 \
    --sol_end 5 \
    --keep_temp \
    --fps 5 \
    --rover perseverance \
    --camera EDL_DDCAM 
```
![perseverance-EDL_DDCAM-SOL0-5-5 0fps-0 0](https://github.com/user-attachments/assets/d76e8477-3299-4bac-850c-fc9e129da78a)

```bash
python make_timelapse.py \
    --sol_start 2 \
    --sol_end 2 \
    --img_perc_end 14 \
    --keep_temp \
    --fps 5 \
    --rover perseverance \
    --camera EDL_RDCAM
```
![perseverance-EDL_RDCAM-SOL2-2-5 0fps-0 0-0_-14_](https://github.com/user-attachments/assets/e7fa4174-39f8-46d3-8dc9-a83182b9f841)

```bash
python make_timelapse.py \
    --sol_start 1250 \
    --sol_end 1350 \
    --keep_temp \
    --fps 5 \
    --rover perseverance \
    --camera REAR_HAZCAM_LEFT
```
![perseverance-REAR_HAZCAM_LEFT-SOL1250-1350-5 0fps-0 0](https://github.com/user-attachments/assets/a8e7605d-a40f-41dd-81ee-3972865a1d2a)

