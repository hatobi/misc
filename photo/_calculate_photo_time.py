import os
from PIL import Image
from PIL.ExifTags import TAGS
import datetime

def get_exif_date_taken(path):
    """Extract the date taken from an image's EXIF data."""
    image = Image.open(path)
    exif_data = image._getexif()
    if exif_data:
        for tag, value in exif_data.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "DateTimeOriginal":
                return datetime.datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
    return None

def calculate_photographing_time(folder_path, break_duration_minutes=10):
    timestamps = []
    
    # Gather all timestamps from the images in the folder
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('jpg', 'jpeg', 'png', 'nef')):
            file_path = os.path.join(folder_path, filename)
            date_taken = get_exif_date_taken(file_path)
            if date_taken:
                timestamps.append(date_taken)

    # Sort the timestamps
    timestamps.sort()
    
    if not timestamps:
        return "No valid images with EXIF timestamps found."
    
    # Calculate total photographing time excluding breaks
    total_duration = datetime.timedelta()
    previous_time = timestamps[0]
    
    for current_time in timestamps[1:]:
        duration = current_time - previous_time
        if duration.total_seconds() > break_duration_minutes * 60:
            # It's a break, so don't add this duration
            previous_time = current_time
        else:
            total_duration += duration
            previous_time = current_time
    
    return total_duration

# Folder containing images
folder_path = os.getcwd()
# Define the break duration in minutes
break_duration_minutes = 10

photographing_time = calculate_photographing_time(folder_path, break_duration_minutes)
print(f"Total time spent photographing (excluding breaks): {photographing_time}")
