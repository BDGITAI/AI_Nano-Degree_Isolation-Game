# AI_Nano-Degree_Isolation-Game

## 0. Project Details  

### Description

This project aims at building a game playing agent using adversarial method.

It consists in implementing the Minimax algorithm with beta pruning and iterative deepening search.

In this project we also define some custom heuristics and analyse how they perform over a series of game.
  
### Isolation Game  

The isolation game is a board game with two opponents. 

Rules can be found [here](https://en.wikipedia.org/wiki/Isolation_(board_game))

An Udacity video is also available :[Isolation explained](https://youtu.be/BYqGXP95QLc)
  
## 1. Getting Started  
  
### Preamble  

This project was developed on a **Windows 64 bits** .

On windows one of the easiest way to install python and other required librairies can be achieved by installating [Anaconda](https://www.anaconda.com/download/)

Anaconda installation procedure is available [here](http://docs.anaconda.com/anaconda/install/windows/)

### Installing

Base installation from Anaconda is sufficient for this project.

Should you wish to manage this project in its own virtual environment you can refer to [managing conda environment](https://conda.io/docs/user-guide/tasks/manage-environments.html)

### Base files 

This project was developped using some starter code provided by Udacity.
Source can be found [here](https://github.com/udacity/AIND-Isolation)

## 2. Run the project  
 
### Structure

The project contains several files. Main files for this project are

* game_agent.py : file where the minimax and heuristics are being implemented

* tournament.py : file used to evaluate the agent and containing the main function

### Execution

To launch the program through command line

`python tournament.py`

