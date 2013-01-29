from Simulator.Commands.Subcommand.Call import Call
from Simulator.Commands.Subcommand.Ret import Ret

class sim(object):
  def __init__(self, command_hash, memory):
    self.memory = memory
    self.cmd_hash = command_hash
    self.interruptTriggered = False
           
    while self.memory.prgm_counter not in self.cmd_hash:
      self.memory.prgm_counter += 1
      if self.memory.prgm_counter > 1024:
        self.memory.prgm_counter = -1
        break
    else:
      if self.cmd_hash[self.memory.prgm_counter].line_num==-1:
        self.doNextStep()
    
    
  def step(self, level=0):
    if self.memory.prgm_counter == -1:
      return -1, -1, -1, self.memory.getChanged()
    if isinstance(self.cmd_hash[self.memory.prgm_counter], Call):
      level += 1
    if isinstance(self.cmd_hash[self.memory.prgm_counter], Ret):
      level -= 1
      
    self.doNextStep()
    
    if self.memory.prgm_counter == -1:
      return -1, -1, -1, self.memory.getChanged()
    
    if level > 0:
      return self.step(level)
    return self.getInitial()
      
  def run(self, pause):
    if self.memory.prgm_counter == -1:
      return [self.memory.getChanged()]
    if pause:
      return self.getInitial()
    self.doNextStep()
    if self.memory.prgm_counter == -1:
      return [self.memory.getChanged()]
    if self.cmd_hash[self.memory.prgm_counter].breakpoint:
      return self.getInitial()
    return 0
    
  def step_into(self):
    if self.memory.prgm_counter == -1:
      return -1, -1, -1, self.memory.getChanged()
    
    self.doNextStep()
      
    if self.memory.prgm_counter == -1:
      return -1, -1, -1, self.memory.getChanged()
    return self.getInitial()
  
  def addBreakpoint(self, line):
    for value in self.cmd_hash.itervalues():
      if value.line_num == line:
        value.breakpoint = True
        break
  
  def removeBreakpoint(self, line):
    for value in self.cmd_hash.itervalues():
      if value.line_num == line:
        value.breakpoint = False
        break

  def interrupt(self):
    self.interruptTriggered = True
  
  def setMem(self, mem, value):
    if mem=='PC':
      self.memory.prgm_counter = value
    else:
      self.memory.setSomething(mem, value)
  
  def getMem(self, mem):
    if mem=='IR':
      if self.memory.prgm_counter in self.cmd_hash:
        return self.cmd_hash[self.memory.prgm_counter].cmd_hex
      else:
        return -1
    else:
      return self.memory.getSomething(mem)
  
  def setActive(self, active):
    self.memory.active = active
  
  def getAddr(self):
    result = {}
    for value in self.cmd_hash.itervalues():
      result[value.line_num] = value.cmd_addr
    return result
  
  def getInitial(self):
    return self.memory.prgm_counter, self.cmd_hash[self.memory.prgm_counter].line_num, self.cmd_hash[self.memory.prgm_counter].cmd_hex, self.memory.getChanged()
    
  def doNextStep(self):
    first = True
    while self.cmd_hash[self.memory.prgm_counter].line_num == -1 or first: 
      first = False
      changed = self.cmd_hash[self.memory.prgm_counter].evaluate(self.memory)
      if changed==None or changed==-1:
        self.memory.prgm_counter += 1
        
      if self.interruptTriggered and self.memory.getMisc("I"):
        ptr = (self.memory.getMisc('StkPtr')-1) & 0xFF
        self.memory.setMisc('StkPtr', ptr)
        self.memory.setRam(ptr, self.memory.getMisc("PC"))
        self.memory.setMisc("PC", 0x3FF)
        self.memory.storeToShadow()
      
      self.interruptTriggered = False
      
      while self.memory.prgm_counter not in self.cmd_hash:
        self.memory.prgm_counter += 1
        if self.memory.prgm_counter > 1024:
          self.memory.prgm_counter = -1
          return
        
  