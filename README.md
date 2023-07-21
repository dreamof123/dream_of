<h1 align="center">Dream-of</h1>

<p align="center">
  <strong>An app for converting speech to image using AI-powered speech-to-text-to-image generation.</strong>
</p>

## Overview

Dream-of allows you to generate creative and visually appealing images from latent space, based on the prompts provided by speech.

## Example of Use Case

Deploy on an art-frame-like monitor [powered by any device capable of running Windows OS] with an input device [keyboard, flic button, etc.] that triggers "listening" with the "press of a button".

Speech provided by the user magically generates an image from latent space. A truly new image, from the user's imagination, that does not exist anywhere else in history.

## Features

- **Minimalistic Interface**: App operates in a minimalistic full-screen black window.
- **Speech to Prompt to Image**: App converts speech to text prompt, then generates an image.
- **Punctuation Handling**: Any time you say "dream of" a comma will insert into the prompt- giving prompter more control of composition.
- **Select SD Model**: You can choose the SD model to use for image generation from a list of (your) available models.
- **On-screen Prompt Transcription**: App transcribes the speech input and displays it on-screen for easy reference.

## Requirements

1. [Client] **Windows OS**
2. [Client] **Python Dependencies**: Please see the `requirements.txt` file for the required Python packages / versions
3. [Client] **SDWebUIAPI**: Auto1111 API wrapper [https://github.com/mix1009/sdwebuiapi]
4. [Server] **Auto1111**: Modulates Stable Diffusion models [https://github.com/AUTOMATIC1111/stable-diffusion-webui]

* Client = end user device [e.g., Windows-powered "art-frame"] running dream_of.py
* Server = server location hosting Auto1111

NOTE: 'dream_of.py' can be refactored to support any OS

## How to Use

1. Run the `dream_of.py` script on client.
2. Enter the Auto1111 host IP, host port, SD model from the provided list.
   - This step will create a config file in your run directory.
   - If you need to reconfigure, delete the config file and rerun `dream_of.py`.
3. Press the spacebar to start providing speech input for the prompt.
* The generated image will be displayed on-screen for 30 seconds before unloading [unload faster with spacebar].
* Loop to step 3

## Keyboard Controls

- **Spacebar**: Start listen for speech.
- **Escape Key**: Close the app.

## Version History

[07.21.23]
- Refactor to force GUI to wait on user inputs via termninal (when config does not exist)
  
[07.20.23]
- Launch v1

## Contributing

Contributions to Dream-of are welcome! If you have any ideas, suggestions, or improvements, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE] file for more information.
