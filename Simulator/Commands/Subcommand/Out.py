from Simulator.Commands.Command import command

class Out(command):
  
  def __init_(self, *args):
    command.__init__(self, *args)
  
  def evaluate(self, mem):
    command.evaluate(self, mem)
    
    if self.cmd == 0b11010:
      ###
	  val = mem.getReg(self.reg1)
	  mem.setOut(self.val, val)
      
    return -1