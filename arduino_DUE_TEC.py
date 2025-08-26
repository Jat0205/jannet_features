#-------------------------------------------------------------------------------
#ArduinoCounter.py
#Original version by Shonali Dhingra (Feb 4, 2014)
#Added home-built Galvo control funcions by Jen (23.May.2014)
#Modified by Jannet Trabelsi: independent of pythics (AUGUST 2025)
# ls /dev/cu.usb*
#-------------------------------------------------------------------------------

import arduino
import numpy as np

class Newport700C(arduino.ArduinoInstrument):
    def __init__(self, *args, **kwargs):
        #constructor
        #ArduinoInstrument object
        super().__init__(*args, **kwargs)
        
        # List of temperature-resistance conversion of the thermistor in TEC module. From BetaTherm 10K3A1B datasheet. 
        # Temperatures in Celsius (C) in Tlist, resistances in Ohm in Rlist.
        # For example, at -79C, the resistance is 6677205ohm, or 6677k ohm. They have the same index.
        self.Tarray = np.array([-80,	-79,	-78,	-77,	-76,	-75,	-74,	-73,	-72,	-71,	-70,	-69,	-68,	-67,	-66,	-65,	-64,	-63,	-62,	-61,	-60,	-59,	-58,	-57,	-56,	-55,	-54,	-53,	-52,	-51,	-50,	-49,	-48,	-47,	-46,	-45,	-44,	-43,	-42,	-41,	-40,	-39,	-38,	-37,	-36,	-35,	-34,	-33,	-32,	-31,	-30,	-29,	-28,	-27,	-26,	-25,	-24,	-23,	-22,	-21,	-20,	-19,	-18,	-17,	-16,	-15,	-14,	-13,	-12,	-11,	-10,	-9,	-8,	-7,	-6,	-5,	-4,	-3,	-2,	-1,	0,	1,	2,	3,	4,	5,	6,	7,	8,	9,	10,	11,	12,	13,	14,	15,	16,	17,	18,	19,	20,	21,	22,	23,	24,	25,	26,	27,	28,	29,	30,	31,	32,	33,	34,	35,	36,	37,	38,	39,	40,	41,	42,	43,	44,	45,	46,	47,	48,	49,	50,	51,	52,	53,	54,	55,	56,	57,	58,	59,	60,	61,	62,	63,	64,	65,	66,	67,	68,	69,	70,	71,	72,	73,	74,	75,	76,	77,	78,	79,	80,	81,	82,	83,	84,	85,	86,	87,	88,	89,	90,	91,	92,	93,	94,	95,	96,	97,	98,	99,	100,	101,	102,	103,	104,	105,	106,	107,	108,	109,	110,	111,	112,	113,	114,	115,	116,	117,	118,	119,	120,	121,	122,	123,	124,	125,	126,	127,	128,	129,	130,	131,	132,	133,	134,	135,	136,	137,	138,	139,	140,	141,	142,	143,	144,	145,	146,	147,	148,	149,	150])
        self.Rarray = np.array([7296874,	6677205,	6114311,	5602677,	5137343,	4713762,	4327977,	3966352,	3655631,	3362963,	3095611,	2851363,	2627981,	2423519,	2236398,	2064919,	1907728,	1763539,	1631173,	1509639,	1397935,	1295239,	1200732,	1113744,	1033619,	959789,	891689,	828865,	770880,	717310,	667828,	622055,	579718,	540530,	504230,	470609,	439445,	410532,	383712,	358806,	335671,	314179,	294193,	275605,	258307,	242195,	227196,	213219,	200184,	188026,	176683,	166091,	156199,	146959,	138322,	130243,	122687,	115613,	108991,	102787,	96974,	91525,	86415,	81621,	77121,	72895,	68927,	65198,	61693,	58397,	55298,	52380,	49633,	47047,	44610,	42314.6,	40149.5,	38108.5,	36182.8,	34366,	32650.8,	31030.4,	29500.1,	28054.2,	26687.6,	25395.5,	24172.7,	23016,	21921.7,	20855.2,	19903.5,	18973.6,	18092.6,	17257.4,	16465.1,	15714,	15001.2,	14324.6,	13682.6,	13052.8,	12493.7,	11943.3,	11420,	10922.7,	10449.9,	10000,	9572,	9164.7,	8777,	8407.7,	8056,	7720.9,	7401.7,	7097.2,	6807,	6530.1,	6266.1,	6014.2,	5773.7,	5544.1,	5321.9,	5115.6,	4915.5,	4724.3,	4541.6,	4366.9,	4199.9,	4040.1,	3887.2,	3741.1,	3601,	3466.9,	3338.6,	3215.6,	3097.9,	2985.1,	2876.9,	2773.2,	2673.9,	2578.5,	2487.1,	2399.4,	2315.2,	2234.7,	2156.7,	2082.3,	2010.8,	1942.1,	1876,	1812.6,	1751,	1693,	1636.63,	1582.41,	1530.28,	1480.12,	1431.87,	1385.37,	1340.68,	1297.64,	1256.17,	1216.23,	1177.75,	1140.71,	1104.99,	1070.58,	1037.4,	1005.4,	974.56,	944.81,	916.11,	888.41,	861.7,	835.93,	811.03,	786.99,	763.79,	741.38,	719.74,	698.82,	678.63,	659.1,	640.23,	622,	604.36,	587.31,	570.82,	554.86,	539.44,	524.51,	510.06,	496.08,	482.55,	469.45,	456.76,	444.48,	432.58,	421.06,	409.9,	399.08,	388.59,	378.44,	368.59,	359.05,	349.79,	340.82,	332.11,	323.37,	315.48,	307.53,	299.82,	292.34,	285.08,	278.03,	271.19,	264.54,	258.09,	251.82,	245.74,	239.82,	234.08,	228.5,	223.08,	217.8,	212.68,	207.7,	202.86,	198.15,	193.57,	189.12,	184.79])
        self.arduino_bits = 2**12 - 1 # For Arduino DUE, 12-bits
        self.arduino_voltageMax = 5.0 # For Arduino DUE with Optical isolator shield.
        self.arduino_voltageMin = -5.0
        self.Rref = 20000. # Rref in ohm, 20k ohm reference resistor.  
        self.nutout = 2023 # Aiming for zero final op-amp output. Experimental value.  
        self.global_setpoint = 0    
        
    def check_ready_message(self):
        return self.readline()

    def setup(self, T_setpoint, kp, ki):
        print(f"Setting up with T_setpoint: {T_setpoint}, kp: {kp}, ki: {ki}")  # Debugging print statement
        bit_setpoint = self.Vin_to_bit(self.T_to_V(T_setpoint))
        print(f"Converted T_setpoint to bit_setpoint: {bit_setpoint}")  # Debugging print statement
        self.global_setpoint = T_setpoint
        return self.ask("setup", bit_setpoint, kp, ki)

    def start(self, T_setpoint, kp, ki, regulate_TEC0):
        outA = self.setup(T_setpoint, kp, ki)
        outB = self.ask("start", int(regulate_TEC0))
        return str(outA) + str(outB)
        
    def stop(self):
        return self.ask("stop")
        
    def bit_to_Vin(self, bit):
        # Experimental fit of the input voltage at the opto-2-2 vs. Arduino read-in bit. 
        # This would include non-linearity of both the optical isolation board and Arduino ADC.
        vin = 0.00267 * float(bit) - 5.418
        return vin
        
    def Vin_to_bit(self, vin):
        # Inverse conversion from target Vin to Arduino bit, for temperature set point.
        bit = (vin + 5.418) / 0.00267
        return int(bit)

    def get_status(self):
        line = self.ask("status")
        try:
            parts = line.strip().split()
            if len(parts) != 2:
                raise ValueError(f"Unexpected response from Arduino: '{line}'")
            TEC0_vin_raw = int(parts[0])
            TEC0_output_raw = float(parts[1])
        except Exception as e:
            print(f"Error parsing status line: {e}")
            return None, None
        vin = self.bit_to_Vin(TEC0_vin_raw)
        temp = self.V_to_T(vin)
        output_frac = (TEC0_output_raw - self.nutout) / (self.arduino_bits / 2.0)
        return temp, output_frac

    def maxcool(self):
        return self.ask("setout", 0) # By the design of the circuit, lowest Arduino output 0 is max cooling current.

    def zerocool(self):
        return self.ask("setout", self.nutout) 
        
    # Unit conversions and other lower level stuff can go here too.
    def V_to_T(self, V):
        Rref = self.Rref
        Vmax = self.arduino_voltageMax
        Rtherm = Rref * (Vmax / V - 1.)   # Voltage divider
        imin = np.argmin(np.abs(self.Rarray - Rtherm))
        if Rtherm > self.Rarray[imin]: # Rtherm greater than the element value, meaning temperature lower than element value.
            T = self.Tarray[imin] + (Rtherm - self.Rarray[imin]) * (self.Tarray[imin] - self.Tarray[imin-1])/(self.Rarray[imin] - self.Rarray[imin-1])
        else: 
            T = self.Tarray[imin] + (Rtherm - self.Rarray[imin]) * (self.Tarray[imin + 1] - self.Tarray[imin])/(self.Rarray[imin + 1] - self.Rarray[imin])
        return T
    
    def T_to_V(self, Tset):
        Rref = self.Rref
        Vmax = self.arduino_voltageMax
        imin = np.argmin(np.abs(self.Tarray - Tset))      
        if Tset < self.Tarray[imin]:
            R = self.Rarray[imin] + (Tset - self.Tarray[imin]) * (self.Rarray[imin] - self.Rarray[imin - 1]) / (self.Tarray[imin] - self.Tarray[imin - 1])
        else:
            R = self.Rarray[imin] + (Tset - self.Tarray[imin]) * (self.Rarray[imin + 1] - self.Rarray[imin]) / (self.Tarray[imin + 1] - self.Tarray[imin]) 
        V = Vmax * Rref / (Rref + R)
        return V 
    
    def get_setpoint(self):
        return self.global_setpoint
    
if __name__ == "__main__":
    
    vTEC = Newport700C('/dev/cu.usbmodem1101')
    #print (vTEC.V_to_T(3.13))
    #print (vTEC.T_to_V(21.0))
    # Send setup command
    #print(vTEC.setup(17, 2.0, 0.3))  # Expects: 2000 300 Done setting.
    # Start regulation
    #print(vTEC.start(17, 2.0, 0.3, 1))  # Expects: 2000 300 Done setting.S Started
    # Read current temperature and output fraction
    #print(vTEC.get_status())        # Expects: (temp, output_frac)
    # Set max cooling
    #print(vTEC.maxcool())           # Expects: S Setout Done.
    # Set zero cooling
    #print(vTEC.zerocool())          # Expects: S Setout Done.
    # Stop regulation
    #print(vTEC.stop())              # Expects: S Stopped.
