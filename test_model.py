from transformers import pipeline
import numpy as np
from PIL import Image

# create a dummy image
img = Image.fromarray(np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8))
img.save("test.jpg")

p = pipeline("image-classification", model="dima806/deepfake_vs_real_image_detection")
result = p("test.jpg")
print("RAW OUTPUT:")
print(result)
