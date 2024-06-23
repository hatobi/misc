import os
import subprocess
import datetime
import sqlite3

def get_exif_date_taken(file_path):
    """Extract the date taken from an image's EXIF data using exiftool."""
    result = subprocess.run(['exiftool', '-DateTimeOriginal', '-s3', file_path], stdout=subprocess.PIPE, text=True)
    date_taken_str = result.stdout.strip()
    if date_taken_str:
        return datetime.datetime.strptime(date_taken_str, '%Y:%m:%d %H:%M:%S')
    return None

def initialize_database(db_path):
    """Create a SQLite database to store image timestamps if it doesn't exist."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS image_timestamps (
                        filename TEXT PRIMARY KEY,
                        timestamp TEXT
                      )''')
    conn.commit()
    conn.close()

def populate_database(folder_path, db_path):
    """Populate the database with image timestamps if not already present."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    files = [f for f in os.listdir(folder_path) if f.lower().endswith(('nef', 'jpg', 'jpeg', 'png'))]
    total_files = len(files)
    
    for i, filename in enumerate(files):
        cursor.execute("SELECT timestamp FROM image_timestamps WHERE filename = ?", (filename,))
        result = cursor.fetchone()
        if result is None:
            print(f"Processing image {i + 1} of {total_files}")
            file_path = os.path.join(folder_path, filename)
            date_taken = get_exif_date_taken(file_path)
            if date_taken:
                cursor.execute("INSERT INTO image_timestamps (filename, timestamp) VALUES (?, ?)",
                               (filename, date_taken.strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()

def load_timestamps_from_database(db_path):
    """Load image timestamps from the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp FROM image_timestamps")
    rows = cursor.fetchall()
    timestamps = [datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S') for row in rows]
    conn.close()
    return timestamps

def calculate_photographing_time(timestamps, break_duration_minutes=10):
    """Calculate the total photographing time excluding breaks."""
    if not timestamps:
        return "No valid images with EXIF timestamps found."
    
    # Sort the timestamps
    timestamps.sort()
    
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

# Use the current directory as the folder path
folder_path = os.getcwd()
db_path = os.path.join(folder_path, 'image_timestamps.db')

# Initialize and populate the database if necessary
initialize_database(db_path)
populate_database(folder_path, db_path)

# Load timestamps from the database
timestamps = load_timestamps_from_database(db_path)

# Ask the user for the break duration in minutes
while True:
    try:
        break_duration_minutes = int(input("Enter the break duration in minutes: "))
        if break_duration_minutes < 0:
            print("Please enter a positive number.")
        else:
            break
    except ValueError:
        print("Invalid input. Please enter a number.")

# Calculate the photographing time
photographing_time = calculate_photographing_time(timestamps, break_duration_minutes)
print(f"Total time spent photographing (excluding breaks): {photographing_time}")
