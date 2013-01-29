from register_file import register_file
from scratchpad_mem import scratchpad_mem
from inputs import inputs

class mem_controller(object):
  def __init__(self, ram_dict, active, activeCallback): 
    self.register = register_file()
    self.ram = scratchpad_mem(ram_dict)
    self.inputs = inputs()
    
    self.carry = 0
    self.zero = 0
    self.shadow_carry = 0
    self.shadow_zero = 0
    self.interrupt = 0
    self.stack_ptr = 0x00
    self.prgm_counter = 0
    
    self.active = active
    self.activeCallback = activeCallback
    self.changedHash = {}
    
    self.mapping = {'C':'carry', 'Z':'zero', 'SC':'shadow_carry', 'SZ':'shadow_zero', 'I':'interrupt', 'StkPtr':'stack_ptr', 'PC':'prgm_counter'}
  
  def getInput(self, input):
    if self.active:
      self.inputs[input] = self.activeCallback("In"+str(input), self.inputs[input])
    return self.inputs[input]
  
  def setInput(self, input, value):
    self.inputs[input] = value
    self.changedHash["In"+str(input)] = self.inputs[input]
  
  def getReg(self, reg):
    return self.register[reg]
    
  def setReg(self, reg, value):
    self.register[reg] = value
    self.changedHash['R'+str(reg)] = self.register[reg]
    
  def getRam(self, addr):
    return self.ram[addr]
  
  def setRam(self, addr, value):
    self.ram[addr] = value
    self.changedHash['S'+str(addr)] = self.ram[addr]
    
  def getMisc(self, name):
    return getattr(self, self.mapping[name])
  
  def setMisc(self, name, value):
    setattr(self, self.mapping[name], value)
    self.changedHash[name] = getattr(self, self.mapping[name])
  
  def setOut(self, addr, value):
    self.changedHash['Out'+str(addr)] = value
  
  def setSomething(self, mem, value):
    if mem in self.mapping.keys():
      setattr(self, self.mapping[mem], value)
    elif mem.startswith('S'):
      self.ram[int(mem[1:])] = value
    elif mem.startswith('R'):
      self.register[int(mem[1:])] = value
    elif mem.startswith('I'):
      self.inputs[int(mem[2:])] = value
    else:
      print "unknown memory: "+mem
  
  def getSomething(self, mem):
    if mem in self.mapping.keys():
      return getattr(self, self.mapping[mem])
    elif mem.startswith('S'):
      return self.ram[int(mem[1:])]
    elif mem.startswith('R'):
      return self.register[int(mem[1:])]
    elif mem.startswith('I'):
      return self.inputs[int(mem[2:])]
    else:
      print "unknown memory: "+mem
  
  def getChanged(self):
    cl = self.changedHash
    self.changedHash = {}
    return cl 
  
  def storeToShadow(self):
    self.setMisc('SC', self.getMisc("C"))
    self.setMisc('C', 0)
    self.setMisc('SZ', self.getMisc("Z"))
    self.setMisc("Z", 0)
    self.setMisc("I", 0)


      