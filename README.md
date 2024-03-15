# Roblox Large Language Model API
Talk with local large language model in Roblox game
![Screenshot 2024-03-14 140308](https://github.com/pixol20/Roblox-LLM-API/assets/115364463/88070a7e-6627-4378-bf44-ef37c9f3a725)
## Installation
1) clone or download repo
2) in cmd change directory to repository
3) `python -m venv ./venv`
4) `.\venv\Scripts\activate.bat`
5) `pip install -r requirements.txt`
6) `python ./src/serve.py`
7) First time this will download [mistralai/Mistral-7B-Instruct-v0.2](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2) model. In src/config.py in "pretrained_model_name_or_path" you can specify either the name of the Hugging Face model or the folder where the model was manually downloaded.
8) Once it's loaded/downloaded you will see "Model loaded" "Starting server". The server will be on `127.0.0.1:8080`. You can change address and port in src/config. **THE SERVER IS STILL IN DEVELOPMENT SO IT'S NOT 100% SAFE**
9) From here you will need tool like [ngrok](https://ngrok.com/) or port forwarding to make this accessible on WAN. 
## Roblox integration
1) Open ExampleGame.rbxl that you downloaded where everything is set up except for server URL.
2) In workspace open "Pepe" model and open "APIScript"
3) Replace AppUrl with your URL
4) DONE! You can also change LogSize and AnswerEverynMessages(variable used to control how often will AI talk).
