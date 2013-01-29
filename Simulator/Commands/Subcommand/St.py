from Simulator.Commands.Command import command

class St(command):
  
  def __init_(self, *args):
    command.__init__(self, *args)
  
  def evaluate(self, mem):
    command.evaluate(self, mem)
    
    #note: the TY register and direct memory address is wrong to compiler, returned value is 0b11101, not 0b11100 as listed!
    if self.cmd == 0b11101:
      value1 = mem.getReg(self.reg1)
      addr = self.val
      mem.setRam(addr, value1)
                            #addr, value
    elif self.cmd == 0b00010: 
      value1 = mem.getReg(self.reg1)
      addr = mem.getReg(self.reg2)
      mem.setRam(int(addr), value1)
      
    return -1