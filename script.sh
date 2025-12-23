#!/bin/bash

# Get the script's directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default image directory: <script_dir>/resized
IMAGE_DIR="$SCRIPT_DIR/resized"

# Supported image formats
shopt -s nullglob
images=("$IMAGE_DIR"/*.{jpg,jpeg,png,gif,bmp,webp})

# Exit if no images found
if [ ${#images[@]} -eq 0 ]; then
  echo "No images found in $IMAGE_DIR"
  exit 1
fi

# Function to display a random image
show_random_image() {
  random_image="${images[RANDOM % ${#images[@]}]}"
  kitty +kitten icat --align left "$random_image"
}

# Function to use fzf to choose and display an image
show_fzf_image() {
  selected_filename=$(printf '%s\n' "${images[@]##*/}" | fzf --prompt="Select an image: ")
  if [[ -n "$selected_filename" ]]; then
    full_path="$IMAGE_DIR/$selected_filename"
    kitty +kitten icat --align left "$full_path"
  else
    show_random_image
  fi
}

# Parse arguments
case "$1" in
--select | -f)
  show_fzf_image
  ;;
*)
  show_random_image
  ;;
esac
