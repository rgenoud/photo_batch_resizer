#!/usr/bin/python
# -*- coding: utf-8 -*-

import wxversion
wxversion.select("2.8")
import wx
import os

border_width = 10

class Frame(wx.Frame):
    def __init__(self, title):
        global border_width

        wx.Frame.__init__(self, None, title=title, pos=(150,150), size=(600,400))
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.statusbar = self.CreateStatusBar()

        panel = wx.Panel(self)
        grid = wx.GridBagSizer(vgap = 5, hgap = 5)

        # static text
        in_dir_text = wx.StaticText(panel, -1, "Répertoire source :")
        out_dir_text = wx.StaticText(panel, -1, "Répertoire destination :")
        scale_text = wx.StaticText(panel, -1, "Pourcentage de réduction :")

        # edit boxes
        in_dir_ctrl = wx.TextCtrl(panel)
        out_dir_ctrl = wx.TextCtrl(panel)
        scale_ctrl = wx.TextCtrl(panel, value = "50")
        # disable the windows for now (only use the dialog boxes)
        in_dir_ctrl.Enable(False)
        out_dir_ctrl.Enable(False)

        # buttons
        in_dir_btn = wx.Button(panel, wx.ID_EDIT)
        out_dir_btn = wx.Button(panel, wx.ID_EDIT)
        exit_btn = wx.Button(panel, wx.ID_EXIT)
        start_btn = wx.Button(panel, wx.ID_OK)
        in_dir_btn.Bind(wx.EVT_BUTTON, self.OnInDirButton)
        out_dir_btn.Bind(wx.EVT_BUTTON, self.OnOutDirButton)
        exit_btn.Bind(wx.EVT_BUTTON, self.OnClose)
        start_btn.Bind(wx.EVT_BUTTON, self.OnStart)

        # add everything to the grid
        text_align = wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT
        ctrl_align = wx.ALL | wx.ALIGN_CENTER | wx.EXPAND
        btn_align = wx.ALL | wx.ALIGN_CENTER
        grid.AddGrowableCol(1, 0)
        grid.Add(in_dir_text, pos = (0, 0), flag = text_align, border = border_width)
        grid.Add(out_dir_text, pos = (1, 0), flag = text_align, border = border_width)
        grid.Add(scale_text, pos = (2, 0), flag = text_align, border = border_width)
        grid.Add(in_dir_ctrl, pos = (0, 1), flag = ctrl_align, border = border_width)
        grid.Add(out_dir_ctrl, pos = (1, 1), flag = ctrl_align, border = border_width)
        grid.Add(scale_ctrl, pos = (2, 1), flag = ctrl_align, border = border_width)
        grid.Add(in_dir_btn, pos = (0, 2), flag = btn_align, border = border_width)
        grid.Add(out_dir_btn, pos = (1, 2), flag = btn_align, border = border_width)
        grid.Add(exit_btn, pos = (3, 0), flag = btn_align, border = border_width)
        grid.Add(start_btn, pos = (3, 3), flag = btn_align, border = border_width)

        self.__in_dir_ctrl = in_dir_ctrl
        self.__out_dir_ctrl = out_dir_ctrl
        self.__scale_ctrl = scale_ctrl

        panel.SetSizer(grid)
        panel.Layout()

    def OnClose(self, event):
        self.Destroy()

    def OnAbout(self, event):
        dlg = wx.MessageDialog(self,
                               "Réducteur d'images en masse\nPar Richard Genoud",
                               "Information", wx.OK)
        result = dlg.ShowModal()
        dlg.Destroy()

    def OnInDirButton(self, event):
        dlg = wx.DirDialog(self,
                           "Choisir le répertoire contenant les images sources",
                           style = wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            self.__in_dir_ctrl.SetValue(dlg.GetPath())
        dlg.Destroy;

    def OnOutDirButton(self, event):
        dlg = wx.DirDialog(self, "Choisir le répertoire destination",
                           style = wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            self.__out_dir_ctrl.SetValue(dlg.GetPath())
        dlg.Destroy;

    def OnStart(self, event):
        pass

app = wx.App(redirect = False)
top = Frame("Hello World")
top.Show()
app.MainLoop()

