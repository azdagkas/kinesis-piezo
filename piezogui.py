# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division

import piezo
from PIL import ImageTk, Image
import sys

if sys.version_info[0] == 3:
    # python 3
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox
else:
    # python 2
    import Tkinter as tk
    import ttk
    import tkMessageBox as messagebox


class StageGUIIndependent():
    '''This is an example GUI that works as stand-alone'''
    def __init__(self, master):
        self.master = master
        master.title("Piezo GUI")
        # Class variables
        self.btnwidth = 11
        self.motor = tk.BooleanVar()
        self.motor.set(False)
        # Create the GUI
        self.stage_widgets(self.master)
        # Create an object of a motor and connect it to the GUI
        self.piezo = piezo.PiezoController(81858318, 84858066)
        if self.piezo.device_connencted:
            self.stageGUI_1.connect_stage(self.piezo)

    def stage_widgets(self, master):
        if not self.motor.get():
            # Create the motor frame
            self.motorframe = ttk.Frame(master)
            # In this simple way, this frame can be part of another bigger GUI
            self.motorframe.pack(side='left', padx=10, pady=10, anchor='n')

            # Create GUI objects
            self.stageGUI_1 = StagePiezo(master, self.motorframe)
        else:
            self.motorframe.pack_forget()
            self.motorframe.destroy()


###############################################################################
#       Basic Class for Stages GUI
###############################################################################
class Stage():
    '''A general stage GUI class with a monitor and general buttons'''
    def __init__(self, master, frame):
        self.master = master
        self.frame = frame
        # Class variables
        self.btnwidth = 5
        # Since I am using self variables for the images, I probably don't
        # need to save the images in extra button variables. The self images
        # exist when the object exists anyway!
        self.imghome = None
        self.imgup = None
        self.imgdown = None
        self.imgback = None
        self.imgmove = None
        self.imgstop = None
        self.imgclosedloop = None
        self.imgopenloop = None
        self.previous_pos = 0
        self.units = None
        self.stage = None
        self.load_images()
        self.motor_panel(self.frame)

    def connect_btns(self, serialNo, set_home, move_to_home, moveup, movedown, units):
        '''Method that gives functionality to the GUI buttons'''
        self.stagefrm.config(text='S/N: '+str(serialNo))
        self.btn_set_home.config(command=set_home)
        self.btn_back.config(command=move_to_home)
        self.btn_up.config(command=moveup)
        self.btn_down.config(command=movedown)
        self.labelunits.config(text=units)

# =============================================================================
#       GUI widgets
# =============================================================================
    def load_images(self):
        '''Load the images for the GUI buttons'''
        # Try to load all the images. If it fails, the GUI will show text
        # on the buttons.
        try:
            im_temp = Image.open("./Source_files/GUI_images/home1.jpg")
            im_temp = im_temp.resize((25, 25), Image.ANTIALIAS)
            self.imghome = ImageTk.PhotoImage(im_temp)

            im_temp = Image.open("./Source_files/GUI_images/back.png")
            im_temp = im_temp.resize((25, 25), Image.ANTIALIAS)
            self.imgback = ImageTk.PhotoImage(im_temp)

            im_temp = Image.open("./Source_files/GUI_images/arrow.png")
            im_temp = im_temp.resize((25, 25), Image.ANTIALIAS)
            im_temp = im_temp.rotate(270)
            self.imgup = ImageTk.PhotoImage(im_temp)

            im_temp = Image.open("./Source_files/GUI_images/arrow.png")
            im_temp = im_temp.resize((25, 25), Image.ANTIALIAS)
            im_temp = im_temp.rotate(90)
            self.imgdown = ImageTk.PhotoImage(im_temp)

            im_temp = Image.open("./Source_files/GUI_images/arrow2.png")
            im_temp = im_temp.resize((25, 25), Image.ANTIALIAS)
            self.imgmove = ImageTk.PhotoImage(im_temp)

            im_temp = Image.open("./Source_files/GUI_images/stop.png")
            im_temp = im_temp.resize((25, 25), Image.ANTIALIAS)
            self.imgstop = ImageTk.PhotoImage(im_temp)

            im_temp = Image.open("./Source_files/GUI_images/closed_loop.png")
            im_temp = im_temp.resize((25, 25), Image.ANTIALIAS)
            self.imgclosedloop = ImageTk.PhotoImage(im_temp)

            im_temp = Image.open("./Source_files/GUI_images/open_loop.png")
            im_temp = im_temp.resize((25, 25), Image.ANTIALIAS)
            self.imgopenloop = ImageTk.PhotoImage(im_temp)
        except Exception as e:
            print(e)
            print('Failed to load GUI images')

    def motor_panel(self, frame):
        '''Positioning of the widgets in the main motor frame'''
        # ==================== Create the motor panel frame ===================
        self.stagefrm = ttk.LabelFrame(frame, text='S/N')
        self.stagefrm.pack(side='top', padx=10, pady=5, anchor='n')

        self.disp = ttk.Entry(self.stagefrm, width=11,
                              font="Helvetica 20 bold", justify="right")
        self.disp.insert('end', '0')
        self.disp.grid(row=1, column=1, padx=5, pady=5)

        self.labelunits = ttk.Label(self.stagefrm, text="", wraplength=50,
                                    font="Helvetica 14 bold", width=3)
        self.labelunits.grid(row=1, column=2, padx=5, pady=5)

        self.btn_move = ttk.Button(self.stagefrm, text="Move", command=None,
                                   width=self.btnwidth, image=self.imgstop)
        self.btn_move.imagemove = self.imgmove
        self.btn_move.imagestop = self.imgstop
        self.btn_move.grid(row=1, column=3, padx=5, pady=5)

        # Create buttons frame
        self.btnfrm = ttk.Frame(self.stagefrm)
        self.btnfrm.grid(row=2, column=1, padx=5, pady=5)
        # Buttons
        self.btn_set_home = ttk.Button(self.btnfrm, text="Home", command=None,
                                       width=self.btnwidth, image=self.imghome)
        self.btn_set_home.image = self.imghome
        self.btn_set_home.grid(row=1, column=1, padx=5, pady=5)

        self.btn_back = ttk.Button(self.btnfrm, text="Back", command=None,
                                   width=self.btnwidth, image=self.imgback)
        self.btn_back.image = self.imgback
        self.btn_back.grid(row=1, column=2, padx=5, pady=5)

        self.btn_down = ttk.Button(self.btnfrm, text="Down", command=None,
                                   width=self.btnwidth, image=self.imgdown)
        self.btn_down.image = self.imgdown
        self.btn_down.grid(row=1, column=3, padx=5, pady=5)

        self.btn_up = ttk.Button(self.btnfrm, text="Up", command=None,
                                 width=self.btnwidth, image=self.imgup)
        self.btn_up.image = self.imgup
        self.btn_up.grid(row=1, column=4, padx=5, pady=5)

        self.labelstate = ttk.Label(self.stagefrm, text="", wraplength=50,
                                    font="Helvetica 10 bold")
        self.labelstate.grid(row=2, column=2, padx=5, pady=5, columnspan=2)


###############################################################################
#       Class for Strain Gauge Reader GUI
###############################################################################
class StageStrainReader(Stage):
    '''Strain reader GUI for the Thorlabs piezoelectric stage.'''
    def __init__(self, master, frame):
        Stage.__init__(self, master, frame)
        self.set_disp_value_flag = False

    def connect_stage(self, piezo, reader):
        '''Connect the strain reader object to the GUI'''
        self.stage = piezo
        self.reader = reader
        self.stagemonitor()
        self.connect_btns(reader.serialNo, self.homebtn,
                          piezo.move_pos_to_home, piezo.move_pos_up,
                          piezo.move_pos_down, reader.get_units())
        self.btn_move.config(image=self.imgmove)
        self.btn_move.config(command=self.btn_move_act)
        self.btn_set_home.config(text='Zero')

    def homebtn(self):
        '''Perform the zeroing function of the strain reader'''
        if messagebox.askokcancel("Set Zero", "To proceed remove the SMA cable  \n" \
                                  " from \"EXT IN\" and press ok! \n" \
                                  "Be sure that you are in open loop with 0 Volts."):
            self.reader.set_zero()

    def btn_move_act(self):
        if self.set_disp_value_flag:
            self.stage.move_to_pos(float(self.disp.get()))
            self.set_disp_value_flag = False
        else:
            self.set_disp_value_flag = True
            self.disp.delete(0, 'end')

    def monitor(self, currentVal):
        if not self.set_disp_value_flag:
            self.disp.delete(0, 'end')
            self.disp.insert('', round(currentVal, 3))

        if self.stage.is_closed_loop():
            self.btn_back.config(state="normal")
            self.btn_up.config(state="normal")
            self.btn_down.config(state="normal")
        else:
            self.btn_back.config(state="disabled")
            self.btn_up.config(state="disabled")
            self.btn_down.config(state="disabled")

        if self.reader.is_zeroing():
            self.labelstate.config(text='Zeroing', foreground="red")
        else:
            self.labelstate.config(text='', foreground="black")

    def stagemonitor(self):
        self.monitor(self.reader.get_pos())
        self.master.after(100, self.stagemonitor)


###############################################################################
#       Class for Piezo Stage GUI
###############################################################################
class StagePiezo(Stage):
    '''Piezo stage GUI for the Thorlabs piezoelectric stages'''
    def __init__(self, master, frame):
        Stage.__init__(self, master, frame)
        self.set_disp_value_flag = False
        self.btn_set_home.imagecl = self.imgclosedloop
        self.btn_set_home.imageol = self.imgopenloop
        self.btn_set_home.config(image=self.imgclosedloop)
        self.btn_set_home.config(state="disabled")

    def connect_stage(self, stage):
        '''Connect the stage object to the GUI'''
        self.stage = stage
        self.stagemonitor()
        self.connect_btns(stage.serialNo, self.closed_loop, stage.move_to_home,
                          stage.moveup, stage.movedown, stage.get_units())
        self.btn_move.config(image=self.imgmove)
        self.btn_move.config(command=self.btn_move_act)
        if self.stage.serial_reader is not 'Empty':
            self.readerGUI = StageStrainReader(self.master, self.frame)
            self.readerGUI.connect_stage(self.stage, self.stage.reader)
            self.btn_set_home.config(state="normal")

    def btn_move_act(self):
        if self.set_disp_value_flag:
            self.stage.set_value(float(self.disp.get()))
            self.set_disp_value_flag = False
        else:
            self.set_disp_value_flag = True
            self.disp.delete(0, 'end')

    def closed_loop(self):
        if self.stage.is_closed_loop():
            self.stage.set_open_loop()
        else:
            self.labelstate.config(text='Calibrating')
            self.stage.set_closed_loop()
            self.stage.calibrate_pos()
            self.labelstate.config(text='')

    def monitor(self, currentVal):
        self.labelunits.config(text=self.stage.get_units())

        if not self.set_disp_value_flag:
            self.disp.delete(0, 'end')
            self.disp.insert('', round(currentVal, 2))

        if self.stage.is_closed_loop():
            self.labelstate.config(text='Closed Loop')
            self.btn_set_home.config(image=self.imgopenloop, text='CL')
        else:
            self.labelstate.config(text='Open Loop')
            self.btn_set_home.config(image=self.imgclosedloop, text='OL')

    def stagemonitor(self):
        self.monitor(self.stage.get_value())
        self.master.after(100, self.stagemonitor)


if __name__ == "__main__":
    root = tk.Tk()
    StageGUIIndependent(root)
    root.mainloop()
