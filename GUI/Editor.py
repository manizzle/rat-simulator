import wx
import wx.stc as stc
import os
from subprocess import Popen
from Parser import parser
from Simulator.Sim import sim
from Simulator.Commands.Command import command

class editor(wx.Frame):
  #highlighting constants
  mathList = "add addc and asr cmp exor lsl ror rol lsr or sec sub subc test clc"
  cpuList = "brcc brcs breq brn brne call ld mov out in st pop push ret wsp sei cli retie retid"
  directives = ".cseg .dseg .org .equ .def .byte .db"
  registers = " ".join(['r'+str(i) for i in range(32)])
  
  def __init__(self, version):
    wx.Frame.__init__(self, None, wx.ID_ANY, title='RAT Sim')
    
    self.version = version
    self.path = ''
    self.parser = parser()
    self.sim = None
    self.active = True
    self.running = False
    self.pause = False
    
    self.currentLine = -1
    self.memoryChanged = []
    
    self.font = wx.Font(9,wx.FONTFAMILY_TELETYPE,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_NORMAL)
        
    self.panel = wx.Panel(self, wx.ID_ANY)
    self.topSizer = wx.BoxSizer(wx.VERTICAL)
    self.setupToolBar()
    
    self.backColor = self.panel.GetBackgroundColour()
        
    #Sizer below the tool bar
    self.bottomSizer = wx.BoxSizer(wx.HORIZONTAL)
    self.topSizer.Add(self.bottomSizer, 1, wx.BOTTOM|wx.EXPAND, 5)

    #to hold the text box and I/O window
    innerLeftSizer = wx.BoxSizer(wx.VERTICAL)
    self.bottomSizer.Add(innerLeftSizer, 1, wx.RIGHT|wx.EXPAND, 5)
    
    textPaneSizer = wx.BoxSizer(wx.HORIZONTAL)
    innerLeftSizer.Add(textPaneSizer, 1, wx.EXPAND)
    
    self.addressPanel = wx.ScrolledWindow(self.panel, style=wx.SUNKEN_BORDER)
    vsizer = wx.BoxSizer(wx.VERTICAL)
    self.addressText = wx.TextCtrl(self.addressPanel, size=(36,-1), style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_NO_VSCROLL|wx.NO_BORDER)
    self.addressText.SetBackgroundColour(self.backColor)
    self.addressText.SetFont(self.font)
    vsizer.Add(self.addressText, 1, wx.EXPAND)
    self.addressPanel.SetSizer(vsizer)
    
    textPaneSizer.Add(self.addressPanel, 0, wx.EXPAND|wx.ALIGN_TOP|wx.RIGHT, 2)
    self.addressStart = 0
    self.addressPanel.Hide()
    
    #where the file shows up    
    self.mainTextPane = stc.StyledTextCtrl(parent=self.panel, id=2000)# pos=(2,30))
    self.mainTextPane.SetMarginType(0, stc.STC_MARGIN_NUMBER)
    self.mainTextPane.SetMarginWidth(0, 32)
    self.mainTextPane.SetMarginWidth(1, 14)
    self.mainTextPane.SetMarginSensitive(0,True)
    self.mainTextPane.SetMarginSensitive(1,True)
    self.mainTextPane.SetTabWidth(4)
    #self.mainTextPane.SetUseTabs(False)
    
    face = self.font.GetFaceName()
    size = self.font.GetPointSize()
    self.mainTextPane.StyleSetSpec(stc.STC_STYLE_DEFAULT,"face:%s,size:%d" % (face, size))
    
    self.mainTextPane.MarkerDefine(0, stc.STC_MARK_ROUNDRECT)
    self.mainTextPane.MarkerSetForeground(0, (0, 0, 0))
    self.mainTextPane.MarkerSetBackground(0, (255, 0, 0))
    
    self.mainTextPane.MarkerDefine(1, stc.STC_MARK_BACKGROUND)
    self.mainTextPane.MarkerSetBackground(1, (255, 255, 100))
    
    self.mainTextPane.SetLexer(stc.STC_LEX_ASM)
    
    self.mainTextPane.SetKeyWords(0, self.cpuList)
    self.mainTextPane.SetKeyWords(1, self.mathList)
    self.mainTextPane.SetKeyWords(2, self.registers)
    self.mainTextPane.SetKeyWords(3, self.directives)
    
    self.mainTextPane.StyleSetSpec(stc.STC_ASM_COMMENT, "fore:#008000")
    self.mainTextPane.StyleSetSpec(stc.STC_ASM_NUMBER, "fore:#800040")
    self.mainTextPane.StyleSetSpec(stc.STC_ASM_CPUINSTRUCTION, "bold,fore:#0000FF")
    self.mainTextPane.StyleSetSpec(stc.STC_ASM_MATHINSTRUCTION, "bold,fore:#5E00C0")
    self.mainTextPane.StyleSetSpec(stc.STC_ASM_REGISTER, "fore:#0080C0")
    self.mainTextPane.StyleSetSpec(stc.STC_ASM_DIRECTIVE, "fore:#804000")
    
    self.mainTextPane.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)
    
    self.findReplace = None
    self.Bind(wx.EVT_FIND, self.onFindThing)
    self.Bind(wx.EVT_FIND_NEXT, self.onFindThing)
    self.Bind(wx.EVT_FIND_REPLACE, self.onReplaceThing)
    self.Bind(wx.EVT_FIND_REPLACE_ALL, self.onReplaceAll)
    self.Bind(wx.EVT_FIND_CLOSE, self.onFindClose)
            
    #self.mainTextPane.SetIndentationGuides(True)
    #self.mainTextPane.StyleSetSpec(stc.STC_STYLE_INDENTGUIDE, "fore:FF0000")
    
    textPaneSizer.Add(self.mainTextPane, 1, wx.EXPAND)
    
    self.Bind(stc.EVT_STC_PAINTED, self.onUpdateMargin)
    
    self.console = wx.TextCtrl(parent=self.panel, size=wx.Size(600,100), style=wx.TE_MULTILINE|wx.TE_READONLY)
    innerLeftSizer.Add(self.console, 0, wx.EXPAND|wx.ALL, 2)
    self.console.Hide()
    
    self.output = wx.ScrolledWindow(parent=self.panel, style=wx.SUNKEN_BORDER)
    innerLeftSizer.Add(self.output, 0, wx.EXPAND|wx.ALL, 2)
    
    #holds the FRW, Reg Window, and Data Memory
    self.innerRightSizer = wx.BoxSizer(wx.HORIZONTAL)
    self.sashWindow = wx.SashWindow(self.panel, style=wx.NO_BORDER)
    self.sashWindow.SetSashVisible(wx.SASH_LEFT, True)
    
    self.setupRegistry()
    self.setupMenu()
    
    self.sashWindow.SetSizerAndFit(self.innerRightSizer)
    self.sashWindow.Layout()
    self.Bind(wx.EVT_SASH_DRAGGED_RANGE, self.onSash)
    self.bottomSizer.Add(self.sashWindow, 0, wx.EXPAND)
    
    self.status = self.CreateStatusBar()
    self.status.SetFieldsCount(2)
    self.status.SetStatusWidths([-1,100])
    self.Bind(stc.EVT_STC_UPDATEUI, self.onUpdateStatus)
    
    self.panel.SetSizer(self.topSizer)
    self.topSizer.Fit(self.panel)
    self.panel.SetAutoLayout(True)
    self.Fit()
    
    self.Bind(stc.EVT_STC_MARGINCLICK, self.onBreak, id=2000)
    
    self.timer = wx.Timer(self, -1)
    self.Bind(wx.EVT_TIMER, self.onTimer, id=self.timer.GetId())
    self.Maximize()
    
    self.width = 0
    self.Bind(wx.EVT_SIZE, self.onResize)
    
    self.SetIcon(wx.Icon('media/ratSim.ico', wx.BITMAP_TYPE_ICO))
    
  def setupRegistry(self):
    self.memory = {}
    inputLength = 9
    spacing = 5
    height = -self.font.GetPixelSize()[1]+3
    
    self.variableKeys = ["PC","IR","StkPtr","I","C","SC","Z","SZ"]
    variableValues = ["PC: ","Inst. Reg: ","Stack Ptr: ","Interrupt: ","C: ","Shadow C: ","Z: ","Shadow Z: "]
    self.variableLengths = [3,5,2,1,1,1,1,1]
    variableSizes = [3,4,2,2,2,2,2,2]
    
    p = wx.Panel(self.output)
    sizer = wx.GridBagSizer()
    for i in range(8):
      st = wx.StaticText(p,wx.ID_ANY,variableValues[i])
      st.SetFont(self.font)
      sizer.Add(st, (i%2+1,i/2*3+1))
      self.memory[self.variableKeys[i]] = wx.TextCtrl(p, value='0'*self.variableLengths[i], size=(inputLength*variableSizes[i],height),style=wx.NO_BORDER)
      self.memory[self.variableKeys[i]].SetFont(self.font)
      self.memory[self.variableKeys[i]].SetMaxLength(self.variableLengths[i])
      self.memory[self.variableKeys[i]].SetBackgroundColour(self.backColor)
      self.memory[self.variableKeys[i]].Bind(wx.EVT_KILL_FOCUS, self.onChangeMem)
      sizer.Add(self.memory[self.variableKeys[i]],(i%2+1,i/2*3+2),flag=wx.BOTTOM|wx.RIGHT,border=spacing)
    sizer.AddSpacer((10,0),(0,3))
    sizer.AddSpacer((10,0),(0,6))
    sizer.AddSpacer((10,0),(0,9))
    sizer.AddSpacer((2,2),(0,0))
    sizer.AddSpacer((2,2),(3,0))
    sizer.AddSpacer((2,2),(0,12))
    p.SetSizer(sizer)
    v = wx.BoxSizer(wx.VERTICAL)
    v.Add(p, 0, wx.EXPAND)
    self.output.SetSizer(v)
    self.output.SetScrollbars(1,0,0,0)
    
    #registry
    vertical = wx.BoxSizer(wx.VERTICAL)
    vertical.Add(wx.StaticText(self.sashWindow, wx.ID_ANY, "Registers:"), 0, wx.EXPAND, 0)
    regPanel = wx.ScrolledWindow(self.sashWindow, size=(300,-1), style=wx.BORDER_SUNKEN)
    regSizer = wx.BoxSizer(wx.VERTICAL)
    p = wx.Panel(regPanel)
    
    for i in range(32):
      s = wx.BoxSizer(wx.HORIZONTAL)
      st = wx.StaticText(p,wx.ID_ANY,str(i)+": "+' '*(2-len(str(i))))
      st.SetFont(self.font)
      s.Add(st, 0)
      self.memory["R"+str(i)] = wx.TextCtrl(p, value="00", size=(inputLength*2,height),style=wx.NO_BORDER)
      self.memory["R"+str(i)].SetFont(self.font)
      self.memory["R"+str(i)].SetMaxLength(2)
      self.memory["R"+str(i)].SetBackgroundColour(self.backColor)
      self.memory["R"+str(i)].Bind(wx.EVT_KILL_FOCUS, self.onChangeMem)
      s.Add(self.memory["R"+str(i)],1, wx.RIGHT, spacing)
      s.AddSpacer(2)
      regSizer.Add(s,1, wx.BOTTOM, spacing)
    p.SetSizer(regSizer)
    v = wx.BoxSizer(wx.VERTICAL)
    v.Add(p, 0, wx.EXPAND)
    regPanel.SetSizer(v)
    regPanel.SetScrollbars(0,2,0,0)
    vertical.Add(regPanel, 1, wx.EXPAND|wx.ALL,5)
    self.innerRightSizer.Add(vertical, 0, wx.EXPAND|wx.ALL, 5)
    
    #memory
    vertical = wx.BoxSizer(wx.VERTICAL)
    vertical.Add(wx.StaticText(self.sashWindow, wx.ID_ANY, "Memory:"), 0, wx.EXPAND, 0)
    self.memPanel = wx.ScrolledWindow(self.sashWindow, size=(1000,-1), style=wx.BORDER_SUNKEN)
    memSizer = wx.BoxSizer(wx.VERTICAL)
    p = wx.Panel(self.memPanel)
    
    for i in xrange(32):
      s = wx.BoxSizer(wx.HORIZONTAL)
      st = wx.StaticText(p,wx.ID_ANY,'0'*(2-len(hex(i*8)[2:]))+hex(i*8)[2:].upper()+": ")
      st.SetFont(self.font)
      s.Add(st, 0)
      
      for x in range(8):
        self.memory["S"+str(i*8+x)] = wx.TextCtrl(p, value="000", size=(inputLength*3,height),style=wx.NO_BORDER)
        self.memory["S"+str(i*8+x)].SetMaxLength(3)
        self.memory["S"+str(i*8+x)].SetFont(self.font)
        self.memory["S"+str(i*8+x)].SetBackgroundColour(self.backColor)
        self.memory["S"+str(i*8+x)].Bind(wx.EVT_KILL_FOCUS, self.onChangeMem)
        s.Add(self.memory["S"+str(i*8+x)], 1, wx.RIGHT, spacing)  
      s.AddSpacer(2)
      memSizer.Add(s,1, wx.BOTTOM, spacing)
    p.SetSizer(memSizer)
    v = wx.BoxSizer(wx.VERTICAL)
    v.Add(p, 0, wx.EXPAND)
    self.memPanel.SetSizer(v)
    self.memPanel.SetScrollbars(1,15,0,0)
    self.memPanel.SetMinSize((310,-1))
    self.memPanel.SetSize((310,-1))
    self.memPanel.SetMaxSize((310,-1))
    vertical.Add(self.memPanel, 1, wx.EXPAND|wx.ALL,5)
    self.innerRightSizer.Add(vertical, 1, wx.EXPAND|wx.ALL, 5)
    
    #input 
    vertical = wx.BoxSizer(wx.VERTICAL)
    vertical.Add(wx.StaticText(self.sashWindow, wx.ID_ANY, "Inputs:"), 0, wx.EXPAND, 0)
    inPanel = wx.ScrolledWindow(self.sashWindow, style=wx.BORDER_SUNKEN)
    inSizer = wx.BoxSizer(wx.VERTICAL)
    p = wx.Panel(inPanel)
    
    for i in xrange(256):
      s = wx.BoxSizer(wx.HORIZONTAL)
      st = wx.StaticText(p,wx.ID_ANY,'0'*(2-len(hex(i)[2:]))+hex(i)[2:].upper()+": ")
      st.SetFont(self.font)
      s.Add(st, 0)
      self.memory["In"+str(i)] = wx.TextCtrl(p, value="00", size=(inputLength*2,height),style=wx.NO_BORDER)
      self.memory["In"+str(i)].SetFont(self.font)
      self.memory["In"+str(i)].SetMaxLength(2)
      self.memory["In"+str(i)].SetBackgroundColour(self.backColor)
      self.memory["In"+str(i)].Bind(wx.EVT_KILL_FOCUS, self.onChangeMem)
      s.Add(self.memory["In"+str(i)],1, wx.RIGHT, spacing)
      s.AddSpacer(2)
      inSizer.Add(s,1, wx.BOTTOM, spacing)
    p.SetSizer(inSizer)
    v = wx.BoxSizer(wx.VERTICAL)
    v.Add(p, 0, wx.EXPAND)
    inPanel.SetSizer(v)
    sizer = wx.BoxSizer(wx.VERTICAL)
    inPanel.SetScrollbars(0,10,0,0)
    vertical.Add(inPanel, 1, wx.EXPAND|wx.ALL,5)
    self.innerRightSizer.Add(vertical, 0, wx.EXPAND|wx.ALL, 5)
    
    #output 
    vertical = wx.BoxSizer(wx.VERTICAL)
    vertical.Add(wx.StaticText(self.sashWindow, wx.ID_ANY, "Outputs:"), 0, wx.EXPAND, 0)
    outPanel = wx.ScrolledWindow(self.sashWindow, style=wx.BORDER_SUNKEN)
    outSizer = wx.BoxSizer(wx.VERTICAL)
    p = wx.Panel(outPanel)
    
    for i in xrange(256):
      s = wx.BoxSizer(wx.HORIZONTAL)
      st = wx.StaticText(p,wx.ID_ANY,'0'*(2-len(hex(i)[2:]))+hex(i)[2:].upper()+": ")
      st.SetFont(self.font)
      s.Add(st, 0)
      self.memory["Out"+str(i)] = wx.TextCtrl(p, value="00", size=(inputLength*2,height),style=wx.NO_BORDER)
      self.memory["Out"+str(i)].SetFont(self.font)
      self.memory["Out"+str(i)].SetMaxLength(2)
      self.memory["Out"+str(i)].SetBackgroundColour(self.backColor)
      self.memory["Out"+str(i)].Bind(wx.EVT_KILL_FOCUS, self.onChangeMem)
      s.Add(self.memory["Out"+str(i)],1, wx.RIGHT, spacing)
      s.AddSpacer(2)
      outSizer.Add(s,1, wx.BOTTOM, spacing)
    p.SetSizer(outSizer)
    v = wx.BoxSizer(wx.VERTICAL)
    v.Add(p, 0, wx.EXPAND)
    outPanel.SetSizer(v)
    sizer = wx.BoxSizer(wx.VERTICAL)
    outPanel.SetScrollbars(0,10,0,0)
    vertical.Add(outPanel, 1, wx.EXPAND|wx.ALL,5)
    self.innerRightSizer.Add(vertical, 0, wx.EXPAND|wx.ALL, 5)
    

  def setupMenu(self):
    menubar = wx.MenuBar()
    file = wx.Menu()
    edit = wx.Menu()
    help = wx.Menu()
    
    file.Append(100, '&New\tCtrl+N', 'Create a new file')
    file.Append(101, '&Open\tCtrl+O', 'Open an existing file')
    file.Append(102, '&Save\tCtrl+S', 'Save the file')
    file.Append(103, 'Save &As...\tCtrl+Shift+S', 'Save the file as a new file')
    file.Append(104, 'Find\tCtrl+F', 'Opens the find replace dialog')
    file.AppendSeparator()
    quit = wx.MenuItem(file, 105, '&Quit\tCtrl+Q', 'Quit the Application')
    file.AppendItem(quit)
    
    edit.Append(200, 'Assemble\tF5', 'Assemble and run')
    edit.Append(205, 'Halt\tF6', 'Stop program execution')
    edit.AppendSeparator()
    edit.Append(201, 'Step\tF1', 'Step over one line')
    edit.Append(202, 'Step Into\tF2', 'Step into next line')
    edit.Append(203, 'Run\tF3', 'Run until a break or interrupt')
    edit.Append(204, 'Break\tF4', 'Break program flow')
    edit.Append(206, 'Interrupt\tF7', 'Generate interrupt signal')
    edit.AppendSeparator()
        
    submenu2 = wx.Menu()
    submenu2.Append(221, 'Active Mode\tCtrl+W', kind=wx.ITEM_RADIO)
    submenu2.Append(222, 'Passive Mode\tCtrl+E', kind=wx.ITEM_RADIO)
    edit.AppendMenu(206, 'Input Mode', submenu2)
    
    help.Append(300, 'About', 'Program Information')
    help.Append(302, 'Ratasm Documentation\tF12', 'The latest Ratasm docs')
    help.Append(301, 'Command List', 'List of commands')
    
    menubar.Append(file, '&File')
    menubar.Append(edit, '&Debug')
    menubar.Append(help, '&Help')
    
    self.Bind(wx.EVT_MENU, self.onNew, id=100)
    self.Bind(wx.EVT_MENU, self.onOpen, id=101)
    self.Bind(wx.EVT_MENU, self.onSave, id=102)
    self.Bind(wx.EVT_MENU, self.onSaveAs, id=103)
    self.Bind(wx.EVT_MENU, self.onFind, id=104)
    self.Bind(wx.EVT_MENU, self.onQuit, id=105)
    
    self.Bind(wx.EVT_MENU, self.onAsm, id=200)
    self.Bind(wx.EVT_MENU, self.onStep, id=201)
    self.Bind(wx.EVT_MENU, self.onStepInto, id=202)
    self.Bind(wx.EVT_MENU, self.onRun, id=203)
    self.Bind(wx.EVT_MENU, self.onHalt, id=204)
    self.Bind(wx.EVT_MENU, self.onStop, id=205)
    self.Bind(wx.EVT_MENU, self.onInterrupt, id=206)
        
    self.Bind(wx.EVT_MENU, self.onActive, id=221)
    self.Bind(wx.EVT_MENU, self.onPassive, id=222)
    
    self.Bind(wx.EVT_MENU, self.onAbout, id=300)
    self.Bind(wx.EVT_MENU, self.onCommandList, id=301)
    self.Bind(wx.EVT_MENU, self.onRatDoc, id=302)
        
    self.SetMenuBar(menubar)
  
  def setupToolBar(self):
    self.toolbar = wx.ToolBar(self.panel)
    self.toolbar.AddSimpleTool(1101, wx.Image('media/new.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'New (Ctrl+N)', '')
    self.toolbar.AddSimpleTool(1102, wx.Image('media/open.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Open (Ctrl+O)', '')
    self.toolbar.AddSimpleTool(1103, wx.Image('media/save.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Save (Ctrl+S)', '')
    self.toolbar.AddSeparator()
    
    self.toolbar.AddSimpleTool(1104, wx.Image('media/function.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Assemble (F5)', '')
    self.toolbar.AddSimpleTool(1109, wx.Image('media/stop.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Halt (F6)', '')
    self.toolbar.AddSeparator()
    
    self.toolbar.AddSimpleTool(1105, wx.Image('media/bmark_next.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Step (F1)', '')
    self.toolbar.AddSimpleTool(1106, wx.Image('media/forward.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Step Into (F2)', '')
    self.toolbar.AddSimpleTool(1107, wx.Image('media/bin_file.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Run (F3)', '')
    self.toolbar.AddSimpleTool(1108, wx.Image('media/pause.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Break (F4)', '')
    self.toolbar.AddSimpleTool(1111, wx.Image('media/log.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Interrupt (F7)', '')
    self.toolbar.AddSeparator()
    self.toolbar.AddSimpleTool(1110, wx.Image('media/quit.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Quit (Ctrl+Q)', '')
    
    self.toolbar.SetToolBitmapSize(wx.Size(16,16))
    
    self.Bind(wx.EVT_TOOL, self.onNew, id=1101)
    self.Bind(wx.EVT_TOOL, self.onOpen, id=1102)
    self.Bind(wx.EVT_TOOL, self.onSave, id=1103)
    self.Bind(wx.EVT_TOOL, self.onAsm, id=1104)
    self.Bind(wx.EVT_TOOL, self.onStep, id=1105)
    self.Bind(wx.EVT_TOOL, self.onStepInto, id=1106)
    self.Bind(wx.EVT_TOOL, self.onRun, id=1107)
    self.Bind(wx.EVT_TOOL, self.onHalt, id=1108)
    self.Bind(wx.EVT_TOOL, self.onStop, id=1109)
    self.Bind(wx.EVT_TOOL, self.onQuit, id=1110)
    self.Bind(wx.EVT_TOOL, self.onInterrupt, id=1111)
        
    self.topSizer.Add(self.toolbar, 0, wx.EXPAND|wx.BOTTOM, 5)
    self.toolbar.Realize()

  def onStep(self, evt):
    if self.sim == None: return
    
    self.updateFields(*self.sim.step())
  
  def onStepInto(self, evt):
    if self.sim == None: return
    
    self.updateFields(*self.sim.step_into())
  
  def onRun(self, evt):
    self.running = True
    self.timer.Start(1)
    self.status.SetStatusText('Running...')
  
  def onInterrupt(self, evt):
    if self.sim==None: return
    self.sim.interrupt()
      
  def onHalt(self, evt):
    self.pause = True
  
  def onNew(self, evt):
    if self.mainTextPane.GetModify():
      dlg = wx.MessageDialog(self, 'Are you sure to create a new file?\nYou will lose all unsaved data.', 'Please Confirm', wx.YES_NO|wx.NO_DEFAULT | wx.ICON_QUESTION)
      if dlg.ShowModal() == wx.ID_YES:
        self.mainTextPane.ClearAll()
        self.path = ''
    else:
      self.mainTextPane.ClearAll()
      self.path = ''
    self.killSim()
    
  def onSave(self, evt):
    if self.path == '':
      self.onSaveAs(None)
    else:
      if not self.mainTextPane.SaveFile(self.path):
        dlg = wx.MessageDialog(self, 'Error saving file at location:\n' + self.path)
        self.path = ''
        dlg.ShowModal()
    self.killSim()
      
  def onSaveAs(self, evt):
    wcd='Assembly files (*.asm)|*.asm|All files(*)|*'
    if self.path == '':
      dir = os.getcwd()
    else:
      dir = os.path.dirname(self.path)
    save_dlg = wx.FileDialog(self, message='Save file as...', defaultDir=dir, defaultFile='', wildcard=wcd, style=wx.SAVE|wx.OVERWRITE_PROMPT)
    
    if save_dlg.ShowModal() == wx.ID_OK:
      self.path = save_dlg.GetPath()
      if not self.mainTextPane.SaveFile(self.path):
        dlg = wx.MessageDialog(self, 'Error saving file at location:\n' + self.path)
        self.path = ''
        dlg.ShowModal()
    self.SetTitle("RAT Sim - "+self.path)
    self.killSim()
    save_dlg.Destroy()
  
  def onOpen(self, evt):
    if self.mainTextPane.GetModify():
      dlg = wx.MessageDialog(self, 'Are you sure to open a different file?\nYou will lose all unsaved data.', 'Please Confirm', wx.YES_NO|wx.NO_DEFAULT | wx.ICON_QUESTION)
      if dlg.ShowModal() != wx.ID_YES:
        return
    
    wcd='Assembly files (*.asm)|*.asm|All files(*)|*'
    if self.path == '':
      dir = os.getcwd()
    else:
      dir = os.path.dirname(self.path)
      
    open_dlg = wx.FileDialog(self, message='Choose a file...', defaultDir=dir, defaultFile='', wildcard=wcd, style=wx.OPEN)
    if open_dlg.ShowModal() == wx.ID_OK:
      self.path = open_dlg.GetPath()
      if not os.path.exists(self.path):
        dlg = wx.MessageDialog(self, 'Error loading file at location:\n' + self.path)
        dlg.ShowModal()
      else:
        self.mainTextPane.LoadFile(self.path)
        self.killSim()
        self.hideConsole()
        self.SetTitle("RAT Sim - "+self.path)
  
  def onAbout(self, evt):
    dlg = wx.MessageDialog(self, '\tRAT Sim\t\n\tVersion {0:s}\t\n\tCopyright Tim Peters and Doug Gallatin\t\n'.format(self.version), 'About', wx.OK)
    dlg.ShowModal()
    dlg.Destroy()
    
  def onFind(self, evt):
    if self.findReplace==None:
      data = wx.FindReplaceData()
      data.SetFindString(self.mainTextPane.GetSelectedText())
      self.findReplace = wx.FindReplaceDialog(self, data, "Find & Replace", wx.FR_REPLACEDIALOG)
      self.findReplace.data = data  # save a reference to it...
      self.findReplace.Show(True)
    else:
      self.findReplace.GetData().SetFindString(self.mainTextPane.GetSelectedText())
      self.findReplace.SetFocus()
      self.findReplace.Show(True)
      
  def onFindThing(self, evt):
    str = evt.GetFindString()
    pos = self.findOccurence(str,evt.GetFlags())
    #self.mainTextPane.GotoPos(pos)
    self.mainTextPane.SetSelection(pos, pos+len(str))
    
  def onReplaceThing(self, evt):    
    if self.mainTextPane.GetSelectedText().lower() == evt.GetFindString().lower():
      self.mainTextPane.ReplaceSelection(evt.GetReplaceString())
    self.onFindThing(evt)
    
  def onReplaceAll(self, evt):
    strin = evt.GetFindString()
    repl = evt.GetReplaceString()
    flags = evt.GetFlags()
    self.mainTextPane.SetCurrentPos(0)
    count = 0
    while True:
      pos = self.findOccurence(strin, flags)
      if pos==-1: break
      self.mainTextPane.SetSelection(pos, pos+len(strin))
      self.mainTextPane.ReplaceSelection(repl)
      count += 1
      
    dlg = wx.MessageDialog(self, 'replaced '+str(count)+' occurances of '+strin, 'Replace All', wx.OK)
    dlg.ShowModal()
    dlg.Destroy()
  
  def findOccurence(self, str, flags):
    f = 0
    if wx.FR_WHOLEWORD & flags:
      f |= stc.STC_FIND_WHOLEWORD
    if wx.FR_MATCHCASE & flags:
      f |= stc.STC_FIND_MATCHCASE
    
    return self.mainTextPane.FindText(self.mainTextPane.GetCurrentPos(),self.mainTextPane.GetLength(), str, f)
  
  def onFindClose(self, evt):
    self.findReplace.Destroy()
    self.findReplace = None
      
  def onCommandList(self, evt):
    s = 'Command List:\n'
    for i, c in enumerate(command.commandList):
      s += c.ljust(4)+' \t'
      if i%3 == 2: s+='\n'
    dlg = wx.MessageDialog(self, s, 'Command List', wx.OK)
    dlg.ShowModal()
    dlg.Destroy()
  
  def onRatDoc(self, evt):
    Popen('"RATASM\\RatDoc.pdf"', shell=True)
  
  def onAsm(self, evt):
    self.killSim()
    self.StatusBar.SetStatusText("Assembling...")
    if self.mainTextPane.GetModify():
      self.onSave(None)

    result = self.parser.parse(self.path, self.active, self.activeCallback)
    if isinstance(result, sim):
      self.sim = result
      for i in xrange(self.mainTextPane.GetLineCount()):
        if self.mainTextPane.MarkerGet(i)&0x01:
          self.sim.addBreakpoint(i+1)
      self.hideConsole()
      self.updateFields(*self.sim.getInitial())
      self.mainTextPane.MarkerAdd(self.currentLine, 1)
    
      height = self.mainTextPane.TextHeight(0)
      mapping = self.sim.getAddr()
      txt = ''
      for i in xrange(self.mainTextPane.GetLineCount()+1):
        if i not in mapping:
          txt += '\n'
        else:
          txt += "{0:03X}\n".format(mapping[i])      
          
      self.addressText.SetValue(txt)
      self.addressText.SetMinSize((27,height*i*1.1))
      self.addressText.SetSize((27,height*i*1.1))
      self.addressText.SetMaxSize((27,height*i*1.1))
      self.addressPanel.SetMinSize((27,height*i*1.1))
      self.addressPanel.SetSize((27,height*i*1.1))
      self.addressPanel.SetMaxSize((27,height*i*1.1))
      self.addressPanel.Show()
      self.addressPanel.Layout()
      self.bottomSizer.Layout()
            
      self.setMemory('StkPtr',self.sim.getMem('StkPtr'),False)
      
    else:
      self.killSim()
      self.showConsole(result)
    self.StatusBar.SetStatusText('')
        
  def onActive(self, evt):
    self.active = True
    if self.sim:
      self.sim.setActive(True)
  
  def onPassive(self, evt):
    self.active = False
    if self.sim:
      self.sim.setActive(False)
  
  def onBreak(self,evt):
    line = 0
    chars = evt.GetPosition()
    c = 0
    while c < chars:
      c += len(self.mainTextPane.GetLine(line))
      line += 1
      
    if self.mainTextPane.MarkerGet(line)&0x01:
      self.mainTextPane.MarkerDelete(line, 0)
      if self.sim:
        self.sim.removeBreakpoint(line+1)
    else:
      self.mainTextPane.MarkerAdd(line, 0)
      if self.sim:
        self.sim.addBreakpoint(line+1)
  
  def onUpdateMargin(self, evt):
    if self.sim==None: return
    start = self.mainTextPane.GetFirstVisibleLine()+1
    if start==self.addressStart: return
    height = self.mainTextPane.TextHeight(0)
    self.addressPanel.ScrollWindow(0, (self.addressStart-start)*height)
    self.addressStart = start
    self.addressPanel.Refresh()
  
  def onKeyPress(self, evt):
    key = evt.GetKeyCode()
    
    if key in [wx.WXK_NUMPAD_ENTER, wx.WXK_RETURN]:      
      line = 0
      chars = self.mainTextPane.GetCurrentPos()
      c = 0
      while c < chars:
        c += len(self.mainTextPane.GetLine(line))
        line += 1
      self.mainTextPane.ReplaceSelection('')
      count = self.mainTextPane.GetLineIndentation(line-1)
      tabs = self.mainTextPane.GetTabWidth()
      self.mainTextPane.AddText('\n'+(count/tabs)*'\t'+(count%tabs)*' ')
    else:
      evt.Skip()
        
  def onUpdateStatus(self, evt):
    line = 0
    chars = self.mainTextPane.GetCurrentPos()
    c = 0
    count = self.mainTextPane.GetLineCount()
    while c <= chars and  count > line:
      c += len(self.mainTextPane.GetLine(line))
      line += 1
    self.status.SetStatusText('('+str(line)+','+str(len(self.mainTextPane.GetLine(line-1))-c+chars+1)+')',1)
  
  def onSash(self, evt):
    self.adjustSize(evt.GetDragRect().width)
  
  def adjustSize(self, width):
    if width > self.width: width = self.width
    if width < 280 and width!=-1: width = 280
    
    self.sashWindow.SetMinSize((width, -1))
    self.sashWindow.SetMaxSize((width, -1))
    self.sashWindow.SetSize((width, -1))
    self.sashWindow.Layout()
    self.panel.Layout()
    self.sashWindow.Refresh()
  
  def onResize(self, evt):
    evt.Skip()
    self.adjustSize(-1)
    if self.width == 0:
      self.width = self.innerRightSizer.GetMinSize()[0]    
    
  def onTimer(self, evt):
    if self.running and self.sim:
      args = self.sim.run(self.pause)
      if args == 0:
        return
      
      if len(args)==1:
        for mem, value in args[0].iteritems():
          self.setMemory(mem, value)
        for i in xrange(self.mainTextPane.GetLineCount()):
          self.mainTextPane.MarkerDelete(i, 1)
        self.timer.Stop()
        self.status.SetStatusText("Program Execution Completed")
        self.running = False
        self.pause = False
        
      else:
        self.running = False
        self.pause = False
        self.status.SetStatusText("")
        self.timer.Stop()
        self.updateFields(*args)
  
  def onChangeMem(self, evt):
    if self.sim == None: return
    
    obj = evt.GetEventObject()
    for key, value in self.memory.iteritems():
      if value is obj:
        if key.startswith("Out"): return
        
        try:
          val = int(obj.GetValue(),16)
          if val < 0 or key=='IR':
            raise ValueError()
          if key in ['C','I','Z','SC','SZ'] and val > 1:
            raise ValueError()
        except ValueError:
          self.setMemory(key, self.sim.getMem(key), False)
          return
        
        self.sim.setMem(key, val)
        self.setMemory(key, self.sim.getMem(key), False)
        break
          
  def onStop(self, evt):
    self.killSim()
    
  def onQuit(self, evt):
    dlg = wx.MessageDialog(self, 'Are you sure to quit?\nYou will lose all unsaved data.', 'Please Confirm', wx.YES_NO|wx.NO_DEFAULT | wx.ICON_QUESTION)
    if dlg.ShowModal() == wx.ID_YES:
      self.Close(True)
  
  def showConsole(self, value):
    self.console.SetValue(value)
    self.console.Show()
    self.output.Hide()
    self.topSizer.Layout()
  
  def hideConsole(self):
    self.console.Hide()
    self.output.Show()
    self.topSizer.Layout()
    
  def killSim(self):
    self.sim = None

    self.mainTextPane.MarkerDeleteAll(1)
    
    for key in self.memory.iterkeys():
      self.setMemory(key, 0, False)
    self.removeHighlights()
    
    self.timer.Stop()
    self.running = False
    self.pause = False
    self.status.SetStatusText("")
    
    self.addressPanel.Hide()
    self.addressStart = 0
    self.bottomSizer.Layout()
  
  def activeCallback(self, item, default):
    run = self.running
    if self.running:
      self.running = False
      self.timer.Stop()
      self.onHalt(None)
      
    while True:
      dlg = wx.TextEntryDialog(self, 'Please enter a value for '+item, 'Enter Value',"0x{0:02X}".format(default))

      if dlg.ShowModal() != wx.ID_OK:
        if run:
          self.running = True
          self.timer.Start(1)
        return default
      try:
        v = int(dlg.GetValue(),0)
        self.setMemory(item, v)
        if run:
          self.running = True
          self.timer.Start(1)
        return v
      except ValueError:
        dlg = wx.MessageDialog(self, dlg.GetValue()+' is of unknown type.  Please use prefix 0x for hex, 0b for binary, 0 for octal, or enter in decimal', 'Uknown Number Format', wx.OK | wx.ICON_QUESTION)
        dlg.ShowModal()
      
  def setMemory(self, key, value, highlight=True):
    if key=='IR':
      self.memory[key].SetValue("{0:05X}".format(value))
    elif key in ['PC']:
      self.memory[key].SetValue("{0:03X}".format(value))
    elif key in ['StkPtr']:
      self.memory[key].SetValue("{0:02X}".format(value))
    elif key in ['Z','SZ','C','SC','I']:
      self.memory[key].SetValue("{0:01d}".format(value))
    elif key.startswith("S"):
      self.memory[key].SetValue("{0:03X}".format(value))
    else:
      self.memory[key].SetValue("{0:02X}".format(value))
      
    if highlight:
      self.memoryChanged.append(key)
      self.memory[key].SetBackgroundColour((255,255,100,255))
      self.memory[key].Refresh()
          
  def removeHighlights(self):
    for mem in self.memoryChanged:
      self.memory[mem].SetBackgroundColour(self.backColor)
      self.memory[mem].Refresh()
    self.memoryChanged = []
  
  def updateFields(self, prgm_counter, newLine, newHex, changed):
    self.mainTextPane.MarkerDeleteAll(1)
    self.removeHighlights()
    self.setMemory("IR", newHex, False)
    self.setMemory("PC", prgm_counter, False)
    
    for mem, value in changed.iteritems():
        self.setMemory(mem, value)  
    
    if prgm_counter == -1:
      self.status.SetStatusText("Program Execution Completed")
      self.sim = None
      return

    self.currentLine = newLine-1
    if self.currentLine >= 0:
      self.mainTextPane.MarkerAdd(self.currentLine, 1)
    
    low = self.currentLine - 10
    if low < 0: low = 0
    high = self.currentLine + 10
    if high > self.mainTextPane.GetLineCount()-1: high = self.mainTextPane.GetLineCount()-1  
    self.mainTextPane.EnsureVisible(self.currentLine)
    self.mainTextPane.GotoLine(low)
    self.mainTextPane.GotoLine(high)
    self.mainTextPane.GotoLine(self.currentLine)
    
    