<!--
Create folder github-assets for readme assets (gifs, images)

-->

# [DCL] Drone Calibration Lab
The repository for the UT Dallas Drone Calibration Lab.

The DCL is built on top of the PyBullet engine, and serves as a testing environment for cheaply and quickly prototyping combat strategies for drone-on-drone warfare. The DCL also offers benchmarks for AI drone controllers in various tasks.

<!--
demo gifs go here
[[AeroMedLab]](https://www.aeromedlab.com/)
-->

---

## Installation
### Requirements
- We recommend the MiniForge CLI for virtual environment and package management. MiniForge is a much more efficient version of Anaconda, and dramatically improves speed and overall performance. MiniForge is also pre-configured to work with the popular conda-forge channel. You can download the Miniforge installer for your device [here](https://github.com/conda-forge/miniforge). Scroll down to the "Download" section, and choose a version that's right for you.
    - If you still wish to use anaconda, simply replace the "mamba" command with the "conda" command and everything should still work the same, only slower.
    - If you use anaconda, you might need to specify for conda to use the conda-forge channel for some of our required libraries. This can be done by adding the text ``` -c conda-forge ``` onto the end of your installation command.
- Git and your IDE of choice is recommended for cloning/modifying the project onto your local computer. You can download Git [here](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).
- *IMPORTANT NOTE*: The AI model trained by the simulator requires an NVIDIA GPU for use.

#### Create an Environment
- Open MiniForge Prompt and create your virtual environment. Our code was built using Python 3.8, so we recommend this version. 
  ```
  mamba create --name dcl "python=3.8"
  mamba activate dcl
  ```
#### Install Required Libraries 

  - | Library     										 |  Command     					  	|
    | -------------------------------------------------- | ------------------------------------ |
    | python3.8  | |	
    | [mamba*](https://mamba.readthedocs.io/en/latest/installation/mamba-installation.html)      					| Comes pre-installed in MiniForge |
    | [torch](https://pytorch.org/docs/stable/index.html)	      									| ``` mamba install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia ```	|
    | [opencv](https://docs.opencv.org/4.x/)      											| ``` mamba install opencv ```				|					|
    | [matplotlib](https://matplotlib.org/stable/index.html) 									| ``` mamba install matplotlib ```				|
    | [pybullet](https://docs.google.com/document/d/10sXEhzFRSnvFcl3XxNGhnD4N2SedqwdAvK3dsihxVUA/edit#heading=h.2ye70wns7io3)    	| ``` mamba install pybullet ``` 	|
    | [pynput](https://pynput.readthedocs.io/en/latest/) 										| ``` mamba install pynput ```			|
    | [einops](https://einops.rocks/#Installation) 											| ``` mamba install einops ```			|
    | [gstreamer](https://gstreamer.freedesktop.org/documentation/tutorials/index.html?gi-language=c)                                                         | ``` mamba install gstreamer ``` |
    
---

## Quick Start
### How to Run
- Edit your desired changes to CONFIG.py in VSCode/IDE of  choice.
  - There, you can change episode and hitpoly parameters, as well as any other configurations.
- Run Main.py with your desired specifications and appropriate action flag.
  ``` 
  python Main.py --action generate_data
  ```

#### Usage
python Main.py --action [OPTIONS]
python Main.py -a [OPTIONS]

#### Action Flag Options
  - ***help***
  &emsp;Output a usage message and exit.
  - ***build_video***
  &emsp;Creates an ```.mp4``` video visualizing the change in hitpoly for the drone based on its position and direction after completion of data generation and training.
  ###### Data Generation
  - ***generate_data***
  &emsp;Generates initial data for training. Attributes such as ```episode_count``` and ```episode_length``` may be modified.
  - ***stitch_data***
  &emsp;Stitches together tensors generated from ```generate_data```. 
  ###### Hitpoly Training
  - ***train_hitpoly***
  &emsp;Trains the hitpoly model in batches. Hitpoly parameters such as ```epochs```, ```learning rate```, and ```batch size``` may be modified.
  - ***query_hitpoly***
  &emsp;Loads the model output from raw pixel array values to be rendered as color images.
  - ***render_hitpoly***
  &emsp;Generates the hitpoly simulator starting from episode 1. Hold the ```enter``` key to progress each frame.


---

## FAQ
##### It says a GPU is required. Can I run this without a GPU?
No. If you were to attempt to run the simulator anyway, you would receive a runtime error. A dedicated GPU is necessary for the high loads of data and processing.

##### Do I need Mamba? I've never seen this library before.
If this is your first time installing Mamba, you may choose to not use it and instead stick with conda instead. This will be considerably slower, however, as conda is quite old and has not aged well.

##### Error: "Torch not compiled with CUDA enabled."
You may have a CPU-only Pytorch version previously installed. Try installing pytorch in a clean MiniForge environment via mamba, and see if that resolves the issue.

##### Error: "Initializing libiomp5md.dll, but found libiomp5md.dll already initialized."
This is an old anaconda error which can be fixed by deleting the libiomp5md.dll file located in anaconda3/envs/dcl/Library/bin/, as is described in [this stack overflow post](https://stackoverflow.com/questions/20554074/sklearn-omp-error-15-initializing-libiomp5md-dll-but-found-mk2iomp5md-dll-a
).





---