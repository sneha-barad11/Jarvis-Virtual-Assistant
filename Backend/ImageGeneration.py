# import asyncio
# from random import randint
# from PIL import Image
# import requests
# from dotenv import get_key
# import os
# from time import sleep

# # Function to open and display images based on a given prompt
# def open_images(prompt):
#     folder_path = r"Data"  # Folder where the images are stored
#     prompt = prompt.replace(" ", "_")  # Replace spaces in prompt with underscores

#     # Generate the filenames for the images
#     Files = [f"{prompt}{i}.jpg" for i in range(1, 5)]

#     for jpg_file in Files:
#         image_path = os.path.join(folder_path, jpg_file)

#         try:
#             # Try to open and display the image
#             img = Image.open(image_path)
#             print(f"Opening image: {image_path}")
#             img.show()
#             sleep(1)  # Pause for 1 second before showing the next image

#         except IOError:
#             print(f"Unable to open {image_path}")

# # API details for the Hugging Face Stable Diffusion model
# API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
# headers = {"Authorization": f"Bearer {get_key('.env', 'HuggingFaceAPIKey')}"}

# # Async function to send a query to the Hugging Face API
# async def query(payload):
#     response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
#     return response.content

# # Async function to generate images based on the given prompt
# async def generate_images(prompt: str):
#     tasks = []

#     # Create 4 image generation tasks
#     for _ in range(4):
#         payload = {
#             "inputs": f"{prompt}, quality=4K, sharpness=maximum, Ultra High details, high resolution, seed = {randint(0, 1000000)}",
#         }
#         task = asyncio.create_task(query(payload))
#         tasks.append(task)

#     # Wait for all tasks to complete
#     image_bytes_list = await asyncio.gather(*tasks)

#     # Save the generated images to files
#     for i, image_bytes in enumerate(image_bytes_list):
#         with open(fr"Data\{prompt.replace(' ', '_')}{i + 1}.jpg", "wb") as f:
#             f.write(image_bytes)

# # Wrapper function to generate and open images
# def GenerateImages(prompt: str):
#     asyncio.run(generate_images(prompt))  # Run the async image generation
#     open_images(prompt)  # Open the generated images

# # Main loop to monitor for image generation requests
# while True:

#     try:
#         # Read the status and prompt from the data file
#         with open(r"Frontend\Files\ImageGeneration.data", "r") as f:
#             Data: str = f.read()

#         Prompt, Status = Data.split(",")

#         # If the status indicates an image generation request
#         if Status == "True":
#             print("Generating Images...")
#             ImageStatus = GenerateImages(prompt=Prompt)

#             # Reset the status in the file after generating images
#             with open(r"Frontend\Files\ImageGeneration.data", "w") as f:
#                 f.write("False,False")
#                 break  # Exit the loop after processing the request

#         else:
#             sleep(1)  # Wait for 1 second before checking again

#     except Exception as e:
#         print(e)
        #python Backend\ImageGeneration.py
import asyncio
from random import randint
from PIL import Image
import requests
import os
import urllib.parse
from time import sleep

# Calculate relative directory paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE_PATH = os.path.join(BASE_DIR, "Frontend", "Files", "ImageGeneration.data")
DATA_DIR = os.path.join(BASE_DIR, "Data")

def open_images(prompt):
    prompt_formatted = prompt.replace(" ", "_")
    files = [f"{prompt_formatted}{i}.jpg" for i in range(1, 5)]

    for jpg_file in files:
        image_path = os.path.join(DATA_DIR, jpg_file)
        try:
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)
        except IOError:
            print(f"Unable to open {image_path}")

async def query(prompt_text):
    # Free active cloud engine replacement for deprecated Hugging Face domain
    encoded = urllib.parse.quote(prompt_text)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&nologo=true"
    response = await asyncio.to_thread(requests.get, url, timeout=30)
    if response.status_code == 200:
        return response.content
    return None

async def generate_images(prompt: str):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    tasks = []
    print(f"Generating 4 image variations for: '{prompt}'...")
    for i in range(4):
        variant_prompt = f"{prompt}, seed={randint(1, 999999)}"
        tasks.append(asyncio.create_task(query(variant_prompt)))

    image_bytes_list = await asyncio.gather(*tasks)

    prompt_formatted = prompt.replace(" ", "_")
    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes:
            file_path = os.path.join(DATA_DIR, f"{prompt_formatted}{i + 1}.jpg")
            with open(file_path, "wb") as f:
                f.write(image_bytes)
            print(f"Saved: {file_path}")

def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))
    open_images(prompt)

while True:
    try:
        if os.path.exists(DATA_FILE_PATH):
            with open(DATA_FILE_PATH, "r") as f:
                content = f.read().strip()

            if "," in content:
                parts = content.split(",")
                Prompt = parts[0].strip()
                Status = parts[1].strip()

                if Status.lower() == "true":
                    print(f"\n[Jarvis]: Generating images for prompt: '{Prompt}'...")
                    GenerateImages(prompt=Prompt)

                    # Reset file status after generation
                    with open(DATA_FILE_PATH, "w") as f:
                        f.write("False,False")
                    print("[Jarvis]: Image generation complete. Reset status.")
                    break

        sleep(1)

    except Exception as e:
        print(f"[Error]: {e}")
        sleep(1)