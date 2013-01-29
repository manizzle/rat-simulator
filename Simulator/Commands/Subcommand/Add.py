from Simulator.Commands.Command import command

class Add(command):
  
  def __init_(self, *args):
    command.__init__(self, *args)
  
  def evaluate(self, mem):
    command.evaluate(self, mem)
    
    value1 = 0
    value2 = 0
    if self.cmd == 0b10100:
      ###
      #grab the input binary value and write it to the given register
      value1 = mem.getReg(self.reg1)
      value2 = self.val
      mem.setReg(self.reg1, value1+value2)
    
    elif self.cmd == 0b00001: #all preceding bits are 0, check length to prevent conflict with '10100'
      ###
      #
      value1 = mem.getReg(self.reg1)
      value2 = mem.getReg(self.reg2)
      mem.setReg(self.reg1, value1+value2)
      
            
    if (value1 + value2) & 0xFF == 0: 
      #set zero flag 
      mem.setMisc("Z", 1)
    else:
      mem.setMisc("Z", 0)
      
    if value1 + value2 > 0xFF: 
      #set carry flag 
      mem.setMisc("C", 1)
    else:
      mem.setMisc("C", 0)
    
    return -1