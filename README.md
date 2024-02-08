<!--
Create folder github-assets for readme assets (gifs, images)

-->

# [DCL] Drone Combat Lab
The repository for the UT Dallas Drone Combat Lab.

The DCL is built on top of the PyBullet engine, and serves as a testing environment for cheaply and quickly prototyping combat strategies for drone-on-drone warfare. The DCL also offers benchmarks for AI drone controllers in various tasks.

<!--
demo gifs go here
[[AeroMedLab]](https://www.aeromedlab.com/)
-->

---

## Installation
### Requirements
- We use Anaconda CLI for virtual environment and package management. You can install Anaconda for your device [here](https://docs.anaconda.com/free/anaconda/getting-started/index.html) or continue with your venv of choice.
- Git and your IDE of choice is required for cloning/modifying the project onto your local computer. You can download Git [here](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) and VSCode [here](https://code.visualstudio.com/download).
- *IMPORTANT NOTE*: This simulator requires an NVIDIA GPU for use.

#### Setting the Stage
- Open Anaconda Prompt and create your virtual environment. We use Python version 3.8.
  ```
  conda create --name dcl python=3.8
  conda activate dcl
  ```
#### Installing Dependencies
- Mamba library is optional, but recommended to speed up Conda runtime and installations. If you choose to not use Mamba, just run `conda` instead of   `mamba` commands.
  ```
  conda install -n base --override-channels -c conda-forge mamba 'python_abi=*=*cp*'
  ```
- Next we install Pytorch. This is downloaded separately to ensure the CUDA-enabled version, rather than the CPU-only version. 
  ```
  pip install torch -f https://download.pytorch.org/whl/torch_stable.html
  ```
- Install the rest of the dependencies. Here we use `mamba`/`conda` instead of `pip` since pip installs libraries globally rather than  locally.
  ```
  conda config --add channels conda-forge
  conda config --add channels anaconda
  mamba install --file requirements.txt
  ```
For any issues or conflicts, consult the table below FAQ for individual downloads. If needed, use pip instead.

---

## Quick Start
#### Cloning the Repository for VSCode
- Open VSCode > View > Command Palette > select Git:Clone and enter the below repository url in the searchbar,
  ```
  https://github.com/hatfield-c/dcl.git
  ```
-  Select your desired directory location and then open in VSCode. 

[Video guide](https://www.youtube.com/watch?v=ILJ4dfOL7zs&ab_channel=CodingWithMeet) for the unfamiliar. Further information on cloning directories can be found [here](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository).
### How to Run
- In the Anconda Prompt, Navigate to your new cloned directory location. Replace ```<C:\Users\directory address\>``` with the actual address on your machine.
  ```
  cd <C:\Users\directory address\>
  ```

- Edit your desired changes to CONFIG.py in VSCode/IDE of choice. 
  - There, you can edit the episode count, hitpoly and diffusion parameters, and define action flags. You can also change the scenario by changing the value of `scenario = 2`.
  - Then run ```Main.py``` with your desired specifications.
    ```
    python Main.py
    ```

#### Action Flags
- ###### Generate Data
  - First, create these empty folders for the generated data to be housed in:
    -  data/v3
    - data/models/hitpoly
    - data/render/frames
  - In CONFIG.py, activate one flag at a time, running `python Main.py` each:
    ```
    actions = "generate_data"
    ``` 
  - And then stitch the tensors by activating `stitch_data`:
    ```
    actions = "stitch_data"
    ``` 

- ###### Training Hitpoly Model
  - `train_hitpoly` trains the hitpoly model in batches. Hotpoly parameters such as epochs, leaerning rate, and batch size may be modified.
    ```
    actions = "train_hitpoly"
    ``` 
  - `query_hitpoly` loads the model output to image rendering.
    ```
    actions = "query_hitpoly"
    ``` 
  - `render_hitpoly` generates the hitpoly simulator starting from episode 1. Hold the `enter` key to progress each frame.   
    ```
    actions = "render_hitpoly"
    ``` 
  - ```build_video``` creates a `.mp4` video visualizing the change in hitpoly for the drone based on its potsition and direction:
    ```
    actions = "build_video"
    ``` 
 - For more information, ```actions = "help"``` is available.


---

## FAQ
##### Can I install the libraries individually? I'm running into some issues with installation.
Absolutely! Below is the dependencies table with all the relevant commands and information links.
- | Library     										 |  Command     					  	|
    | -------------------------------------------------- | ------------------------------------ |
    | python3.8  | |	
    | [pip](https://pip.pypa.io/en/stable/)         														| ``` mamba install pip ``` |
    | [mamba*](https://mamba.readthedocs.io/en/latest/installation/mamba-installation.html)      					| ``` conda install -n base --override-channels -c conda-forge mamba 'python_abi=*=*cp*' ``` |
    | [torch](https://pytorch.org/docs/stable/index.html)	      									| ``` pip install torch -f https://download.pytorch.org/whl/torch_stable.htmll ```	|
    | [opencv](https://docs.opencv.org/4.x/)      											| ``` mamba install opencv ```				|					|
    | [matplotlib](https://matplotlib.org/stable/index.html) 									| ``` mamba install matplotlib ```				|
    | [pybullet](https://docs.google.com/document/d/10sXEhzFRSnvFcl3XxNGhnD4N2SedqwdAvK3dsihxVUA/edit#heading=h.2ye70wns7io3)    	| ``` mamba install -c conda-forge pybullet ``` 	|
    | [pynput](https://pynput.readthedocs.io/en/latest/) 										| ``` mamba install conda-forge::pynput ```			|
    | [einops](https://einops.rocks/#Installation) 											| ``` mamba install conda-forge::einops ```			|
    | [gstreamer](https://gstreamer.freedesktop.org/documentation/tutorials/index.html?gi-language=c)                                                         | ```mamba install anaconda::gstreamer``` |

##### Do I need Mamba? I've never seen this library before.
If this is your first time installing Mamba, you may choose to not install it and instead stick with Conda commands instead. Mamba may take some time to install, so if you'd like to jump in ASAP, you can choose to forego it.

##### Why am I getting a "Torch not compiled with CUDA enabled" error?
You may have a CPU-only Pytorch version previously installed. In that event, installing a new Pytorch would not fix the issue as it continues to use the cached CPU-only version -- you will need to uninstall and reinstall.
  ```
    pip uninstall torch
    pip cache purge
    pip install torch -f https://download.pytorch.org/whl/torch_stable.html
  ```
##### It says a GPU is required. Can I run this without a GPU?
No. If you were to attempt to run the simulator anyway, you would receive a runtime error. A dedicated GPU is necessary for the high loads of data and processing.




---