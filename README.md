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
- We use Anaconda CLI for virtual environment and package management. You can install Anaconda for your device [here](https://docs.anaconda.com/free/anaconda/getting-started/index.html) or continue with your venv of choice.
- Git and your IDE of choice is required for cloning/modifying the project onto your local computer. You can download Git [here](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).
- *IMPORTANT NOTE*: This simulator requires an NVIDIA GPU for use.

#### Setting the Stage
- Open Anaconda Prompt and create your virtual environment. We use Python version 3.8.
  ```
  conda create --name dcl python=3.8
  conda activate dcl
  ```
#### Install Dependencies 

  - | Library     										 |  Command     					  	|
    | -------------------------------------------------- | ------------------------------------ |
    | python3.8  | |	
    | [mamba*](https://mamba.readthedocs.io/en/latest/installation/mamba-installation.html)      					| ```conda install -n base --override-channels -c conda-forge mamba 'python_abi=*=*cp*' ``` |
    | [torch](https://pytorch.org/docs/stable/index.html)	      									| ```mamba install pytorch=*=*cuda* cudatoolkit -c pytorch```	|
    | [opencv](https://docs.opencv.org/4.x/)      											| ``` mamba install opencv ```				|					|
    | [matplotlib](https://matplotlib.org/stable/index.html) 									| ``` mamba install matplotlib ```				|
    | [pybullet](https://docs.google.com/document/d/10sXEhzFRSnvFcl3XxNGhnD4N2SedqwdAvK3dsihxVUA/edit#heading=h.2ye70wns7io3)    	| ``` mamba install -c conda-forge pybullet ``` 	|
    | [pynput](https://pynput.readthedocs.io/en/latest/) 										| ``` mamba install conda-forge::pynput ```			|
    | [einops](https://einops.rocks/#Installation) 											| ``` mamba install conda-forge::einops ```			|
    | [gstreamer](https://gstreamer.freedesktop.org/documentation/tutorials/index.html?gi-language=c)                                                         | ```mamba install anaconda::gstreamer``` |
    - *mamba library is optional, but recommended to speed up Conda runtime and installations. If you choose to not use Mamba, just run `conda` instead of   `mamba` commands.

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
If this is your first time installing Mamba, you may choose to not install it and instead stick with Conda commands instead. Mamba may take some time to install, so if you'd like to jump in ASAP, you can choose to forego it.

##### Error: "Torch not compiled with CUDA enabled."
You may have a CPU-only Pytorch version previously installed. In that event, installing a new Pytorch would not fix the issue as it continues to use the cached CPU-only version -- you will need to uninstall and reinstall.
  ```
    pip uninstall torch
    pip cache purge
    pip install torch -f https://download.pytorch.org/whl/torch_stable.html
  ```

##### Error: "Initializing libiomp5md.dll, but found libiomp5md.dll already initialized."
This can be fixed by deleting the libiomp5md.dll file located in anaconda3/envs/dcl/Library/bin/, as is described in [this stack overflow post](https://stackoverflow.com/questions/20554074/sklearn-omp-error-15-initializing-libiomp5md-dll-but-found-mk2iomp5md-dll-a
).





---