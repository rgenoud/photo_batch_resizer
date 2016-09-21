#!/usr/bin/python
# -*- coding: utf-8 -*-
import Image
import os
import multiprocessing
import threading
import logging
import logging.handlers
import pyexiv2
import wxversion
wxversion.select("3.0")
import wx

border_width = 10
scale_factor = 50

logger = logging.getLogger("threadTestLogger")
logger.setLevel(logging.DEBUG)
#logger.setLevel(logging.WARNING)
console = logging.StreamHandler()

formatter = logging.Formatter("%(created)f %(threadName)s %(message)s")

console.setFormatter(formatter)

logger.addHandler(console)

def do_scale(value) :
    global scale_factor
    return ((value * scale_factor) / 100)


def resize(in_file, out_file) :
    try :
        image = Image.open(in_file, mode = 'r')
    except :
        logger.error("unable to open file " + in_file)
        return

    if (image and image.format) :
        logger.info("treat file : " + in_file + " format=" + image.format)
        # calculate new size
        new_size = map(do_scale, image.size)
        # resize image
        try :
            image.thumbnail(new_size, Image.ANTIALIAS)
            image.save(out_file, image.format)
        except :
            logger.error("unable to save file " + out_file)
            return

            # get source image EXIF data
        try :
            source_image = pyexiv2.ImageMetadata(in_file)
            source_image.read()
        except :
            # no exif tag, no need to go further
            logger.error("no exif tag" + out_file)
            return

        try :
            # copy them to dest image
            dest_image = pyexiv2.metadata.ImageMetadata(out_file)
            dest_image.read()
            source_image.copy(dest_image)

            # set EXIF image size info to resized size
            dest_image["Exif.Photo.PixelXDimension"] = new_size[0]
            dest_image["Exif.Photo.PixelYDimension"] = new_size[1]
            dest_image.write()
        except :
            logger.error("unable to write exif metadata for file " + out_file);


class Thread_resize(threading.Thread) :
    def __init__(self, to_do, update) :
        threading.Thread.__init__(self)
        self.__to_do = to_do
        self.__update = update

    def run(self) :
        logger.debug("starting thread " + self.getName())
        try :
            while (True) :
                value = self.__to_do.pop()
                resize(value[0], value[1])
                self.__update(value[0] + "->" +  value[1] + " ok !")
        except :
            # end of list
            pass
        finally :
            logger.debug("stopping thread " + self.getName())

class Frame(wx.Frame):
    def __init__(self, title, refreshTime):
        global border_width
        global scale_factor

        wx.Frame.__init__(self, None, title=title, pos=(150,150), size=(600,300))
        self.timer = wx.Timer(self)

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_TIMER, self.OnTimer)

        self.__refreshTime = refreshTime
        self.__s = threading.Semaphore()
        self.statusbar = self.CreateStatusBar()
        self.__jobs = []

        panel = wx.Panel(self)
        grid = wx.GridBagSizer(vgap = 5, hgap = 5)

        # static text
        in_dir_text = wx.StaticText(panel, -1, u"Répertoire source :")
        out_dir_text = wx.StaticText(panel, -1, u"Répertoire destination :")
        scale_text = wx.StaticText(panel, -1, u"Pourcentage de réduction :")

        # edit boxes
        in_dir_ctrl = wx.TextCtrl(panel)
        out_dir_ctrl = wx.TextCtrl(panel)
        scale_ctrl = wx.TextCtrl(panel, value = str(scale_factor))
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
        grid.AddGrowableCol(0, 0)
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

    def OnTimer(self, event):
        self.__s.acquire()
        self.statusbar.SetStatusText(self.__statusText)
        self.__s.release()
        still_processing = 0

        # checking if all threads have finished
        for i in range(len(self.__jobs)) :
            if (self.__jobs[i].is_alive()) :
                still_processing = 1

        if (not still_processing) :
            self.statusbar.SetStatusText(u"Opération terminée !")
            self.timer.Stop()

    def OnInDirButton(self, event):
        dlg = wx.DirDialog(self,
                           u"Choisir le répertoire contenant les images sources",
                           style = wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            self.__in_dir_ctrl.SetValue(dlg.GetPath())
        dlg.Destroy;

    def OnOutDirButton(self, event):
        dlg = wx.DirDialog(self, u"Choisir le répertoire destination",
                           style = wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            self.__out_dir_ctrl.SetValue(dlg.GetPath())
        dlg.Destroy;

    def Update_Status(self, txt):
        self.__s.acquire()
        self.__statusText = txt
        self.__s.release()

    def OnStart(self, event):
        global scale_factor
        self.__jobs = []
        to_do = []
        in_dir = self.__in_dir_ctrl.GetValue()
        out_dir = self.__out_dir_ctrl.GetValue()
        cpu_count = multiprocessing.cpu_count()

        self.Update_Status("")

        try:
            scale_factor = int(self.__scale_ctrl.GetValue())
        except:
            scale_factor = 0
        if (scale_factor < 1):
            wx.MessageBox(u"Mauvaise valeur de réduction")
            return
        if not os.path.isdir(in_dir) or not os.path.isdir(out_dir):
            wx.MessageBox(u"Veuillez renseigner les répertoires source/destination")
            return

        logger.info("found %s processors", cpu_count)

        dirList = os.listdir(in_dir)

        # list of files to process
        for i in dirList :
            logger.debug("found file " + i)
            in_file = os.path.join(in_dir, i)
            if (os.path.isfile(in_file)) : 
                out_filename = os.path.splitext(i)[0] + '_small' + os.path.splitext(i)[1]
                out_file = os.path.join(out_dir, out_filename)
                to_do.append((in_file, out_file))
                logger.debug("in_file=" + in_file + " out_file=" + out_file)

        # create the threadpool
        for i in range(cpu_count) :
            self.__jobs.append(Thread_resize(to_do, self.Update_Status))

        # start the threads
        for i in range(len(self.__jobs)) :
            self.__jobs[i].start()

        # start the timer
        self.timer.Start(self.__refreshTime)

app = wx.App(redirect = False)
top = Frame(u"Réducteur d'images", 50)
top.Show()
app.MainLoop()



