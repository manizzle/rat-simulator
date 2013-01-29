from Simulator.Commands.Command import command

class Addc(command):
  
  def __init_(self, *args):
    command.__init__(self, *args)
  
  def evaluate(self, mem):
    command.evaluate(self, mem)
    
    value1 = 0
    value2 = 0
    carry = mem.getMisc("C")
    
    if self.cmd == 0b10101:
      ###
      #grab the register number from the binary command string
      #operation location 2-2 (first four bits chopped off), 3-7 reg1, 8-12 reg2 
      value1 = mem.getReg(self.reg1)
      value2 = self.val
      mem.setReg(self.reg1, value1+value2+carry)
      
    elif self.cmd == 0b00001:
      ###
      #grab the input binary value and write it to the given register
      #locations 2-6 are the operation, 7-11 are the register, 12-20 are the bit value
      value1 = mem.getReg(self.reg1)
      value2 = mem.getReg(self.reg2)
      mem.setReg(self.reg1, value1+value2+carry)
      
    if (value1+value2+carry) & 0xFF == 0: 
      #set zero flag 
      mem.setMisc("Z", 1)
    else:
      mem.setMisc("Z", 0)
        
    if value1+value2+carry > 0xFF: 
      #set carry flag 
      mem.setMisc("C", 1)
    else:
      mem.setMisc("C", 0)
    
      
    return -1
