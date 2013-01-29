from Simulator.Commands.Command import command

class Lsr(command):
  
  def __init_(self, *args):
    command.__init__(self, *args)
  
  def evaluate(self, mem):
    command.evaluate(self, mem)
    
    #register case of AND
    if self.cmd == 0b01000: #all preceding bits are 0, check length to prevent conflict with '10100'
      ###
      #grab the register number from the binary command string
      #operation location 2-6 (first four bits chopped off), 7-11 reg1, 12-20 input bits 
      value1 = mem.getReg(self.reg1)
      mem.setReg(self.reg1, (mem.getMisc("C")<<7) | (value1)>>1)
      
      if ((mem.getMisc("C")<<7) | (value1)>>1 == 0):
        mem.setMisc("Z", 1)
      else: 
        mem.setMisc("Z", 0)

      mem.setMisc("C", value1&0x01)
        
    return -1