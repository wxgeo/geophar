# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

import param
from pylib import *
import  wx.grid as  gridlib 
#--------------------------------------------------------------------------- 

class EditorsAndRenderersGrid(gridlib.Grid): 
    def __init__(self, parent): 
        gridlib.Grid.__init__(self, parent,) 
        self.SetDefaultCellAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE) 
        self.CreateGrid(8, 2)
        self.EnableDragRowSize(False)
        self.SetColLabelValue(0, "X")
        self.SetColLabelValue(1, "Y")
        self.SetCellValue(0, 0, "Valeurs")
        self.SetCellValue(0, 1, "Valeur libre") 
        self.liste = ["Valeur libre"] + ["Y%s"%(i+1) for i in range(param.nombre_courbes)]
        self.choix = gridlib.GridCellChoiceEditor(self.liste, False)
        self.SetCellEditor(0, 1, self.choix)
        self.SetReadOnly(0, 0, True)
        #self.SetCellAlignment(0, 1, wx.CENTER, wx.CENTER)
        self.SetRowLabelSize(30)
        self.SetColSize(0, 75) 
        self.SetColSize(1, 75) 
        self.AutoSizeRows(True) 
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_DCLICK, self.OnLeftDClick)
        self.Bind(gridlib.EVT_GRID_CELL_CHANGE, self.OnChange)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.SetGridCursor(1, 0)
        #self.SetScrollbars(0, 0, 0, 0)
        
        
    def OnKeyDown(self, evt):
        if evt.KeyCode() <> wx.WXK_DELETE: 
            evt.Skip()
        else:
            print self.GetSelectedCells()
            for couple in self.GetSelectedCells():
                self.SetCellValue(couple[0], couple[1], "")
            print self.GetSelectionBlockTopLeft()
            print self.GetSelectionBlockBottomRight()
            for (couple0, couple1) in zip(self.GetSelectionBlockTopLeft(), self.GetSelectionBlockBottomRight()):
                i0, j0 = couple0
                i1, j1 = couple1
                couples = ((i,j) for i in range(i0, i1 + 1) for j in range(j0, j1 + 1))
                for couple in couples:
                    self.SetCellValue(couple[0], couple[1], "")
            self.SetCellValue(self.GetGridCursorRow(), self.GetGridCursorCol(), "")
        #self.SetScrollbars(0, 0, 0, 0)

                    
    # I do this because I don't like the default behaviour of not starting the 
    # cell editor on double clicks, but only a second click. 
    def OnLeftDClick(self, event = None): 
        if self.CanEnableCellControl(): 
            self.EnableCellEditControl()
        #self.SetScrollbars(0, 0, 0, 0)
    
    def OnChange(self, event = None):
        #print help(event.__class__)
        l = event.GetRow()
        c = event.GetCol()
        print event.__class__.__name__
        if c == 0 and l <> 0:
            try:
                choix_fonction = self.choix.GetValue()
                if choix_fonction <> self.liste[0]:
                    i = int(choix_fonction[1:])
                    intervalles = self.intervalles[i].GetValue().split("|")
                    equations = self.equations[i].GetValue().split("|")
                    self.SetCellValue(l, 1, str(float(self.GetCellValue(l, 0))**2))
            except:
                event.Veto()
            if l == self.GetNumberRows() - 1:
                self.AppendRows()
                self.MoveCursorDown(False)
        #self.SetScrollbars(0, 0, 0, 0)
                
        
#--------------------------------------------------------------------------- 
class TableauValeurs(wx.MiniFrame): 
    def __init__(self, parent): 
        wx.MiniFrame.__init__(self, parent, "Tableau de valeurs", style=wx.DEFAULT_FRAME_STYLE | wx.TINY_CAPTION_HORIZ, size=(250,300)) 
        self.parent = parent
        p = self.panel = QWidget(self)

        sizer = wx.BoxSizer(wx.VERTICAL)
        barre = wx.BoxSizer(wx.HORIZONTAL)
        creer = wx.Button(p, -1, "Creer les points")
        effacer = wx.Button(p, -1, "Effacer")
        barre.Add(creer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        barre.Add(effacer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        
        self.grid = grid = EditorsAndRenderersGrid(p)
        self.Bind(wx.EVT_BUTTON, self.efface, effacer)
        sizer.Add(barre, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        sizer.Add(grid, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND , 5)

        #p.SetSizer(sizer)
        p.SetSizerAndFit(sizer)
        x, y = p.GetSize().GetWidth(), p.GetSize().GetHeight()
        self.SetClientSize(wx.Size(x + 15, y + 15))
        grid.AdjustScrollbars()
        
    def efface(self, event = None):
        self.grid.ClearGrid()
        
#--------------------------------------------------------------------------- 
if __name__ == '__main__': 
    import sys 
    app = wx.PySimpleApp() 
    frame = TableauValeurs(None) 
    frame.show() 
    app.MainLoop() 
#--------------------------------------------------------------------------- 
