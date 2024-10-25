from waitress import serve
from config import config
import app

#Remove TextGeneration

# import TextGeneration
# TextGeneration.LoadModel()

print("Model loaded")
print("Starting server")
serve(**config["Server"], app=app.app)