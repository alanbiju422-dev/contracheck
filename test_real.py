from transformers import pipeline
import requests
from PIL import Image
from io import BytesIO

p = pipeline("image-classification", model="dima806/deepfake_vs_real_image_detection")

# let's download a known real image
url = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/React-icon.svg/256px-React-icon.svg.png"
response = requests.get(url)
img = Image.open(BytesIO(response.content)).convert("RGB")

prediction = p(img)
print("RAW OUTPUT FOR REAL IMAGE:")
print(prediction)
