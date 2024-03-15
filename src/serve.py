from waitress import serve
from config import config
import app
import TextGeneration
TextGeneration.LoadModel()
print("Model loaded")
print("Starting server")
serve(**config["Server"], app=app.app)