from Simulator.Commands.Command import command

class Cli(command):
  def __init_(self, *args):
    command.__init__(self, *args)
  
  def evaluate(self, mem):
    command.evaluate(self, mem)
    
    if self.cmd == 0b01101:
      mem.setMisc("I", 0)
      