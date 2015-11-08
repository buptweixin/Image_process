#encoding=utf-8
__author__ = 'weixin'

import wx
import os



class gui(wx.Frame):
    def __init__(self, parent):
        self.title = "Ulsula"
        super(gui, self).__init__(parent, -1, self.title, size=(800, 600))
        self.panel = wx.Panel(self, size = self.Size)
        self.panel.SetBackgroundColour("WHITE")
        self.createMenuBar()

    def menuData(self):#2 菜单数据
        return [("&File", (
            ("&New", "New BMP file", self.OnNew),
            ("&Open", "Open BMP file", self.OnOpen),
            ("&Save", "Save BMP file", self.OnSave),
            ("", "", ""),
            ("&Quit", "Quit", self.OnCloseWindow)
        ))]

    wildcard = "Sketch files (*.sketch)|*.bmp"

    def OnNew(self, evt): pass
    def OnOpen(self, evt):
        dlg = wx.FileDialog(self, "Open BMP file", os.getcwd(), wildcard = self.wildcard, style=wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetPath()
            self.SetTitle(self.title + '--' + self.filename)
        dlg.Destroy()
    def OnSave(self, evt): pass
    def OnCloseWindow(self, evt): pass


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

    def createMenubar(self):
        menuBar = wx.MenuBar()
        for eachMenuData in self.menuData():
            menulabel = eachMenuData[0]
            menuItems = eachMenuData[1]
            menuBar.Append(self.createMenu(menuItems), menulabel)
        self.SetMenuBar(menuBar)





if __name__ == '__main__':
    app = wx.App()
    myframe = gui(None)
    myframe.Show()
    app.MainLoop()