<h1 align="center">Dream-of</h1>

<p align="center">
  <strong>An app for converting speech to image using AI-powered speech-to-text-to-image generation.</strong>
</p>

## Overview

Dream-of is a script that converts speech input into image prompts using AI-powered text-to-image generation. It allows you to generate creative and visually appealing images based on the prompts you provide through speech. This project aims to make the process of generating image prompts easy and interactive.

A cool use case-

Deploy on an art-frame-like monitor with an input device that triggers "listening" (keyboard, flic button, etc.).

Super minimalistic interface for distraction-free dreaming..

## Features

- **Minimalistic Interface**: App operates in a minimalistic full-screen black window.
- **Speech to Prompt to Image**: App converts speech to text prompt, then generates an image.
- **Punctuation Handling**: Any time you say "dream of" a comma will insert into the prompt- giving prompter more control of composition.
- **Select SD Model**: You can choose the SD model to use for image generation from a list of (your) available models.
- **On-screen Prompt Transcription**: App transcribes the speech input and displays it on-screen for easy reference.

## Requirements

1. **Windows OS**: The script is designed to run on the Windows operating system.
2. **Auto1111**: [https://github.com/AUTOMATIC1111/stable-diffusion-webui]
3. **SDWebUIAPI**: [https://github.com/mix1009/sdwebuiapi]
4. **Python Dependencies**: Please see the `requirements.txt` file for the required Python packages and versions.

## How to Use

1. Run the `dream_of.py` script (binary version coming soon).
2. Enter the Auto1111 host IP, host port, SD model from the provided list.
   - Note: This step will create a config file. If you need to reconfigure, delete the config file and rerun `dream_of.py`.
3. Press the spacebar to start providing speech input for the prompt.
4. The generated image will be displayed on-screen for 30 seconds before unloading [unload faster with spacebar].
5. Loop to step 3

## Keyboard Controls

- **Spacebar**: Start speech input [listening] and generate the corresponding image prompt.
- **Escape Key**: Close the application.

## Contributing

Contributions to Dream-of are welcome! If you have any ideas, suggestions, or improvements, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE] file for more information.
