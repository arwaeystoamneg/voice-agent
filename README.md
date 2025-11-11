# voice agent

to run
1. pip install requirements.txt
2. python run_agent.py

architecture 
1. agent processes user audio
2. transcribes input audio to text
3. converts text to action plan based on predetermined actions
4. executes the plan

limitations:
* only handles user instructions according to predefined voice action mapping
* no caching mechanism for actions asked before
* limitations on the length of the audio supported
* only logging limited information of the user requests
