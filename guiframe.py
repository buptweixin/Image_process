#encoding=utf-8
__author__ = 'weixin'

import wx
import wx.lib.imagebrowser as imagebrowser
import os

import matplotlib
matplotlib.use('WXAgg')
from impy import imglib
from matplotlib.figure import Figure
import numpy as np
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

class guiFrame(wx.Frame):
    def __init__(self, parent):
        self.title = "Pixel"
        super(guiFrame, self).__init__(parent, -1, self.title, size=(1200, 700))
        self.panel = wx.Panel(self, size = (self.Size[0]*2/3, self.Size[1]-20))
        self.panel.SetBackgroundColour("WHITE")
        self.noteBook = self.createNotebook()
        self.createHistPanel()
        self.createToolBar()
        self.initStatusBar()
        self.createMenuBar()
        self.direction = u'水平'
        self.method = u"双线性"
        self.filtermethod = u"理想"
        self.filename = './testImages/lena/lena200.bmp'
        self.sb1 = wx.StaticBitmap(self.panel, -1)
        self.figure = Figure(figsize=(5,3))
        self.axes = self.figure.add_subplot(111)
        self.filePath = os.getcwd()
        self.openBMP()
        self.hsider = wx.BoxSizer(wx.HORIZONTAL)
        self.staticBitmaps = self.createStaticBitmaps()
        for staticBitmap in self.staticBitmaps:
            self.hsider.Add(staticBitmap, proportion=1, flag= wx.ALL, border=20)

        self.panel.SetSizer(self.hsider)

    def createStaticBitmaps(self):
        return [wx.StaticBitmap(self.panel, -1, pos=(i*self.panel.Size[1]/3 + 100, 20)) for i in range(3)]

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
            [[u'最近邻', u'双线性'],self.OnSelecteZoomMethod],
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
        notebook = wx.Notebook(self, pos=(self.panel.Size[0], 0),\
                               size = (self.Size[0]-self.panel.Size[0], self.panel.Size[1]/2))
        panels = self.createPanels(notebook, notebook.Size)
        labels = self.getPanellabel()
        for item, panel in enumerate(panels):
            notebook.AddPage(panel, labels[item])
        return notebook

    def createHistPanel(self):
        self.histpanel = histPanel(self, style = wx.BORDER|wx.SOLID,
                                   pos = (self.panel.Size[0], self.panel.Size[1]/2+50),
                                   size = (self.noteBook.Size[0], self.panel.Size[1]/2))
        histEqualizationBtn = wx.Button(self.histpanel, label=u"均衡化")
        histEqualizationBtn.Bind(wx.EVT_BUTTON, self.OnHistEqu)
        self.histpanel.hsizer.Add(histEqualizationBtn,1, wx.RIGHT, border=1)
        self.histpanel.vsizer.Add(self.histpanel.hsizer)
        self.histpanel.SetSizerAndFit(self.histpanel.vsizer)


    def getData(self):
        return [
            [
                [['label', u'空域滤波']],
                [['choices', [u"低通", u"中值"], self.OnSmoothMethod],['button', u'滤波',self.OnSmooth]],
                [['choices', [u"高通", u"高增益", u"Roberts算子", u"Prewitt算子", u"Sobel算子", u"Laplacian算子"],
                  self.OnSharpenMethod],['button', u'锐化', self.OnSharpen]],
                [['label', u'变换与反变换']],
                [['button', u'傅里叶', self.OnFourier], ['button', u'离散余弦', self.OnCos]],
                [['button', u'傅里叶反变换', self.OnFourierInv], ['button', u'离散余弦反变换', self.OnCosInv]],
                [['label', u'频域滤波']],
                [['choices', [u"理想滤波器", u"巴特沃斯滤波器", u"高斯滤波器", u"指数滤波器"], self.OnFilterChoice],
                ['slider',[25, 0, 50]]],
                [['button', u'低通滤波', self.OnLowPass], ['button', u'高通滤波', self.OnHighPass]]


            ],
            [
                [['label', u'图像检索'],['button' ,u'选择文件夹', self.OnSearchSimilarImg], ['label', u'similarImg']]
            ]
                ]



    def getPanellabel(self):
        return [u'图像操作', u'图像检索', u'xxx']


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
                        if component[1] == u'similarImg':
                            font = wx.Font(14, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
                            self.similarImg = wx.StaticText(panel, label=" ", style=wx.TE_PROCESS_ENTER)
                            self.similarImg.SetFont(font)
                            self.similarImg.SetForegroundColour("RED")
                            gbsizer.Add(self.similarImg, pos = (3,1), span=(1,1),flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
                        else:
                            gbsizer.Add(wx.StaticText(panel, label=component[1]), pos = (itemcol+1, itemrow+1), span=(1,1), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
                    elif component[0] == u'choices':
                        choice = self.buildOneChoices(panel, component[1:], gbsizer, position = (itemcol+1, itemrow+1))
                        self.choices.append(choice)
                    elif component[0] == u'button':
                        self.buildOneButton(panel, component[1:], gbsizer, position = (itemcol+1, itemrow+1))
                    elif component[0] == u'slider':
                        self.slider = wx.Slider(panel, id = wx.NewId(), value = component[1][0], minValue=component[1][1],
                                                maxValue = component[1][2], style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS)
                        #self.slider.Bind(wx.EVT_SLIDER, self.OnSlider)
                        gbsizer.Add(self.slider, pos = (itemcol+1, itemrow+1), span=(1,1), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
            panel.SetSizerAndFit(gbsizer)
            panels.append(panel)
        self.smoothMethodChoices = self.choices[0]
        self.sharpenMethodChoices = self.choices[1]
        self.filtermethodChoices = self.choices[2]
        self.fourierBtn = panels[0].GetChildren()[6]
        self.costranBtn = panels[0].GetChildren()[7]
        self.fourierInvBtn = panels[0].GetChildren()[9]
        self.costranInvBtn = panels[0].GetChildren()[10]
        #self.fourierInvBtn.Enable(False)
        #self.costranInvBtn.Enable(False)
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
        self.fourierBtn.Enable(True)
        self.fourierInvBtn.Enable(True)
        self.costranBtn.Enable(True)
        self.costranInvBtn.Enable(True)
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

    def OnFilterChoice(self, evt):
        self.filtermethod = self.filtermethodChoices.GetStringSelection()

    def OnSharpen(self, evt):
        if self.sharpenMethodChoices.GetStringSelection() == u"高通":
            self.bitmap.Sharpen_HPF()
        elif self.sharpenMethodChoices.GetStringSelection() == u"高增益":
            self.bitmap.Sharpen_GFF()
        elif self.sharpenMethodChoices.GetStringSelection() == u"Roberts算子":
            self.bitmap.Sharpen_Roberts()
        elif self.sharpenMethodChoices.GetStringSelection() == u"Prewitt算子":
            self.bitmap.Sharpen_Prewitt()
        elif self.sharpenMethodChoices.GetStringSelection() == u"Sobel算子":
            self.bitmap.Sharpen_Sobel()
        elif self.sharpenMethodChoices.GetStringSelection() == u"Laplacian算子":
            self.bitmap.Sharpen_Laplacian()
        self.refreshBitmap()

    def OnSmooth(self, evt):
        if self.smoothMethodChoices.GetStringSelection() == u"低通滤波":
            self.bitmap.Smooth_LPF()
        else:
            self.bitmap.Smooth_midvaule()
        self.refreshBitmap()

    def OnFourier(self, evt):
        self.bitmap.image_fft()
        self.refreshBitmap()
        self.fourierBtn.Enable(False)
        self.fourierInvBtn.Enable(True)

    def OnFourierInv(self, evt):
        self.bitmap.image_ifft()
        self.refreshBitmap()
        self.fourierBtn.Enable(True)
        self.fourierInvBtn.Enable(False)

    def OnCos(self, evt):
        self.bitmap.image_dct()
        self.refreshBitmap()
        self.costranBtn.Enable(False)
        self.costranInvBtn.Enable(True)



    def OnCosInv(self, evt):
        self.bitmap.image_idct()
        self.refreshBitmap()
        self.costranBtn.Enable(True)
        self.costranInvBtn.Enable(False)

    def OnLowPass(self, evt):
        #self.OnFourier(evt)
        args = self.slider.GetValue()
        if self.filtermethod == u"理想":
            self.bitmap.Ideal_LPF(args)
        elif self.filtermethod == u"巴特沃斯":
            self.bitmap.butterworth_LPF(d=args)
        elif self.filtermethod == u"高斯":
            self.bitmap.Gauss_LPF(d=args)
        else:
            self.bitmap.exponential_LPF(d=args)
        self.refreshBitmap()

    def OnHighPass(self, evt):
        #self.OnFourier(evt)
        args = self.slider.GetValue()
        if self.filtermethod == u"理想":
            self.bitmap.Ideal_HPF(d= args)
        elif self.filtermethod == u"巴特沃斯":
            self.bitmap.butterworth_HPF(d= args)
        elif self.filtermethod == u"高斯":
            self.bitmap.Gauss_HPF(d= args)
        else:
            self.bitmap.exponential_HPF(d= args)
        self.refreshBitmap()

    def showHistFig(self):
        data = self.bitmap.hist()
        self.histpanel.refresh(data)

    def OnHistEqu(self, evt):
        data = self.bitmap.hist()
        equData = self.histpanel.refresh(data)
        self.bitmap.hist_equalization(equData)
        self.refreshBitmap()




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
        data = self.bitmap.hist()
        self.histpanel.refresh(data)
        fileDlg = wx.FileDialog(self, "Open BMP file", self.filePath, wildcard = self.wildcard, style=wx.OPEN)
        if fileDlg.ShowModal() == wx.ID_OK:
            self.filename = fileDlg.GetPath()
            self.filePath = os.path.split(self.filename)[0]
            self.openBMP()
        fileDlg.Destroy()

    def OnSearchSimilarImg(self, evt):
        pathDlg = wx.DirDialog(self, "Select a dir", os.getcwd())
        if pathDlg.ShowModal() == wx.ID_OK:
            self.path = pathDlg.GetPath()
        pathDlg.Destroy()
        filenames = os.listdir(self.path)
        filenames = filter(lambda filename: filename[-4:]==".bmp", filenames)
        hists = [np.array(self.axes.hist(imglib.readImg(self.path + '/' + filename).hist(), 256, range=(0, 255))) for filename in filenames]
        bitmaphist = np.array(self.axes.hist(self.bitmap.hist(), 256, range=(0, 255)))

        diff = [np.sum((bitmaphist[0]-hist[0])**2, axis=0) for hist in hists]
        sortedImg = np.argsort(diff, axis=0)
        label = u"共发现{filenum}个.bmp格式文件， 按直方图相似度排序为：".format(filenum=len(filenames))
        for item, value in enumerate(sortedImg):
            label += u"\n"+str(item+1)+u"."+filenames[value]

            if item < 3:
                image = wx.Image(self.path+'/'+filenames[value], wx.BITMAP_TYPE_BMP)
                bmp = wx.BitmapFromImage(image)
                self.staticBitmaps[item].SetBitmap(bmp)
            if item > 9:
                break
        self.similarImg.SetLabel(label)


    def openBMP(self):
        self.sb1.Destroy()
        # 打开图像，并复制一份，所有图像处理操作在这个复制图像上进行R
        self.image = wx.Image(self.filename, wx.BITMAP_TYPE_BMP)
        self.bitmap = imglib.readImg(self.filename)
        self.tmpImg = './tmp.bmp'
        self.bitmap.save_to(self.tmpImg)
        self.sb1 = wx.StaticBitmap(self.panel, pos = ((self.panel.Size[0] - self.image.Width)/2,
                                                      (self.panel.Size[1]-self.image.Height)/2),
                                   id = -1, bitmap = wx.BitmapFromImage(self.image))
        self.sb1.Bind(wx.EVT_MOTION, self.getImageGray)
        self.sb1.Bind(wx.EVT_LEFT_DOWN, self.setDownPoint)
        self.sb1.Bind(wx.EVT_LEFT_UP, self.setUpPoint)
        data = self.bitmap.hist()
        self.histpanel.refresh(data)
        self.SetTitle(self.title + '--' + self.filename)

    # created at 11.12
    def refreshBitmap(self):
        self.bitmap.save_to(self.tmpImg)
        self.image = wx.Image(self.tmpImg, wx.BITMAP_TYPE_BMP)
        self.sb1.SetBitmap(wx.BitmapFromImage(self.image))
        self.sb1.Refresh()
        data = self.bitmap.hist()
        self.histpanel.refresh(data)


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


class histPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        super(histPanel, self).__init__(*args, **kwargs)
        self.hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.vsizer = wx.BoxSizer(wx.VERTICAL)
        self.createFigureCanvas()

    def createFigureCanvas(self):
        self.figure = Figure(figsize=(5,3))
        self.axes = self.figure.add_subplot(111)
        # self.axes = self.figure.add_subplot(111)
        #self.axes.hist([1,1,1,12,2,2,2,3], 120)
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.vsizer.Add(self.canvas)


    def refresh(self, data):
        self.canvas.Close()
        self.axes.cla()
        hist_data = self.axes.hist(data, 256, range=(0, 255))
        self.canvas.draw()
        #self.canvas.Refresh()
        return hist_data





class App(wx.App):
    def OnPreInit(self):
        bmp = wx.Image("./icons/splash.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        wx.SplashScreen(bmp, wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT,1500, None, -1)
        wx.Yield()
        myframe = guiFrame(None)
        myframe.Show()
        return True


if __name__ == '__main__':
    app = App()
    app.MainLoop()
