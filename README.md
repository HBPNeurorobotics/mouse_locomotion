# Mouse Locomotion Simulation
This repository gathered 3D musculoskeletal models and python scripts for legged locomotion driven by neural networks.

This program has been tested with Ubuntu since version 14.04 LTS with x64 processor architecture. Windows and Mac compatibility are not provided.
This project is working with Python 2.7, compatibility with Python 3.5 is not yet be provided.
Only one 3D simulator is currently implemented, *Blender* (version 2.77). *Gazebo*, *SOFA*, *Webots* and *Opensim* compatibility are under discussion.

## Contains

### Sources

The simulations are run with the files in the bin folder (see section Installation). 

- Musculoskeletals:
It contains the muscles and the sensors classes for the musculoskeletal model. The Body class is calling them to create the legs and the sensors for feedback.
- Optimizations:
This package implements optimization and meta-optimization algorithms to find a good connection matrix between the different models.
- Oscillators:
The spinal cord code is located in this folder. We will probably use *Nest* to replace our current models of neurons.
- Simulations:
It provides client and server program to distribute the simulation between the different machines connected.
- Simulators:
Inside it, you will find all the classes to exchange with the 3D simulators implemented.
- Utils:
This folder contains all the utility classes used during simulation.

### Configuration files
The configs folder contains json files that are linked to a musculoskeletal model and are used to configure its muscles and the spinal cord parameters.
You can also specify in here some simulation parameters such as its duration, its exit condition etc.

### Models
The mdl folder has all the musculoskeletal models which are opened by the 3D simulator. You can edit their geometry, mass, visual properties, etc. or add your own models in here. 

## Installation

### Prepare the environment
You should get sudo access to run the following commands:
```
sudo apt-get update
sudo apt-get install -y python-dev python-pip make git wget gcc pkg-config python-virtualenv libpython2.7-stdlib libfreetype6-dev libglu1-mesa libxi6
```

### Download:

- Clone the project on Github:
```
git clone  https://github.com/HBPNeurorobotics/mouse_locomotion.git
```

### Dependency Installation
This repository requires Python libraries to run. A list of these libraries and their version could be find on *requirements.txt*.
The common Makefile will automatically create a Python virtual environment with all the dependencies.
```
cd mouse_locomotion
make devinstall
```
This simulator uses features available in Blender 2.77 version.
Simulators can be installed separately in the *dist* folder thanks to the *Makefile* inside *src.simulators.SIMULATOR_NAME* package.
```
make install_SIMULATOR_NAME
```
Or you can do the complete installation, with the common *Makefile*:
```
make install_all
```

## Execution

You can launch simulations using the python files and the shell scripts inside the bin folder.
Before starting any simulation you should start the Python virtual environment:
```
source dist/venv/bin/activate
```

 - Start a registry server. He will be used both by the client to be acknowledged of the cloud state (shell 1):
```
python registry
```
 - Start a service server to process requests. The following daemon can be used to start a XVFB server (to redirect the simulation display):
```
python server
``` 
Notice that the number of parallel simulations that your server can run is linked to the CPU and Memory usage that one simulation is requesting.
Therefore, the server will run a simulation test before being available to the client side. You can set the max CPU and Memory usage with the *-cpu* and *-mem* flags.

 - Start simulation on the client side:
```
python client -m model.blend -c MyConfig -t SimulationType
```

All the parameters for simulations are described with:
```
python registry -h
python server -h
python client -h
```

Stop the virtual environment:
```
deactivate
```

Note that the logs of your simulations will be saved in *~/.log/locomotionSim.log*. You can change the logs' level with the *--verbose* flag.

## Cloud Simulation on Elis network

This section has been written to work on a specific intranet network. Refactoring is needed (especially for bash scripts) in order to work on different network.

### Bashrc Installation

A custom .bashrc file referencing all variables can be installed on all computers of the network with the script:
 
```
cd mouse_locomotion
./sh/install_remote_bash.sh
```

### Installation

The following script download and install this repository as well as all dependencies on remote computers:
 
```
./install_packages.sh
```

### Execution

See section Installation.Execution.
