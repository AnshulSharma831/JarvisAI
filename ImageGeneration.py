import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import get_key
import os
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Function to open generated images (return paths for GUI)
def open_image(prompt):
    folder_path = "Data"
    prompt = prompt.replace(" ", "_")
    files = [f"{prompt}{i}.jpg" for i in range(1, 5)]
    image_paths = []

    for jpg_file in files:
        image_path = os.path.join(folder_path, jpg_file)
        if os.path.exists(image_path):
            image_paths.append(image_path)
            logger.info(f"Found image: {image_path}")
        else:
            logger.warning(f"Image not found: {image_path}")

    return image_paths

# Hugging Face API configuration
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
huggingface_api_key = get_key('.env', 'HuggingFaceAPIKey')
if not huggingface_api_key:
    logger.error("HuggingFaceAPIKey not found in .env file.")
    raise ValueError("HuggingFaceAPIKey not found in .env file.")
headers = {"Authorization": f"Bearer {huggingface_api_key}"}

# Asynchronous function to query the Hugging Face API with retry on rate limits
async def query(payload, retries=3, backoff=5):
    for attempt in range(retries):
        try:
            logger.info(f"Sending request to Hugging Face API with payload: {payload}")
            response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
            response.raise_for_status()
            logger.info(f"API request successful, received {len(response.content)} bytes.")
            return response.content
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Rate limit exceeded
                logger.warning(f"Rate limit exceeded, retrying in {backoff} seconds (attempt {attempt + 1}/{retries})")
                await asyncio.sleep(backoff)
                backoff *= 2  # Exponential backoff
                continue
            logger.error(f"API request failed: {e}")
            if e.response:
                logger.error(f"Status Code: {e.response.status_code}")
                logger.error(f"Response Text: {e.response.text}")
            return None, str(e)
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None, str(e)
    logger.error("Max retries reached for API request.")
    return None, "Max retries reached due to rate limit."

# Asynchronous function to generate images
async def generate_images(prompt: str):
    tasks = []
    errors = []

    for _ in range(4):
        payload = {
            "inputs": f"{prompt}, quality=4k, sharpness=maximum, Ultra High details, high resolution, seed={randint(0, 1000000)}",
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)

    results = await asyncio.gather(*tasks)

    # Ensure the Data directory exists
    try:
        os.makedirs("Data", exist_ok=True)
    except Exception as e:
        logger.error(f"Failed to create Data directory: {e}")
        return False, str(e)

    # Count the number of successfully generated images
    success_count = 0
    prompt_cleaned = prompt.replace(" ", "_")

    for i, result in enumerate(results):
        image_bytes, error = result
        if image_bytes:
            image_path = os.path.join("Data", f"{prompt_cleaned}{i + 1}.jpg")
            try:
                with open(image_path, "wb") as f:
                    f.write(image_bytes)
                logger.info(f"Successfully saved image: {image_path}")
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to save image {image_path}: {e}")
                errors.append(f"Failed to save image {i + 1}: {str(e)}")
        else:
            logger.warning(f"Image {i + 1} failed to generate (no bytes received).")
            errors.append(f"Image {i + 1} failed: {error}")

    logger.info(f"Generated {success_count} images successfully.")
    return success_count > 0, "; ".join(errors) if errors else "No errors"

# Function to generate images (return success status, paths, and error message)
def GenerateImages(prompt: str):
    try:
        success, error_msg = asyncio.run(generate_images(prompt))
        if success:
            image_paths = open_image(prompt)
            return True, image_paths, "Images generated successfully."
        else:
            return False, [], f"Failed to generate images: {error_msg}"
    except Exception as e:
        logger.error(f"Error in GenerateImages: {e}")
        return False, [], f"Error in GenerateImages: {str(e)}"

# Main loop to monitor the ImagesGeneration.data file (not used in GUI)
def main():
    while True:
        try:
            file_path = os.path.join("Frontend", "Files", "ImagesGeneration.data")
            with open(file_path, "r") as f:
                data: str = f.read().strip()

            prompt, status = data.split(",")

            if status == "True":
                logger.info("Generating Images...")
                success, image_paths, error_msg = GenerateImages(prompt)
                logger.info(f"Result: Success={success}, Paths={image_paths}, Error={error_msg}")

                # Update the status in the file
                with open(file_path, "w") as f:
                    f.write("False,False")
                break
            else:
                time.sleep(1)
        except Exception as e:
            logger.error(f"Error: {e}")
            break

if __name__ == "__main__":
    prompt = "A futuristic city"
    success, paths, error_msg = GenerateImages(prompt)
    print(f"Success: {success}, Paths: {paths}, Error: {error_msg}")