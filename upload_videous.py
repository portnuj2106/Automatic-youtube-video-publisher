import os

import time

from youtube import upload_video




def upload_videos(directory):
    for entry in os.listdir(directory):
        full_path = os.path.join(directory, entry)
        if os.path.isfile(full_path):
            print("File:", full_path)
            try:
                upload_video(full_path, entry)
            except Exception as e:
                if "quotaExceeded" in str(e):
                    print("Quota exceeded. Retrying after some time...")
                    time.sleep(60)  # Wait for a minute before retrying
                    upload_video(full_path, entry)
                else:
                    raise  # Raise the exception if it's not a quota error

        elif os.path.isdir(full_path):
            print("Directory:", full_path)
            upload_videos(full_path)  # Recursively call the function for subdirectories


# Start uploading videos from the 'videos' directory
upload_videos('videos')
