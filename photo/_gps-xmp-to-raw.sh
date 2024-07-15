#!/bin/bash

# Get the current folder path
folder_path=$(pwd)

# Check if there are any RAW files in the folder
shopt -s nullglob
raw_files=("$folder_path"/*.NEF)

if [ ${#raw_files[@]} -eq 0 ]; then
    echo "No RAW files found in the folder."
    exit 1
fi

# Loop through each RAW file in the folder
for raw_file in "${raw_files[@]}"; do
    # Get the corresponding sidecar XMP file
    sidecar_file="${raw_file%.NEF}.xmp"

    # Check if the sidecar XMP file exists
    if [ -f "$sidecar_file" ]; then
        # Copy GPS coordinates from sidecar XMP to RAW file
        exiftool -tagsfromfile "$sidecar_file" -GPSLatitude -GPSLatitudeRef=N -GPSLongitude -GPSLongitudeRef=W -overwrite_original -ext nef "$raw_file"

        # Remove the sidecar XMP file
        rm "$sidecar_file"
    else
        echo "Sidecar file for $raw_file does not exist."
    fi
done
