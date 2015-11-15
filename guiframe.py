#encoding=utf-8
__author__ = 'weixin'

import wx
import wx.lib.imagebrowser as imagebrowser
import os

import matplotlib
matplotlib.use('WXAgg')
from impy import imglib
from matplotlib.figure import Figure

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

from numpy import sin, pi, arange, random
from matplotlib import pyplot as plt



class histPanel(wx.Panel):
    def __init__(self, parent, id, pos, size, data):
        super(histPanel, self).__init__(parent, id, pos, size)
        self.data = data
        self.createFigureCanvas()

    def createFigureCanvas(self):
        self.figure = Figure(figsize=(2,2))
        self.axes = self.figure.add_subplot(111)
        self.axes.hist(self.data, 256)
        self.canvas = FigureCanvas(self, -1, self.figure)

    def refresh(self, data):
        self.axes.hist(data, 256)
        self.canvas.Refresh()


class guiFrame(wx.Frame):
    def __init__(self, parent):
        self.title = "Ulsula"
        super(guiFrame, self).__init__(parent, -1, self.title, size=(1200, 720))
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.panel = wx.Panel(self, size = (self.Size[0]*2/3, self.Size[1]-20))
        self.panel.SetBackgroundColour("WHITE")
        self.sizer.Add(self.panel, 1, wx.LEFT | wx.TOP | wx.EXPAND, border = 1)
        self.noteBook = self.createNotebook()
        self.sizer.Add(self.noteBook,1,wx.RIGHT|wx.TOP|wx.EXPAND, border = 1)
        self.createToolBar()
        self.initStatusBar()
        self.createMenuBar()
        self.direction = u'水平'
        self.method = u"双线性"
        self.filename = './bear1107.bmp'
        self.openBMP()

    def createMenuItem(self, menu, label, status, handler, kind=wx.ITEM_NORMAL):
        if not label:
            menu.AppendSeparator()
            return
        menuItem = menu.Append(-1, label, status, kind) #4 创建菜单项
        self.Bind(wx.EVT_MENU, handler, menuItem)

    def createMenu(self, menuData):
        menu = wx.Menu()
        # 3 创建子菜单
        for eachItem in menuData:
            if len(eachItem) == 2:
                label = eachItem[0]
                subMenu = self.createMenu(eachItem[1])
                menu.AppendMenu(wx.NewId(), label, subMenu)

            else:
                self.createMenuItem(menu, *eachItem)
        return menu

    def createMenuBar(self):
        menuBar = wx.MenuBar()
        for eachMenuData in self.menuData():
            menuLabel = eachMenuData[0]
            menuItems = eachMenuData[1]
            menuBar.Append(self.createMenu(menuItems), menuLabel)
        self.SetMenuBar(menuBar)

    def getToolbarData(self):
        return [
            ["./icons/mirror_hor.png", u"水平翻转", self.OnMirrorHor],
            ["./icons/mirror_ver.png", u"垂直翻转", self.OnMirrorVer],
            ["./icons/move.png", u"移动图片", self.OnClickMoveBtn],
            ["./icons/cut.png", u"裁剪图片", self.OnClickCutBtn],
            [[u'双线性',u'最近邻'],self.OnSelecteZoomMethod],
            ["./icons/zoomin.png", u"放大", self.OnZoomIn],
            ["./icons/zoomout.png", u"缩小", self.OnZoomOut],
            ["./icons/rotate.png", u"旋转", self.OnRotate],
            ["./icons/OK.png", u"确定", self.OnOK]
        ]

    def createToolBar(self):
        self.toolbar = self.CreateToolBar()
        data = self.getToolbarData()
        for item in data:
            if len(item) == 3:
                icon = wx.Image(item[0], wx.BITMAP_TYPE_ANY).ConvertToBitmap()
                toolbtn = wx.BitmapButton(self.toolbar, wx.NewId(), bitmap = icon)
                toolbtn.Bind(wx.EVT_BUTTON, item[2])
                toolbtn.SetHelpText(item[1])
                self.toolbar.AddControl(toolbtn)
            else:
                choice = wx.Choice(self.toolbar, choices=item[0])
                choice.Bind(wx.EVT_CHOICE, item[1])
                self.toolbar.AddControl(choice)
        cancelBtn = wx.Button(self.toolbar, wx.NewId(), label = u"还原")
        cancelBtn.Bind(wx.EVT_BUTTON, self.OnCancel)
        self.toolbar.AddControl(cancelBtn)

        self.toolItems = self.toolbar.GetChildren()
        self.moveBtn = self.toolItems[2]
        self.cutBtn = self.toolItems[3]
        self.OKBtn = self.toolItems[8]
        self.OKBtn.Show(False)
        self.choice = self.toolItems[4]
        #self.smoothMethod = self.choice
        self.toolbar.Realize()

##########################
###
###     创建右侧控制菜单
###
#########################

    def createNotebook(self):
        notebook = wx.Notebook(self, pos=(self.panel.Size[0], 0), size = (self.Size[0]-self.panel.Size[0], self.panel.Size[1]))
        panels = self.createPanels(notebook, notebook.Size)
        labels = self.getPanellabel()
        for item, panel in enumerate(panels):
            notebook.AddPage(panel, labels[item])
        return notebook



    def getData(self):
        return [
            [
                [['label', u'空域滤波']],
                [['choices', [u"低通滤波", u"中值滤波"], self.OnSmoothMethod],['button', u'平滑',self.OnSmooth]],
                [['choices', [u"高通滤波", u"高增益滤波", u"Roberts算子", u"Prewitt算子", u"Sobel算子", u"Laplacian算子"],self.OnSharpenMethod],['button', u'锐化', self.OnSharpen]],
                [['label', u'频域变换'], ['button', u'傅里叶', self.OnFourier], ['button', u'离散余弦', self.OnCos]],
                [['label', u'反变换'],['button', u'傅里叶反变换', self.OnFourierInv], ['button', u'离散余弦反变换', self.OnCosInv]],
                [['label', u'频域滤波'], ['button', u'低通滤波', self.OnLowPass], ['button', u'高通滤波', self.OnHighPass]]
            ],
            [
                [['label', u'图像检索']]
            ]
                ]

    def getPanellabel(self):
        return [u'空域滤波', u'图像检索', u'xxx']


    def createPanels(self, parent, panels_size):
        data = self.getData()
        panels = []
        self.choices = []
        for paneldata in data:
            panel = wx.Panel(parent, size = panels_size)
            gbsizer = wx.GridBagSizer(vgap=8, hgap=6)
            for itemcol, value in enumerate(paneldata):
                 for itemrow, component in enumerate(value):
                    if component[0] == u'label':
                        gbsizer.Add(wx.StaticText(panel, label=component[1]), pos = (itemcol+1, itemrow+1), span=(1,1), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
                    elif component[0] == u'choices':
                        choice = self.buildOneChoices(panel, component[1:], gbsizer, position = (itemcol+1, itemrow+1))
                        self.choices.append(choice)
                    elif component[0] == u'button':
                        self.buildOneButton(panel, component[1:], gbsizer, position = (itemcol+1, itemrow+1))
            panel.SetSizerAndFit(gbsizer)
            panels.append(panel)
        self.smoothMethod = self.choices[0]
        self.sharpenMethod = self.choices[1]
        return panels

    def buildOneChoices(self, parent, data, sizer, position):
        choice = wx.Choice(parent, choices=data[0])
        choice.Bind(wx.EVT_CHOICE, data[1])
        sizer.Add(choice, pos = position, span=(1,1), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        return choice

    def buildOneButton(self, parent, data, sizer, position):
        button = wx.Button(parent, label = data[0])
        button.Bind(wx.EVT_BUTTON, data[1])
        sizer.Add(button, pos = position, span=(1,1), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)

    ### 响应事件
    def OnOK(self, evt):
        self.EnableToolbarBtns()

    def OnSelectedDirection(self, evt):
        self.direction = self.choices[0].GetStringSelection()

    def OnSelecteZoomMethod(self, evt):
        self.method = self.choice.GetStringSelection()

    def OnMirrorHor(self, evt):
        self.EnableToolbarBtns()
        self.bitmap.mirror(imglib.HORIZONTAL)
        self.refreshBitmap()

    def OnMirrorVer(self, evt):
        self.EnableToolbarBtns()
        self.bitmap.mirror(imglib.VERTICAL)
        self.refreshBitmap()

    def EnableToolbarBtns(self):
        self.OKBtn.Show(False)
        for button in self.toolItems:
            button.Enable(True)

    def OnClickMoveBtn(self, evt):
        if self.moveBtn.IsEnabled():
            self.moveBtn.Enable(False)# 移动按钮设置为不可点击并将其他按钮设为可点击
            self.OKBtn.Show(True)
            for button in self.toolItems:
                if button != self.moveBtn:
                    button.Enable(True)




    def OnClickCutBtn(self, evt):
        if self.cutBtn.IsEnabled():
            self.cutBtn.Enable(False)# 移动按钮设置为不可点击并将其他按钮设为可点击
            self.OKBtn.Show(True)
            for button in self.toolItems:
                if button != self.cutBtn:
                    button.Enable(True)

    def setDownPoint(self, evt):
        self.upPoint = evt.GetPositionTuple()

    def setUpPoint(self, evt):
        if all((self.moveBtn.IsEnabled(), self.cutBtn.IsEnabled())):
            pass
        else:
            self.downPoint = evt.GetPositionTuple()
            dx = self.downPoint[0]-self.upPoint[0]
            dy = self.downPoint[1]-self.upPoint[1]
            if not self.moveBtn.IsEnabled():
                self.bitmap.move(dx, dy)
            elif not self.cutBtn.IsEnabled():
                self.bitmap.cut(self.upPoint[::-1], self.downPoint[::-1] )
            self.refreshBitmap()
    def OnCancel(self, evt):
        self.EnableToolbarBtns()
        self.image = wx.Image(self.filename, wx.BITMAP_TYPE_BMP)
        self.bitmap = imglib.readImg(self.filename)
        self.sb1.SetBitmap(wx.BitmapFromImage(self.image))
        self.sb1.Refresh()


    def OnRotate(self, evt):
        self.bitmap.rotate()
        self.refreshBitmap()

    def OnZoomIn(self, evt):
        self.EnableToolbarBtns()
        if self.method == u"最近邻":
            self.bitmap.resize_nearest(1.1)
        else:
            self.bitmap.resize_bilinear(1.1)
        self.refreshBitmap()

    def OnZoomOut(self, evt):
        self.EnableToolbarBtns()
        if self.method == u"最近邻":
            self.bitmap.resize_nearest(0.9)
        else:
            self.bitmap.resize_bilinear(0.9)
        self.refreshBitmap()


    def OnSmoothMethod(self, evt):
        pass

    def OnSharpenMethod(self, evt):
        pass

    def OnSharpen(self, evt):
        if self.sharpenMethod.GetStringSelection() == u"高通滤波":
            self.bitmap.Sharpen_HPF()
        elif self.sharpenMethod.GetStringSelection() == u"高增益滤波":
            self.bitmap.Sharpen_GFF()
        elif self.sharpenMethod.GetStringSelection() == u"Roberts算子":
            self.bitmap.Sharpen_Roberts()
        elif self.sharpenMethod.GetStringSelection() == u"Prewitt算子":
            self.bitmap.Sharpen_Prewitt()
        elif self.sharpenMethod.GetStringSelection() == u"Sobel算子":
            self.bitmap.Sharpen_Sobel()
        elif self.sharpenMethod.GetStringSelection() == u"Laplacian算子":
            self.bitmap.Sharpen_Laplacian()
        self.refreshBitmap()

    def OnSmooth(self, evt):
        if self.smoothMethod.GetStringSelection() == u"低通滤波":
            self.bitmap.Smooth_LPF()
        else:
            self.bitmap.Smooth_midvaule()
        self.refreshBitmap()

    def OnFourier(self, evt):
        self.bitmap.image_fft()
        self.refreshBitmap()

    def OnCos(self, evt):
        self.bitmap.image_dct()
        self.refreshBitmap()

    def OnFourierInv(self, evt):
        pass

    def OnCosInv(self, evt):
        pass

    def OnLowPass(self, evt):
        pass

    def OnHighPass(self, evt):
        pass




    def getImageGray(self, evt):
        pos = evt.GetPositionTuple()
        self.statusbar.SetStatusText("X:%s, Y:%s" % (str(pos[0]), str(pos[1])))
        self.statusbar.SetStatusText("Gray:%s" % str(self.bitmap.getPix(pos)), 1)

    def initStatusBar(self):
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetFieldsCount(3)
        self.statusbar.SetStatusWidths([-1, -2, -3])

    def menuData(self):#2 菜单数据
        return [("&File", (
            ("&Open", "Open BMP file", self.OnOpen),
            ("&Save", "Save BMP file", self.OnSave),
            ("&Saveas", "Save as", self.OnSaveAs),
            ("", "", ""),
            ("&Quit", "Quit", self.OnCloseWindow)
        ))]

    wildcard = "BMP files (*.bmp)|*.bmp"


    def OnOpen(self, evt):
        dlg = wx.FileDialog(self, "Open BMP file", os.getcwd(), wildcard = self.wildcard, style=wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetPath()
            self.openBMP()
            self.SetTitle(self.title + '--' + self.filename)

        dlg.Destroy()

    def openBMP(self):
        # 打开图像，并复制一份，所有图像处理操作在这个复制图像上进行R
        self.image = wx.Image(self.filename, wx.BITMAP_TYPE_BMP)
        self.bitmap = imglib.readImg(self.filename)
        self.tmpImg = './tmp.bmp'
        self.bitmap.save_to(self.tmpImg)
        self.sb1 = wx.StaticBitmap(self.panel, pos = ((self.panel.Size[0] - self.image.Width)/2, (self.panel.Size[1]-self.image.Height)/2), id = -1, bitmap = wx.BitmapFromImage(self.image))
        self.sb1.Bind(wx.EVT_MOTION, self.getImageGray)
        self.sb1.Bind(wx.EVT_LEFT_DOWN, self.setDownPoint)
        self.sb1.Bind(wx.EVT_LEFT_UP, self.setUpPoint)

    # created at 11.12
    def refreshBitmap(self):
        self.bitmap.save_to(self.tmpImg)
        self.image = wx.Image(self.tmpImg, wx.BITMAP_TYPE_BMP)
        self.sb1.SetBitmap(wx.BitmapFromImage(self.image))
        self.sb1.Refresh()


    def OnSave(self, evt):
        self.bitmap.save_to(self.filename)
    def OnSaveAs(self, evt):
        dlg = wx.FileDialog(self, "Save BMP as...", os.getcwd(), style=wx.SAVE|wx.OVERWRITE_PROMPT, wildcard= self.wildcard)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            if not os.path.splitext(self.filename)[1]:
                filename += '.bmp'
            self.filename = filename
            self.bitmap.save_to(self.filename)
            self.SetTitle(self.title+'--'+self.filename)
        dlg.Destroy()



    def OnCloseWindow(self, evt):
        self.Destroy()
        wx.Exit()






class App(wx.App):
    def OnPreInit(self):
        provider = wx.CreateFileTipProvider("./impy/tips.txt", 0)
        wx.ShowTip(None, provider, True)
        myframe = guiFrame(None)
        myframe.Show()
        return True


if __name__ == '__main__':
    app = App()
    app.MainLoop()