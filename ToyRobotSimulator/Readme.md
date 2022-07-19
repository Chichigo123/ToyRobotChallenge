#Toy Robot Coding Challenge

##Installation

#### 1.) Install python 3.10.5 or any latest python version from https://www.python.org/downloads/
#### 2.) Open windows powershell
#### 3.) Create virtual environment via venv 
     python -m venv python_env
#### 4.) Activate virtual environment python_env
    .\python_env\Scripts\activate
#### 5.) Install the dependencies
     cd ToyRobotChallenge/ToyRobotSimulator 
     pip install -r requirements.txt


##Run the Simulator
#### After installing the dependecies, run the simulation:
     cd ToyRobotChallenge/ToyRobotSimulator/toyrobotsimulator
     python manage.py run_simulator --help
     python manage.py run_simulator


##Run the Tests
     cd ToyRobotChallenge/ToyRobotSimulator/toyrobotsimulator
     python manage.py test
