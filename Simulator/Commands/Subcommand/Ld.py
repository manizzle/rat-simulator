from Simulator.Commands.Command import command

class Ld(command):
  
  def __init_(self, *args):
    command.__init__(self, *args)
  
  def evaluate(self, mem):
    command.evaluate(self, mem)
    
    #note: the TY register and direct memory address is wrong to compiler, returned value is 0b11101, not 0b11100 as listed!
    if self.cmd == 0b11100:
      addr = self.val
      mem.setReg(self.reg1, mem.getRam(addr))
                            #addr, value
    elif self.cmd == 0b00010:
      addr = mem.getReg(self.reg2)
      mem.setReg(self.reg1, mem.getRam(addr))
      
    return -1