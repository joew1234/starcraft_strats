## Starcraft Strategies


#### Description

This is my capstone project for the end of my data science immersive program at Galvanize. I want to cluster player actions in a game of Starcraft into distinct strategies. I can then analyze the strategies by looking at win rates, effect on game length and strategy combinations (which strategies are used together?). I have scoped the project to the first 10 minutes of each game as I believe that this early part of the game can be easily summarized by what kinds and how many of each unit are built. Later in the game, positioning and interactions between the players become much more important and are not as easily captured. For reference, I found the average game length to be 15 minutes.

Brief description of what Starcraft is:
Starcraft is a real time strategy computer game simulating war between two players. Players build units and buildings and attempt to destroy all of their opponent's buildings. Before a game can start, each player chooses a race- Zerg, Terran, or Protoss that each have unique units and playstyles.


#### Motivation
I have loved the Starcraft franchise since I was young. I came across the stardata dataset (https://github.com/TorchCraft/StarData) on gitlogs while looking for a capstone project and knew I had to do something with it. The dataset itself had 50,000 full game replays. The size of that dataset should be both an interesting challenge and useful for machine learning.

#### Data:
The dataset and description is provided here:
https://github.com/TorchCraft/StarData

###### Description of Dataset:
-50,000 game replay files  
-Full state information split into frames, with 8 frames captured per second. With an average game length of 15 minutes, this means that there are 50,000 games * 15 minutes * 60 seconds/minutes * 8 frames/second = 360,000,000 or 360 million frames in total!  
-Total file size was 500 gigabytes when uncompressed.  
-Each frame has full state information about the map, units and building of each player  
Python library pytorch was included with the data which can extract information from the replay files.  

###### Data Pipeline:
-In my src/scpipeline.py module, I have a SCPipeline class that takes a single replay file as input. This class then stores all general state information like race of each player and winner of the game.  
-Note that the games do not have winner stored in them so I had to create an algorithm to determine the winner. The winner is determined first by if one player has run out of buildings (the actual win condition of the game), then by which player has the most army units (if one player leaves before losing all buildings, it's probably because their inferior army size), if the army counts are tied, then the highest building count wins. Finally, if army and building counts are tied, I just called it a tie.  
-My SCPipeline class has a method, get_units_df, that keeps track of units gained from one frame to the next and totals them up for a specified amount of time (10 minutes for my analysis).  
-My src/model.py module can take an entire directory of replay files and uses SCPipeline to extract information from each and aggregates them into a pandas dataframe.  
-model.py also has the code that performs NMF to the resulting matrix  
-Finally, my src/analysis.py module extracts relevent information like matchup win rates for each strategy  

##### Potential Problems:
Some problems I encountered in both the original data set as well as while working on the project:  
-No documentation on torchcraft: The python portion of torchcraft had no documentation which led to a lot of time spent playing with and guessing at the meaning of its methods  
-My pipeline was written so that it would not keep processing if a file threw an error. Only finished processing half of all replay files  
-No winner label, I determined winner based off of my self created (reasonable) heuristic  
-My opinion determined what was the most interesting number of strategies, with reconstruction error only giving me a starting point  
-NMF was used more to be different and see if it would work than anything else. Original authors of torchcraft used k-means. Didn’t have time to do anything with soft clustering property of NMF  
-My initial round of clustering left me with strategies that were ~80% of the games for their respective races. This was not interesting so I removed them.  

#### Next Steps:
Some useful ways to extend this project:  
-Incorporate this information into an AI playing starcraft.  
-Incorporate more game state information: Location, time, map, unit destruction  
-Take advantage of soft clustering property of NMF (strategy pairs? interactions?)  
-Late game strategies  

##### Credits
Special thanks to:  
Lin, Z., G., Jonas, K., Vasil, Synnaeve, G. for creating and maintaining stardata dataset and torchcraft  
Ivan C. and Moses M., my scrum leaders  
Everyone at Galvanize, especially Cary G. and Mark L. for spending so many hours fixing technical issues  
