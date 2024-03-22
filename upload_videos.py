import asyncio
import os
import shutil

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv, find_dotenv

from youtube import upload_video

load_dotenv(find_dotenv())

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher()

quota_exceeded = False  # Variable to track if the quota has been exceeded


async def send_message(message):
    await bot.send_message(chat_id=os.getenv('ADMIN'), text=message)


class QuotaExceededError(Exception):
    pass


async def upload_videos(directory, uploaded_videos_directory):
    global quota_exceeded  # Access the global variable
    retry_count = int(os.getenv('RETRY_COUNT'))  # Number of retry attempts
    for entry in os.listdir(directory):
        if quota_exceeded:  # Check if quota is exceeded before processing more files
            await send_message("Quota exceeded. Stopping upload.")
            raise QuotaExceededError("Quota exceeded. Stopping upload.")
        full_path = os.path.join(directory, entry)
        if os.path.isfile(full_path):
            print("File:", full_path)
            for _ in range(retry_count + 1):  # Retry the upload for the specified number of times
                try:
                    await upload_video(full_path, entry)

                    # If upload is successful, move the file
                    move_path = os.path.join(uploaded_videos_directory, entry)
                    shutil.move(full_path, move_path)
                    print("File moved successfully to:", move_path)

                    # Send message to the bot that the video is uploaded
                    await send_message(f"Video '{entry}' uploaded successfully!")

                    try:
                        # Now that upload is successful, remove the file
                        os.remove(move_path)  # Use move_path instead of full_path
                        print("File removed successfully.")
                    except OSError as e:
                        print(f"Error occurred while removing file: {e}")

                    break  # Break the loop if upload is successful

                except Exception as e:
                    if "quotaExceeded" in str(e) or "uploadLimitExceeded" in str(e):
                        print("Quota exceeded. Skipping this file.")
                        quota_exceeded = True  # Set quota_exceeded to True
                        break  # Break the loop if quota exceeded
                    elif retry_count == 0:
                        print(f"Error occurred: {e}. Maximum retry attempts reached.")
                        # Send message to the bot about the error
                        await send_message(f"Error occurred while uploading video '{entry}': {e}. "
                                           f"Maximum retry attempts reached.")
                        break  # Break the loop if maximum retry attempts reached
                    else:
                        print(f"Error occurred: {e}. Retrying...")
                        # Send message to the bot about the error
                        await send_message(f"Error occurred while uploading video '{entry}': {e}. Retrying...")

                        # Wait for a short period before retrying
                        await asyncio.sleep(5)  # Adjust the delay time as needed

        elif os.path.isdir(full_path):
            print("Directory:", full_path)
            await upload_videos(full_path, uploaded_videos_directory)  # Recursively call the function for subdirectories


async def upload_videos_periodic():
    while True:
        await upload_videos(os.getenv("VIDEOS"), os.getenv("UPLOADED_VIDEOS"))
        await asyncio.sleep(float(os.getenv("UPLOAD_FREQUENCY")) * 60)  # Upload videos every hour (3600 seconds)


async def on_startup(bot):
    print("Bot started. Uploading videos...")
    await asyncio.create_task(upload_videos_periodic())  # Start the periodic task


async def main():
    dp.startup.register(on_startup)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
