from Simulator.Commands.Command import command

class Sec(command):
  
  def __init_(self, *args):
    command.__init__(self, *args)
  
  def evaluate(self, mem):
    command.evaluate(self, mem)
    
    if self.cmd == 0b01100:
      ###
      mem.setMisc("C", 1)
      
    return -1