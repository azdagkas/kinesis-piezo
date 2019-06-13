# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division

import clr
import time
# Needed for the use of Decimal class of c#. Requires clr to import System in
# this way.
from System import Decimal
clr.AddReference("System")
clr.AddReference("./libs/kinesis/Thorlabs.MotionControl.DeviceManagerCLI")
clr.AddReference("./libs/kinesis/Thorlabs.MotionControl.GenericPiezoCLI")
clr.AddReference("./libs/kinesis/Thorlabs.MotionControl.TCube.PiezoCLI")
clr.AddReference("./libs/kinesis/Thorlabs.MotionControl.TCube.StrainGaugeCLI")
from Thorlabs.MotionControl.DeviceManagerCLI import DeviceManagerCLI
from Thorlabs.MotionControl.GenericPiezoCLI import Piezo
from Thorlabs.MotionControl.TCube.PiezoCLI import *
from Thorlabs.MotionControl.TCube.StrainGaugeCLI import *


class ThorStages(object):
    '''
    Class for the initialization and connection of thorlabs stages.
    '''
    def __init__(self):
        self.num_of_devices = None
        self.serial_numbers = None
        self.device_connencted = False

    def device_search(self):
        # Ask the device manager to get the list of all devices connected
        # to the computer
        try:
            DeviceManagerCLI.BuildDeviceList()
            connected = True
        except Exception as e:
            print('Exception raised by BuildDeviceList \n', e)
            print('Tholabs stage not found')
            connected = False

        if connected:
            # Get a c# list with all the connected kinesis serial numbers
            self.serial_numbers = DeviceManagerCLI.GetDeviceList()
            self.num_of_devices = self.serial_numbers.Count
            if self.num_of_devices != 0:
                for i in range(self.num_of_devices):
                    print(self.serial_numbers[i])
            else:
                print('No stages found')
                connected = False

        self.device_connencted = connected
        return connected

    def connect_enable(self, device, serialNo):
        '''Connect and enable the communication of the device with the computer.

        Args:
        -------
        device : object.
                An object of the device that we want to connect.

        serialNo : int.
                The serial number of the device.
        '''
        # Open a connection to the device
        try:
            device.Connect(serialNo)
        except Exception as e:
            print('Failed to open device ', serialNo)
            print(e)

        # Wait for the device settings to initialize
        if not device.IsSettingsInitialized():
            try:
                print('Wait for initialization')
                device.WaitForSettingsInitialized(5000)
            except Exception as e:
                print('Settings failed to initialize')
                print(e)

        # Start the device polling (asks for comunication every 250ms).
        device.StartPolling(250)
        # Needs a delay so that the current enabled state can be obtained
        time.sleep(0.500)
        # Enable the channel otherwise any move is ignored
        device.EnableDevice()
        # Needs a delay to give time for the device to be enabled
        time.sleep(0.500)
        print('Device is now enabled')

        # Display info about device
        deviceInfo = device.GetDeviceInfo()
        print("Device ", deviceInfo.SerialNumber, ' = ', deviceInfo.Name)


###############################################################################
#       Strain Gauge Reader Controller
###############################################################################
class StrainReader(ThorStages):
    '''
    Class for the control of the Strain Gauge Reader.

    Objects of this class are created in the PiezoController class.
    After all, this is a reader it doesn't make sense to connect it
    without the piezo controller, except for debugging purposes.
    '''
    def __init__(self, serial):
        ThorStages.__init__(self)
        # Variables
        self.serialNo = str(serial)
        self.device = None
        self.travelmode = None
        # Initialize
        if self.device_search():
            self.initialize()

    def initialize(self):
        self.device = TCubeStrainGauge.CreateDevice(self.serialNo)
        if self.device is None:
            print('Strain Reader is a null object')
        else:
            print('Strain Reader, ' + str(self.serialNo) + ', has been created')

        # Connect and enable the device
        self.connect_enable(self.device, self.serialNo)

        # Initialize the DeviceUnitConverter object required for real world
        # unit parameters.
        self.device.GetStrainGaugeConfiguration(self.serialNo)

        self.device.SetLEDs(120)

    def get_pos(self):
        current_pos = Decimal.ToDouble(self.device.Status.get_Reading())
        return current_pos

    def set_zero(self):
        self.device.SetZero()

    def is_zeroing(self):
        return self.device.Status.get_IsZeroing()

    def get_units(self):
        if self.device.GetDisplayMode() == 1:
            units = 'μm'
        elif self.device.GetDisplayMode() == 2:
            units = 'V'
        elif self.device.GetDisplayMode() == 3:
            units = 'N'
        else:
            units = 'Error'
        return units


###############################################################################
#       Piezo Controller
###############################################################################
class PiezoController(ThorStages):
    '''
    Class for the control of the Piezo Controller.

    Args
    ------
    serial_controller : int.
            The serial number of the controller

    serial_reader : int (optional).
            This is an optional argument. It is the serial number of the strain
            reader and if given creates an object of the StrainReader class.
            It is required to use the stage in closed loop.

    Example
    -------
    import piezo
    mypiezo = piezo.PiezoController(81858318, 84858066)
    '''
    def __init__(self, serial_controller, serial_reader='Empty'):
        ThorStages.__init__(self)
        # Variables
        self.serialNo = str(serial_controller)
        self.serial_reader = str(serial_reader)
        self.device = None
        self.reader = None
        self.travelmode = None
        self.mysettings = None
        # Initialize
        if self.device_search():
            self.initialize()
        # Calibration variables
        self.a = None
        self.b = None

    def initialize(self):
        # Create the device
        self.device = TCubePiezo.CreateDevice(self.serialNo)
        if self.device is None:
            print('Piezo Controller is a null object')
        else:
            print('Piezo Controller, ' + str(self.serialNo) + ', has been created')

        # Connect and enable the device
        self.connect_enable(self.device, self.serialNo)

        # Initialize the DeviceUnitConverter object required for real world
        # unit parameters.
        self.device.GetPiezoConfiguration(self.serialNo)

        # Create an instance of device setting.
        # Change the settings using this object and then use set
        # settings to load them into the device.
        self.mysettings = self.device.PiezoDeviceSettings
        # Eg.
        # self.mysettings.HubInputSource.set_HubMode(2)
        # self.device.SetSettings(mysettings, False)
        # False means to not write it in the memory for default on startup

        # Change the Jog steps
        self.mysettings.OutputVoltageRange.set_MaxOutputVoltage(Decimal(75))
        self.mysettings.Control.set_VoltageStepSize(Decimal(1))
        self.mysettings.Control.set_PercentageStepSize(Decimal(1))
        self.device.SetSettings(self.mysettings, False)  # False for not persistent settings

        if self.serial_reader is not 'Empty':
            self.reader = StrainReader(self.serial_reader)

    def get_units(self):
        if self.is_closed_loop():
            units = '%'
        else:
            units = 'V'
        return units

    def get_value(self):
        if self.is_closed_loop():
            value = Decimal.ToDouble(self.device.GetPercentageTravel())
        else:
            value = Decimal.ToDouble(self.device.GetOutputVoltage())
        return value

    def set_value(self, Value):
        if self.is_closed_loop():
            self.device.SetPercentageTravel(Decimal(Value))
        else:
            self.device.SetOutputVoltage(Decimal(Value))

    def moveup(self):
        self.device.Jog(1)

    def movedown(self):
        self.device.Jog(2)

    def move_to_home(self):
        if self.is_closed_loop():
            self.device.SetPercentageTravel(Decimal(0))
        else:
            self.device.SetOutputVoltage(Decimal(0))

    # ### Closed loop #########################################################
    def is_closed_loop(self):
        return self.device.Status.get_IsClosedLoop()

    def set_closed_loop(self):
        # Switch to software and Potentiometer control
        if self.device.GetVoltageSource() != 2:
           self.device.SetVoltageSource(2)  # 2 for software and Potentiometer only

        # Switch to feedback input from SMA, EXT IN
        # print(self.device.GetIOSettings().VoltageLimit)
        if self.device.GetIOSettings().HubAnalogueInput != 3:  # 3 for external SMA
            self.mysettings.HubInputSource.set_HubMode(3)
            self.device.SetSettings(self.mysettings, False)  # False for not persistent settings

        if self.device.GetPositionControlMode() == 1:
            # Mode=1 => openloop
            # Mode=2 => closed loop
            self.device.SetPositionControlMode(2)

    def set_open_loop(self):
        # Switch to software and Potentiometer control
        if self.device.GetVoltageSource() != 2:
           self.device.SetVoltageSource(2)  # 2 for software and Potentiometer only

        # Switch to feedback input from Channel1
        # print(self.device.GetIOSettings().VoltageLimit)
        if self.device.GetIOSettings().HubAnalogueInput != 1:  # 3 for external SMA
            self.mysettings.HubInputSource.set_HubMode(1)
            self.device.SetSettings(self.mysettings, False)  # False for not persistent settings

        if self.device.GetPositionControlMode() == 2:
            # Mode=1 => openloop
            # Mode=2 => closed loop
            self.device.SetPositionControlMode(1)

    def calibrate_pos(self):
        '''Creates a calibration that translates position to voltage.

        The controller takes as input a value that is the percentage of the
        maximum posible voltage. It usefull to be able to use as input a number
        in um. Hence, a simple calibration procedure is used. The stage moves
        to 10 and 70 percent of the maximum voltage and the reader value is
        recorded. Assuming a linear relationship,
        percentage = a*position + b
        the slope a and the constant b are calculated and used to translate
        position to percentage voltage.

        This function should be called imediately after set_closed_loop.
        '''
        y1 = 10
        y2 = 70
        time.sleep(1)
        if self.is_closed_loop():
            self.device.SetPercentageTravel(Decimal(y1))
            time.sleep(4)
            x1 = self.reader.get_pos()
            time.sleep(0.01)
            self.device.SetPercentageTravel(Decimal(y2))
            time.sleep(4)
            x2 = self.reader.get_pos()
            time.sleep(0.01)
            self.a = (y2-y1)/(x2-x1)
            self.b = -self.a*x1+y1
            # eg go to 1um
            y = self.a*1.0+self.b
            self.device.SetPercentageTravel(Decimal(y))

    def move_to_pos(self, value):
        y=self.a*value+self.b
        self.device.SetPercentageTravel(Decimal(y))

    def move_pos_up(self):
        if self.reader.get_pos() < 19:
            self.move_to_pos(self.reader.get_pos()+1)

    def move_pos_down(self):
        if self.reader.get_pos() > 1:
            self.move_to_pos(self.reader.get_pos()-1)

    def move_pos_to_home(self):
        self.move_to_pos(0)


if __name__ == "__main__":
    # Create an object of the PiezoController class. The numbers, are the
    # serial numbers of the controller and the reader respectively.
    mypiezo = PiezoController(81858318, 84858066)
