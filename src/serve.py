from waitress import serve
from config import config
import app
import TextGeneration
TextGeneration.LoadModel()
print("Model loaded")
serve(**config["Server"], app=app.app)