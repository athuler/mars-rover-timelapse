# Mars Rover Timelapse
 Create timelapses from Mars rover images using the [Mars Rover Photo API](https://github.com/corincerami/mars-photo-api)


## Installation


## Usage

```sh
python make_timelapse.py \
    --rover perseverance \
    --camera FRONT_HAZCAM_LEFT_A \
    --sol_start 300 \
    --sol_start 310
```

| Flag          | Possible Values   | Description      |
| ------------- | ------------- | ------------- |
| `--rover` | `perseverance`, `curiosity` | **REQUIRED**  Name of the rover from which to download images. |
| `--camera` | [valid camera names](https://github.com/corincerami/mars-photo-api?tab=readme-ov-file#cameras)<br/>ex: `FRONT_HAZCAM_LEFT_A` | **REQUIRED**  Name of the rover from which to download images. |
| `--sol_start` | [SOL calculator](https://solonmars.com/)<br/>ex: `305` | **REQUIRED**  First Mars SOL to include in the timelapse. |
| `--sol_end` | [SOL calculator](https://solonmars.com/)<br/>ex: `315` | **REQUIRED**  Last Mars SOL to include in the timelapse. Must be equal or greater than `sol_start` |
| `--fps` | integer `> 0` | Frames per second of exported video. Default: `2` |
| `--min_aspect_ratio` | float `> 0.0` | Minimum aspect ratio of pictures to include in the timelapse. Default: `0` |
| `--keep_temp` | N/A | Pass this flag to prevent the deletion of the temporary directory containing the raw and resized images upon completion. On the following runs, images will not be redownloaded unless `--force_download` is passed. |
| `--force_download` | N/A | Pass this flag to force downloading of images that already exist in the temp directory if it exists |



> [!NOTE]  
> The `opportunity` and `spirit` rover images are unavailable as NASA took down the images from their server. You can read more about it on [this](https://github.com/corincerami/mars-photo-api/issues/197) Github issue and [this](https://www.reddit.com/r/Mars/comments/1c7a4kd/due_to_the_website_change_i_can_no_longer_find/) Reddit thread.