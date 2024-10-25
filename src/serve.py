# from waitress import serve
# from config import config
# import app

# #Remove TextGeneration

# # import TextGeneration
# # TextGeneration.LoadModel()

# print("Model loaded")
# print("Starting server")
# serve(**config["Server"], app=app.app)

# serve.py

import uvicorn
import app

print("Starting server")

if __name__ == '__main__':
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)