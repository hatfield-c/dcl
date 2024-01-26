# [DCL] Drone Combat Lab
The repository for the UT Dallas Drone Combat Lab.
The DCL is built on top of the PyBullet engine, and serves as a testing environment for cheaply and quickly prototyping combat strategies for drone-on-drone warfare. The DCL also offers benchmarks for AI drone controllers in various tasks.

<!--
demo gifs go here
[[AeroMedLab]](https://www.aeromedlab.com/)
-->

---

## Installation
We use [Anaconda](https://docs.anaconda.com/free/anaconda/getting-started/index.html) CLI for running and package management. This simulator requires a GPU for use.

### Dependencies Quick Guide
| Library     										 |  Command     					  	|
| -------------------------------------------------- | ------------------------------------ |
| python 3.8  | |	
| [pip](https://pip.pypa.io/en/stable/)         														| ``` mamba install pip ``` |
| [mamba*](https://mamba.readthedocs.io/en/latest/installation/mamba-installation.html)      					| ``` conda install -n base --override-channels -c conda-forge mamba 'python_abi=*=*cp*' ``` |
| [pybullet](https://docs.google.com/document/d/10sXEhzFRSnvFcl3XxNGhnD4N2SedqwdAvK3dsihxVUA/edit#heading=h.2ye70wns7io3)    	| ``` mamba install -c conda-forge pybullet ``` 	|
| [opencv](https://docs.opencv.org/4.x/)      											| ``` mamba install opencv ```				|					|
| [torch](https://pytorch.org/docs/stable/index.html)	      									| ``` mamba install pytorch torchvision torchaudio -c pytorch ```	|
| [matplotlib](https://matplotlib.org/stable/index.html) 									| ``` mamba install matplotlib ```				|
| [einops](https://einops.rocks/#Installation) 											| ``` mamba install conda-forge::einops ```			|
| [pynput](https://pynput.readthedocs.io/en/latest/) 										| ``` mamba install conda-forge::pynput ```			|
* *Mamba library is optional, but recommended to speed up Conda runtime. If you choose to not use Mamba, just run `conda` instead of `mamba` commands.

---

## Documentation

---

## FAQ

---