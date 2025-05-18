import time
import smbus

I2C_ADDR = 0x27  
LCD_WIDTH = 16 
LCD_CHR = 1     
LCD_CMD = 0     
LCD_LINE_1 = 0x80 
LCD_LINE_2 = 0xC0  
LCD_BACKLIGHT = 0x08  
ENABLE = 0b00000100   
E_PULSE = 0.0002  
E_DELAY = 0.0002    

class LCD:
    def __init__(self, i2c_addr):
        self.i2c_addr = i2c_addr
        self.bus = smbus.SMBus(1)

    def init_LCD(self):
        try:
            self.send_instruction(0x33) 
            self.send_instruction(0x32) 
            self.send_instruction(0x28)  
            self.send_instruction(0x0C) 
            self.send_instruction(0x06)  
            self.clear_display()        
        except Exception as e:
            print("LCD initialization failed:", e)

    def send_byte_with_e_toggle(self, bits):
        try:
            self.bus.write_byte(I2C_ADDR, (bits | ENABLE))
            time.sleep(E_PULSE)
            self.bus.write_byte(I2C_ADDR, (bits & ~ENABLE))
            time.sleep(E_DELAY)
        except Exception as e:
            print("Error sending byte with E toggle:", e)

    def set_data_bits(self, bits, mode):
        upper_nibble = (bits & 0xF0) | mode | LCD_BACKLIGHT
        lower_nibble = ((bits << 4) & 0xF0) | mode | LCD_BACKLIGHT
        self.send_byte_with_e_toggle(upper_nibble)
        self.send_byte_with_e_toggle(lower_nibble)

    def send_instruction(self, byte):
        self.set_data_bits(byte, LCD_CMD)

    def send_character(self, byte):
        self.set_data_bits(byte, LCD_CHR)

    def send_string(self, message, line):
        if line == 1:
            self.send_instruction(LCD_LINE_1)
        elif line == 2:
            self.send_instruction(LCD_LINE_2)

        if len(message) <= LCD_WIDTH:
            for char in message:
                self.send_character(ord(char))
        else:
            for i in range(len(message) - LCD_WIDTH + 1):
                self.send_instruction(LCD_LINE_1 if line == 1 else LCD_LINE_2)
                substring = message[i:i + LCD_WIDTH]
                for char in substring:
                    self.send_character(ord(char))
                time.sleep(0.5) 

    def clear_display(self):
        self.send_instruction(0x01)
        time.sleep(0.002) 
