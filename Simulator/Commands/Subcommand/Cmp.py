from Simulator.Commands.Command import command

class Cmp(command):
  
  def __init_(self, *args):
    command.__init__(self, *args)
  
  def evaluate(self, mem):
    command.evaluate(self, mem)
    
    value1 = value2 = 0
    #register case of AND
    if self.cmd == 0b11000: #all preceding bits are 0, check length to prevent conflict with '10100'
      ###
      #grab the register number from the binary command string
      #operation location 2-6 (first four bits chopped off), 7-11 reg1, 12-20 input bits 
      value1 = mem.getReg(self.reg1)
      value2 = self.val      
    elif self.cmd == 0b00010:
      ###
      #given some address: 0b10000 00001 0 10, the cmd bits are all 0, and will be discounted
      #locations 0-0 are the operation, 2-? are reg1, ?+1 - ?+6 are the bit value
      #topAdd = len(bin(self.cmd_hex)) - 8
      value1 = mem.getReg(self.reg1)
      value2 = mem.getReg(self.reg2)
    
    if (value1 - value2 < 0):
      mem.setMisc("C", 1)
    else: 
      mem.setMisc("C", 0)
    if ((value1 - value2) & 0xFF == 0x00):
      mem.setMisc("Z", 1)
    else: mem.setMisc("Z", 0)
            
    return -1