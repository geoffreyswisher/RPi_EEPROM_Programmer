import wiringpi
from time import sleep


# Pin numbers using wiringPi pin numbering
# Shift Registers
SHIFT_DATA = 0
SHIFT_CLK = 2
SHIFT_LATCH = 1

# EEPROM
WRITE_EN = 27

EEPROM_DATA = [3,4,5,6,23,24,26,25]

# Voltage constants
INPUT = 0
OUTPUT = 1
LOW = 0
HIGH = 1
MSBFIRST = 1
LSBFIRST = 0

# Pulse the shift register latch

def pulseLatch():

	wiringpi.digitalWrite(SHIFT_LATCH, HIGH)
	wiringpi.digitalWrite(SHIFT_LATCH, LOW)


# Shifts out the address using the shift registers
# Attaches output enable bit to the last output

def setAddress(address, outputEnable):

	# shift out greatest 3 bits + output enable (low for true, high for false)
	wiringpi.shiftOut(SHIFT_DATA, SHIFT_CLK, MSBFIRST, ((address >> 8) | (0x00 if outputEnable else 0x80)))

	# shift out the bottom 8 bits
	wiringpi.shiftOut(SHIFT_DATA, SHIFT_CLK, MSBFIRST, (address & 255))

	#pulse latch for output
	pulseLatch()


# Read the data an address from the EEPROM

def readEEPROM(address):

	# setup data pins for input
	for pin in EEPROM_DATA:
		wiringpi.pinMode(pin, INPUT)

	setAddress(address, True)

	# return byte
	data = 0
	for pin in reversed(EEPROM_DATA):
		data = (data << 1) + wiringpi.digitalRead(pin)

	return hex(data)


# Write to an address on the EEPROM

def writeEEPROM(address, data):

	# setup data pins for output
	for pin in EEPROM_DATA:
		wiringpi.pinMode(pin, OUTPUT)

	setAddress(address, False)

	# output the data
	for pin in EEPROM_DATA:
		wiringpi.digitalWrite(pin, data & 1)
		data = data >> 1

	# send the 1000 ns write pulse (not very accurate bc of time module)
	wiringpi.digitalWrite(WRITE_EN, LOW)
	sleep(0.0000001)
	wiringpi.digitalWrite(WRITE_EN, HIGH)

	# delay before next write (just to be sure)
	sleep(0.01)


# prints the first 256 bytes

def print256bytes():

	# print the first 256 bytes in groups of 16
	for base in range(0,256,16):

		return_list = []

		# the base value - the "0x"
		return_list.append(hex(base)[2:])
		return_list.append(": ")

		for offset in range(0, 16):

			# the single byte value - the "0x"
			return_list.append(readEEPROM(base + offset)[2:])
			return_list.append(" ")

		return_string = "".join(return_list)
		print return_string

	print("\n")


# Prints the entire contents of the EEPROM

def printContents():

	# print the 2048 bytes in groups of 16
        for base in range(0,2048,16):

                return_list = []

                # the base value - the "0x" 
                return_list.append(hex(base)[2:])
                return_list.append(": ")

                for offset in range(0, 16):

                        # the single byte value - the "0x"
                        return_list.append(readEEPROM(base + offset)[2:])
                        return_list.append(" ")

                return_string = "".join(return_list)
                print return_string


# Write a series of bytes starting at an address

def writeBytes(start_address, bytes):

	offset = 0
	for byte in bytes:
		writeEEPROM(start_address + offset, byte)
		offset = offset + 1




# Erases an amount of bytes after start address

def eraseBytes(start_address, amount):

	counter = 0
	while counter < amount:
		writeEEPROM(start_address + counter, 0xff)
		counter = counter + 1


# Using the program

def instruct():

	'''address = 0x9

	print("Reading EEPROM")
	print(readEEPROM(address))

	print("Writing to EEPROM")
	writeEEPROM(address, 0x88)

	print("Reading EEPROM")
	print(readEEPROM(address))
	'''

	bytes = [0xca, 0xfe, 0xba, 0xbe, 0xde, 0xad, 0xbe, 0xef]
	writeBytes(0x0, bytes)

	print256bytes()

	eraseBytes(0x0, 256)
	print256bytes()


# setup board and most pins for use

def setup():

	wiringpi.wiringPiSetup()

	wiringpi.digitalWrite(SHIFT_DATA, LOW)
	wiringpi.pinMode(SHIFT_DATA, OUTPUT)

	wiringpi.digitalWrite(SHIFT_CLK, LOW)
	wiringpi.pinMode(SHIFT_CLK, OUTPUT)

	wiringpi.digitalWrite(SHIFT_LATCH, LOW)
	wiringpi.pinMode(SHIFT_LATCH, OUTPUT)

	wiringpi.digitalWrite(WRITE_EN, HIGH)
	wiringpi.pinMode(WRITE_EN, OUTPUT)

	instruct()

setup()
