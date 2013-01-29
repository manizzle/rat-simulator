class inputs(object):
  
  def __init__(self):
    self.mem = [0 for i in xrange(256)]
    
  def __getitem__(self, key):
    return self.mem[key]
    
  def __setitem__(self, key, value):
    self.mem[key] = value & 0xFF