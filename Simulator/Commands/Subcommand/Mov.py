from Simulator.Commands.Command import command

class Mov(command):
  
  def __init_(self, *args):
    command.__init__(self, *args)
  
  def evaluate(self, mem):
    command.evaluate(self, mem)
    
    if self.cmd == 0b00010:
      ###
      #grab the register number from the binary command string
      #operation location 2-3 (first three bits chopped off), 4-8 reg1, 9-13 reg2 
      val = mem.getReg(self.reg2)
      mem.setReg(self.reg1, val)
      
    elif self.cmd == 0b11011:
      ###
      #grab the input binary value and write it to the given register
      #locations 2-6 are the operation, 7-11 are the register, 12-20 are the bit value
      mem.setReg(self.reg1, self.val)
    
    return -1