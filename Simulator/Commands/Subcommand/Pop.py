from Simulator.Commands.Command import command

class Pop(command):
  
  def __init_(self, *args):
    command.__init__(self, *args)
  
  def evaluate(self, mem):
    command.evaluate(self, mem)
    
    #note: the TY register and direct memory address is wrong to compiler, returned value is 0b11101, not 0b11100 as listed!
    if self.cmd == 0b01001:
      ptr = mem.getMisc('StkPtr')
      val = mem.getRam(ptr)
      addr = self.reg1
      mem.setReg(addr, val)
      ptr = (ptr+1) & 0xFF
      mem.setMisc('StkPtr', ptr)
                            #addr, value
     
    return -1
