# PawTalk

**ML-powered Dog Emotion Recognition** 
Dogs have a lot to say, but their emotions often remain a mystery. This project implements an emotion-classification system for dogs. It uses a trained machine-learning model running on a Raspberry Pi to analyze camera input, then shows detected emotions and confidence scores on a LCD display and signals them via an RGB LED. The model recognizes four primary emotional states.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Hardware Setup](#hardware-setup)
3. [Software Installation](#software-installation)
4. [Configuration](#configuration)
5. [Project Structure](#project-structure)
6. [Usage](#usage)
7. [Limitations](#limitations)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

* **Hardware:**

  * Freenove Ultimate Starter Kit for Raspberry Pi (includes RGB LED, push-button, and 16×2 LCD display)
  * Raspberry Pi (Model 3B+ or newer) with Raspberry Pi OS installed
  * Pi Camera or USB webcam

## Hardware Setup

1. **LCD Display**

   * Connect SDA to GPIO2 (pin 3) and SCL to GPIO3 (pin 5).
   * Connect VCC to 5V, GND to GND on the Pi.
2. **RGB LED**

   * Connect red, green, blue pins to GPIO5, GPIO6, and GPIO13 respectively (through appropriate resistors).
   * Connect common pin to GND.
3. **Push-Button (optional)**

   * Connect one leg to GPIO21 and the other leg to GND (with the pull-up resistor configured in software).
4. **Camera**

   * Attach the Pi Camera to the CSI port or plug in your USB webcam.

## Software Installation

Clone the repository and install dependencies for both the AI client and the Raspberry Pi server.

# Clone the repo
git clone https://github.com/Juliane-Farmer/PawTalk-ML-powered-Dog-Emotion-Recognition.git
cd PawTalk-ML-powered-Dog-Emotion-Recognition

# AI client setup
cd ai_client
pip install -r requirements.txt

# Raspberry Pi server setup
cd ../rpi_server
pip install -r requirements.txt

## Configuration

Project-level configuration lives in `config.yaml` at the repository root:


model_path: ./models/best_colab.pt
server:
  host: 0.0.0.0
  port: 8500
confidence_threshold: 0.6


* **model\_path:** Path to your trained `.pt` model file.
* **server.host/server.port:** Address and port for the Pi socket server.
* **confidence\_threshold:** Minimum confidence required to display an emotion.

Emotion labels are defined in `classes.txt` (one label per line, in the order of model output indices):

happy
sad
angry
relaxed

## Project Structure

```
PawTalk-ML-powered-Dog-Emotion-Recognition/
├── ai_client/
│   ├── ai_client_dog.py
│   └── requirements.txt
├── rpi_server/
│   ├── rpi_server_dog.py
│   ├── lcd.py
│   ├── rgb_led.py
│   └── requirements.txt
├── models/
│   └── best_colab.pt
├── classes.txt
├── config.yaml
└── .gitignore
```

## Usage

1. **Start the Raspberry Pi server** (on your Pi):

   cd PawTalk-ML-powered-Dog-Emotion-Recognition/rpi_server
   python rpi_server_dog.py

   The server will initialize the LCD, LED, and begin listening for incoming connections.

2. **Start the AI client** (on a separate machine or the Pi itself):

   cd PawTalk-ML-powered-Dog-Emotion-Recognition/ai_client
   python ai_client_dog.py

   The client opens the camera, runs emotion detection, and sends results to the server.

3. **View output:**

   * The LCD will display the detected emotion and confidence percentage.
   * The RGB LED will light up in a color corresponding to the emotion.
   * Press the button to toggle the LED on/off (if wired).

## Limitations

* This model was trained exclusively on images of dogs. It is not designed to differentiate between dogs and other species or humans, and may misclassify emotions when presented with non-dog subjects.

## Troubleshooting

* **No image from camera:** Ensure the camera is enabled in `raspi-config` or that USB webcam drivers are installed.
* **I2C LCD not found:** Run `sudo i2cdetect -y 1` to verify the address (should show `0x27`).
* **Socket errors:** Confirm both client and server use the same host/port in `config.yaml`.
* **Model loading errors:** Check that `model_path` points to a valid `.pt` file and that you’ve installed the required Python packages.


