# kinesis-piezo

## Python code for the control of Thorlabs piezoelectric stages
The repository contains code for the control of the Thorlabs TPZ001 (piezo driver) and
 TSG001 (strain gauge reader) controllers with the kinesis API. It contains 2 files:
- piezo.py for the communication with the controllers that can be used as standalone and
- piezogui.py that creates a graphical user interface (GUI) written with tkinter.

## Description
This code was created for the automation of an optical interferometry experiment and
is presented here to act as a guide to people that are looking for something similar.
 The modular approach makes it very easy to embed in bigger GUIs (see the image bellow)
 that combine many more instruments which is usually the case in big experiments
that require automation.

![](https://user-images.githubusercontent.com/49478566/59421776-12819000-8dc7-11e9-931c-7747ca39304a.png)

The red dashed square indicates the GUI carrying the piezo stage functionality that is 
embedded in a bigger GUI carrying functionality for cameras, a laser and the processing
of the acquired data.

## Instructions
1. Make sure you have these installed:
- pythonnet
- Pillow, only if you plan to load images to the GUI

2. Download the source code from the [release](https://github.com/azdagkas/kinesis-piezo/releases) tab 
or clone the repository.

3. (Optional) Download images for the buttons of the GUI.

4. Connect the controller to your computer and run the
 piezo.py file or the piezogui.py file if you want
 to use the GUI. Do not forget to change the serial numbers
 with the serial numbers of your devices.
 
Has been tested with python 2.7 and 3.6.
