from Simulator.Commands.Command import command

class Breq(command):
  
  def __init_(self, *args):
    command.__init__(self, *args)
  
  def evaluate(self, mem):
    command.evaluate(self, mem)
    
    #note: the TY register and direct memory address is wrong to compiler, returned value is 0b11101, not 0b11100 as listed!
    if self.cmd == 0b00100 and mem.getMisc("Z") == 1:
      mem.setMisc("PC", self.jmp)
      
      return 1