import tempfile
import numpy as np
import pyrebase
import requests
from io import BytesIO
from PIL import Image
from starlette.responses import FileResponse

config = {
    "apiKey": "AIzaSyDGNO1_nxBds_3BEU1b5N0WqVW3IsKvkZ0",
    "authDomain": "conigcare.firebaseapp.com",
    "projectId": "conigcare",
    "storageBucket": "conigcare.appspot.com",
    "messagingSenderId": "745722589326",
    "appId": "1:745722589326:web:a84e397f7598219ea799df",
    "serviceAccount": "serviceAccount.json",
    "databaseURL": "https://conigcare-default-rtdb.firebaseio.com/"
}


firebase = pyrebase.initialize_app(config)
storage = firebase.storage()


def get_image_url(number):
    # Function to fetch image URL based on number
    image_path = f"{number}.jpg"
    return storage.child(image_path).get_url(None)


def letter_to_number(letter):
    # Convert letters to numeric values
    if letter.isalpha():
        letter = letter.upper()
        return ord(letter) - ord('A') + 1
    else:
        return 0


def tokenize_sentence(sentence):
    # Tokenize the sentence
    tokens = [letter_to_number(letter) for letter in sentence]
    return tokens


def fetch_images(result):
    frames = []
    sizes = set()
    for number in result:
        image_url = get_image_url(number)
        print(image_url)
        response = requests.get(image_url)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            frames.append(np.array(img))
            sizes.add(img.size)

    # Check if all images have the same size
    if len(sizes) > 1:
        min_width = min(s[0] for s in sizes)
        min_height = min(s[1] for s in sizes)
        frames = [np.array(Image.fromarray(frame).resize((min_width, min_height))) for frame in frames]

    return frames

# Get user input and tokenize the sentence
def process_word(name:str):
    input_sentence = name
    result = tokenize_sentence(input_sentence)


    # Fetch frames
    frames = fetch_images(result)

    if len(frames) > 0:
        # Repeat the first frame a few times at the beginning for a smooth start
        repetitions = 5  # Adjust the number of repetitions as needed
        initial_frames = [frames[0]] * repetitions
        frames = initial_frames + frames

        # Convert NumPy arrays back to PIL Images
        frames = [Image.fromarray(frame) for frame in frames]

        # # Save frames as a GIF
        # output_path_gif = 'output_animation.gif'
        # output_gif = BytesIO()
        # frames[0].save(output_path_gif, save_all=True, append_images=frames[1:], duration=500, loop=0)  # Adjust duration as needed
        # output_gif.seek(0)  # Reset the pointer
        with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as temp_gif:
            frames[0].save(temp_gif, format='GIF', save_all=True, append_images=frames[1:], duration=500,
                           loop=0)  # Adjust duration as needed
            temp_gif_path = temp_gif.name





    print(f"Animation created and saved as a GIF")
    print("Tokenized values:", result)
    return FileResponse(temp_gif_path, media_type="image/gif")


