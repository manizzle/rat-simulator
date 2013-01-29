from Simulator.Commands.Command import command

class Test(command):
  
  def __init_(self, *args):
    command.__init__(self, *args)
  
  def evaluate(self, mem):
    command.evaluate(self, mem)
    
    value1 = value2 = 0
    #register case of AND
    if self.cmd == 0b10011: #all preceding bits are 0, check length to prevent conflict with '10100'
      ###
      value1 = mem.getReg(self.reg1)
      value2 = self.val
      
    elif self.cmd == 0b00000:
      ###
      value1 = mem.getReg(self.reg1)
      value2 = mem.getReg(self.reg2)

    if (value1 & value2) == 0:
      mem.setMisc("Z", 1)            
    else:
      mem.setMisc("Z", 0)
        
    return -1