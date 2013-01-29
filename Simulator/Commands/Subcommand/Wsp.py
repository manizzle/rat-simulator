from Simulator.Commands.Command import command

class Wsp(command):
  
  def __init_(self, *args):
    command.__init__(self, *args)
  
  def evaluate(self, mem):
    command.evaluate(self, mem)
    
    if self.cmd == 0b01010:
      #the first 8 bits are changed to the value in the specified register
      mem.setMisc('StkPtr', mem.getReg(self.reg1))
     