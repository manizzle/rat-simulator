from Simulator.Commands.Command import command

class Call(command):
  
  def __init_(self, *args):
    command.__init__(self, *args)
  
  def evaluate(self, mem):
    command.evaluate(self, mem)
    
    #note: the TY register and direct memory address is wrong to compiler, returned value is 0b11101, not 0b11100 as listed!
    if self.cmd == 0b00100:
      ptr = (mem.getMisc('StkPtr')-1) & 0xFF
      mem.setMisc('StkPtr', ptr)
      # the saved value of the PC must be indexed 1 past the current location (to avoid jumping back to the jump.
      mem.setRam(ptr, mem.getMisc("PC") + 1)
      mem.setMisc('PC', self.jmp)
    
    return 1