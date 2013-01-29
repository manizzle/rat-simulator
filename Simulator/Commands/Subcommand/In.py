from Simulator.Commands.Command import command

class In(command):
  
  def __init_(self, *args):
    command.__init__(self, *args)
  
  def evaluate(self, mem):
    command.evaluate(self, mem)
    
    if self.cmd == 0b11001:
      ###
	  val = mem.getInput(self.val)
	  mem.setReg(self.reg1, val)
      
    return -1