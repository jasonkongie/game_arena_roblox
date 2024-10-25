## Game Arena Roblox API
1) clone or download repo
2) cd to repo
3) Set up virtual env:
 `python -m venv env`
`source env/bin/activate` for MacOS/Linux. `env\Scripts\activate` for Windows.
6) `pip install -r requirements.txt`
7) `python ./src/serve.py` You might need to do something like this (due to import error): `export PYTHONPATH="/Users/USER/Documents/Roblox-LLM-API:$PYTHONPATH"`
8) Update `config.py` with OPENAI_API_KEY. The `config.py` file is in our slack group chat. 
9) Use [ngrok](https://ngrok.com/) to perform port forwarding to make this accessible on WAN. 
Run the command: `ngrok http 8000`
