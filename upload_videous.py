import os
import shutil

from youtube import upload_video


def upload_videos(directory, uploaded_videos_directory):
    for entry in os.listdir(directory):
        full_path = os.path.join(directory, entry)
        if os.path.isfile(full_path):
            print("File:", full_path)
            try:
                upload_video(full_path, entry)

                # If upload is successful, delete the file and move it
                os.remove(full_path)
                print("File removed successfully.")
                move_path = os.path.join(uploaded_videos_directory, entry)
                shutil.move(full_path, move_path)
                print("File moved successfully to:", move_path)

            except Exception as e:
                if "quotaExceeded" in str(e) or "uploadLimitExceeded" in str(e):
                    print("Quota exceeded. Skipping this file.")
                else:
                    raise  # Raise the exception if it's not a quota error

        elif os.path.isdir(full_path):
            print("Directory:", full_path)
            upload_videos(full_path, uploaded_videos_directory)  # Recursively call the function for subdirectories


# Start uploading videos from the 'videos' directory
upload_videos('videos', 'uploaded_videos')
