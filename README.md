<img src="https://img.search.brave.com/FYZv7tc4rXgB7MBBlx_5fpPs5nty8vxddZHTgHMk5Es/rs:fit:256:256:1/g:ce/aHR0cHM6Ly93d3cu/cmFzcGJlcnJ5cGku/b3JnL3dwLWNvbnRl/bnQvdXBsb2Fkcy8y/MDEyLzAxL1NwZWMt/UmFzcGJlcnJ5UGkt/R0lGLTI1Ni1UcmFu/c3AuZ2lm.gif" width="70" height="70" align="left"/> <img src="https://img.search.brave.com/EqqdMAUAljyJNtFZXbZmuPjWk-rG3eYXr5RXcvBcgfQ/rs:fit:480:320:1/g:ce/aHR0cHM6Ly9tZWRp/YS5naXBoeS5jb20v/bWVkaWEvUkRKZk9T/T2Rsbmh1L2dpcGh5/LmdpZg.gif" width="60" height="60" align="right" />

<h1 align="center">Accident Scape</h1>


Smart Accident Prevention Using Raspberry Pi 3B+, OpenCV and Dlib

<a href="https://www.canva.com/design/DAE38Dxw5-Q/view">
  
## Demo

<img src = "https://raw.githubusercontent.com/tanujdargan/accidentscape/main/icgg2022gif.gif?token=GHSAT0AAAAAABSBHTQMMWEKOTAETM2FE7K6YRSY24A" width="256" height="256" align="center">
  
<h1 align="center">First Time Raspberry Pi Setup</h1>

## If you would like to remote SSH into the RPI then do this
```
sudo apt install xrdp
hostname -I 
```
→ gives an IP Address that can be used to connect to the Raspberry Pi Remotely
## Project Setup
```
git clone https://github.com/tanujdargan/ic2022gg.git
sudo apt-get update
sudo apt-get install build-essential cmake 
sudo apt-get install libopenblas-dev liblapack-dev
sudo apt-get install libx11-dev libgtk-3-dev
sudo apt-get install python python-dev python-pip
sudo apt-get install python3 python3-dev python3-pip
pip install virtualenv
sudo pip install virtualenvwrapper
export WORKON_HOME=(directory you need to save envs)
source /usr/local/bin/virtualenvwrapper.sh -p $WORKON_HOME
mkvirtualenv icgg2022 -p python3
workon icg2022
pip install numpy
pip install dlib
pip install imutils
pip install scipy
sudo apt-get install libatlas-base-dev
pip install opencv-python==4.5.3.56
sudo apt-get install espeak
```
## Setting up virtualenv
```
sudo apt-get install python3-pip

sudo pip3 install virtualenv
sudo pip3 install virtualenvwrapper

mkdir ~/.virtualenvs

export WORKON_HOME=~/.virtualenvs

VIRTUALENVWRAPPER_PYTHON='/usr/bin/python3'

source /usr/local/bin/virtualenvwrapper.sh

mkvirtualenv venv
virtualenv venv
```
## Run Program
```
/home/pi/directory/icgg2022/bin/python3.9 /home/pi/ic2022gg/drowsiness_yawn.py
```
## To Run Script At Boot
```
sudo nano /etc/profile
```
Add to the end of the file -
```
/home/pi/directory/icgg2022/bin/python3.9 /home/pi/ic2022gg/drowsiness_yawn.py
```
## Libraries Used

* Python 3.9.2
* Dlib v19.23
* CMake
* VirtualEnvironments
* OpenCV-Python
* Espeak
* Scipy
* Numpy
* Imutils
