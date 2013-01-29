class meta(type):
  def __new__(cls, name, bases, attr):
    if name!='command':
      command.commandList.append(name)
    return super(meta, cls).__new__(cls, name, bases, attr)

class command(object):
  __metaclass__ = meta
  commandList = []
  
  def __init__(self, line_number, command_hex, command_address):
    self.line_num = line_number
    self.cmd_hex = command_hex
    self.cmd_addr = command_address
    self.breakpoint = False
    self.cmd = (self.cmd_hex & 0x3E000) >> 13
    self.reg1 = (self.cmd_hex & 0x01F00) >> 8
    self.reg2 = (self.cmd_hex & 0x000F8) >> 3
    self.val = (self.cmd_hex & 0x000FF)
    self.jmp = (self.cmd_hex & 0x01FF8) >> 3
  
  def evaluate(self, memory):
    return -1
    
