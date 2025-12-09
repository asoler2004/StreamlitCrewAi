import os
from instagrapi import Client
from datetime import datetime, timedelta
import schedule
import time
from pathlib import Path
from PIL import Image
from dotenv import load_dotenv
# import logging

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger()


def login_user():
    load_dotenv()
    USERNAME = os.getenv('INSTAGRAM_USERNAME')
    PASSWORD = os.getenv('INSTAGRAM_PASSWORD')
    cl = Client()
    cl.login(USERNAME, PASSWORD)
    print("Successfully logged in")
    # logger.info("Successfully logged in")
    return cl

def post_image(cl, image_path, caption):
    print("entrando a post_image...")
    headers = {'User-Agent':'Instagram 76.0.0.15.395 Android (24/7.0; 640dpi; 1440x2560; samsung; SM-G930F; herolte; samsungexynos8890; en_US; 138226743)'} 
    cl.photo_upload(path=image_path, caption=caption)
    print(f"Posted image: {image_path}")    
    # logger.info(f"Posted image: {image_path}")    


def generate_daily_schedule(story_data, start_time):
    images = os.listdir(image_folder)
    schedule_times = []
    current_time = start_time
    for _ in images:
        schedule_times.append(current_time.strftime("%H:%M"))
        current_time += timedelta(minutes=60)  # Post every hour
        if current_time.day != start_time.day:
            break
    return schedule_times

def schedule_and_post():
    cl = login_user()
    image_folder = 'images'
    images = os.listdir(image_folder)
    if images:
        image = images[0]
        caption = os.path.splitext(image)[0] + "\n #midjourney #aiart #promptengineering #chaos #midjourneychaos"
        image_path = os.path.join(image_folder, image)
        post_image(cl, image_path, caption)
        os.remove(image_path)
        # logger.info(f"Posted and removed image: {image_path}")
        return True
    else:
        # logger.info("No images left to post")
        return False

def main():
    print("Hello from instagramApi!")
    start_time = datetime.now() + timedelta(minutes=1)
    image_folder = 'images'
    images = os.listdir(image_folder)
    daily_schedule = generate_daily_schedule(image_folder, start_time)
    images_to_post = len(images)

    for post_time in daily_schedule:
        schedule.every().day.at(post_time).do(schedule_and_post)

    print(f"Scheduled {len(daily_schedule)} posts starting at: {daily_schedule[0]}")
    print(f"Full schedule: {', '.join(daily_schedule)}")

    
    # logger.info(f"Scheduled {len(daily_schedule)} posts starting at: {daily_schedule[0]}")
    # logger.info(f"Full schedule: {', '.join(daily_schedule)}")

    while images_to_post > 0:
        schedule.run_pending()
        time.sleep(1)
        if not os.listdir(image_folder):
            images_to_post = 0

    # logger.info("All images have been posted. Script is ending.")
    print("La historia fue publicada.")

if __name__ == "__main__":
    main()
