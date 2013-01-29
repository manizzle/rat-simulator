from Simulator.Commands.Command import command

class Subc(command):
  
  def __init_(self, *args):
    command.__init__(self, *args)
  
  def evaluate(self, mem):
    command.evaluate(self, mem)
    
    value1 = value2 = 0
    carry = mem.getMisc("C")
    if self.cmd == 0b10111:
      ###
      value1 = mem.getReg(self.reg1)
      value2 = self.val
          
    elif self.cmd == 0b00001: #all preceding bits are 0, check length to prevent conflict with '10100'
      ###
      value1 = mem.getReg(self.reg1)
      value2 = mem.getReg(self.reg2)
      
    #zero flag set        
    if (value1 - value2 - carry) & 0xFF == 0: 
      mem.setMisc("Z", 1)
    else:
      mem.setMisc("Z", 0)
    #carry flag set  
    if value1 - value2 - carry < 0: 
      mem.setMisc("C", 1)
    else:
      mem.setMisc("C", 0)
    mem.setReg(self.reg1, value1-value2-carry)
      
    return -1