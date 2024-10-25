## Game Arena Roblox API
1) clone or download repo
2) in cmd change directory to repository
3) `python -m venv env`
4) `source env/bin/activate` for MacOS/Linux. `env\Scripts\activate` for Windows.
5) `pip install -r requirements.txt`
6) `python ./src/serve.py` You might need to do something like this (due to import error): `export PYTHONPATH="/Users/USER/Documents/Roblox-LLM-API:$PYTHONPATH"`
7) Update `config.py` with OPENAI_API_KEY. The `config.py` file is in our slack group chat. 
8) Use [ngrok](https://ngrok.com/) to perform port forwarding to make this accessible on WAN. 
Run the command: `ngrok http 8000`
