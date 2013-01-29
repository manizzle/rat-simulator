from Simulator.Commands.Command import command

class Retid(command):
  
  def __init_(self, *args):
    command.__init__(self, *args)
  
  def evaluate(self, mem):
    command.evaluate(self, mem)
    
    #note: the TY register and direct memory address is wrong to compiler, returned value is 0b11101, not 0b11100 as listed!
    if self.cmd == 0b01101:
      ptr = mem.getMisc('StkPtr')
      prgm_count = mem.getRam(ptr)
      mem.setMisc('StkPtr', (ptr + 1) & 0xFF)
      mem.setMisc('PC', prgm_count)
      
      mem.setMisc('C', mem.getMisc("SC"))
      mem.setMisc('Z', mem.getMisc("SZ"))
      
      return 1