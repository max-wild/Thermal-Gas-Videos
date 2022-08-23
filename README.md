
# Rendering Thermal Video of Gas

This [**Python notebook**](https://github.com/max-wild/Thermal-Gas-Videos/blob/main/thermal_gas_videos.ipynb) built using Google Colab allows for very easy video generation of gas:

<p float="left" align="middle" display="flex" align-items="center">
<img src="https://github.com/max-wild/Thermal-Gas-Videos/raw/main/examples/example.gif" width="32%">
<img src="https://github.com/max-wild/Thermal-Gas-Videos/raw/main/examples/example2.gif" width="32%">
<img src="https://github.com/max-wild/Thermal-Gas-Videos/raw/main/examples/example3.gif" width="32%">
</p>

<hr>

The simulation is realistic to the real-world, using physics from the program Blender. Each render of a video uses a randomized environment for the gas, leading to individual renders for every video. Blender renders in frames of 128x128 pixels, and there are 4 easily changeable parameters to adjust the results:

 1. `fps` determines the frame-rate of the video in frames per second
 2. `seconds` lets you decide how long the video should be, in seconds
 3. `video_count` sets how many videos (with different gas scenarios) are created
 4. `render_image_slideshow` lets you pick between rendering each scenario in a single .mp4 video, or a series of .png images

## Generated Environments

Each environment for the gas changes many different parameters to ensure that every scenario is complex, akin to the real world. Each scenario includes changes to forces such as:

 - Wind direction and strength
 - Temperature of the gas in relation to the environment
 - Gas buoyancy
 - Gas vorticity
 - Direction of lighting
 - Air turbulence and noise intensity
 - Initial direction of emitted particles
 - Amounts of initial emitted particles
 - Density and color of gas (in greyscale)

## Note

If Google Colab is used to run this project, ensure that the runtime is connected to a GPU with Edit->Notebook settings->Hardware accelerator->GPU 

Cheers!
Max
