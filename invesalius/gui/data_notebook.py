#--------------------------------------------------------------------------
# Software:     InVesalius - Software de Reconstrucao 3D de Imagens Medicas
# Copyright:    (C) 2001  Centro de Pesquisas Renato Archer
# Homepage:     http://www.softwarepublico.gov.br
# Contact:      invesalius@cti.gov.br
# License:      GNU - GPL 2 (LICENSE.txt/LICENCA.txt)
#--------------------------------------------------------------------------
#    Este programa e software livre; voce pode redistribui-lo e/ou
#    modifica-lo sob os termos da Licenca Publica Geral GNU, conforme
#    publicada pela Free Software Foundation; de acordo com a versao 2
#    da Licenca.
#
#    Este programa eh distribuido na expectativa de ser util, mas SEM
#    QUALQUER GARANTIA; sem mesmo a garantia implicita de
#    COMERCIALIZACAO ou de ADEQUACAO A QUALQUER PROPOSITO EM
#    PARTICULAR. Consulte a Licenca Publica Geral GNU para obter mais
#    detalhes.
#--------------------------------------------------------------------------
import Image

import wx
import wx.grid
import wx.lib.flatnotebook as fnb
import wx.lib.pubsub as ps

import gui.widgets.listctrl as listmix

# Panel that initializes notebook and related tabs
class NotebookPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, pos=wx.Point(0, 50), size=wx.Size(256, 140))
                        
        book = wx.Notebook(self, -1,style= wx.BK_DEFAULT)
        # TODO: check under Windows and Linux
        # this was necessary under MacOS:
        #if wx.Platform == "__WXMAC__":
        book.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)

        book.AddPage(MasksListCtrlPanel(book), "Masks")
        book.AddPage(SurfacesListCtrlPanel(book), "Surfaces")
        book.AddPage(MeasuresListCtrlPanel(book), "Measures")
        book.AddPage(AnnotationsListCtrlPanel(book), "Annotations")
        
        book.SetSelection(0)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(book, 1, wx.EXPAND)
        self.SetSizer(sizer)
        
        book.Refresh()
        
        # TODO: insert icons bellow notebook

class MasksListCtrlPanel(wx.ListCtrl, listmix.TextEditMixin):

    def __init__(self, parent, ID=-1, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.LC_REPORT):
        
        # native look and feel for MacOS
        #if wx.Platform == "__WXMAC__":
        #    wx.SystemOptions.SetOptionInt("mac.listctrl.always_use_generic", 0)
        
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style=wx.LC_REPORT)
        listmix.TextEditMixin.__init__(self)
        self.mask_list_index = {}
        self.mask_bmp_idx_to_name = {}
        self.__init_columns()
        self.__init_image_list()
        self.__bind_events_wx()
        self.__bind_events()
        
    def __bind_events_wx(self):
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.OnEditLabel)

    def __bind_events(self):
        ps.Publisher().subscribe(self.AddMask, 'Add mask')
        ps.Publisher().subscribe(self.EditMaskThreshold,
                                 'Set mask threshold in notebook')
        ps.Publisher().subscribe(self.EditMaskColour,
                                 'Change mask colour in notebook')

    def __init_columns(self):
        
        self.InsertColumn(0, "", wx.LIST_FORMAT_CENTER)
        self.InsertColumn(1, "Name")
        self.InsertColumn(2, "Threshold", wx.LIST_FORMAT_RIGHT)
        
        self.SetColumnWidth(0, 20)
        self.SetColumnWidth(1, 120)
        self.SetColumnWidth(2, 90)
        
    def __init_image_list(self):
        self.imagelist = wx.ImageList(16, 16)

        image = wx.Image("../icons/object_visible.jpg")
        bitmap = wx.BitmapFromImage(image.Scale(16, 16))
        bitmap.SetWidth(16)
        bitmap.SetHeight(16)
        img_check = self.imagelist.Add(bitmap)
        
        image = wx.Image("../icons/object_invisible.jpg")
        bitmap = wx.BitmapFromImage(image.Scale(16, 16))
        bitmap.SetWidth(16)
        bitmap.SetHeight(16)
        img_null = self.imagelist.Add(bitmap)
        
        self.SetImageList(self.imagelist, wx.IMAGE_LIST_SMALL)

        self.image_gray = Image.open("../icons/object_colour.jpg")
        
    def OnEditLabel(self, evt):
        print "Editing label", evt.GetLabel()
        #print evt.GetImage()
        #print evt.GetId()
        #print evt.GetIndex()
        print "--------"
        print evt.m_oldItemIndex
        print evt.m_itemIndex
        index = evt.GetIndex()
        #print dir(evt)
        
        print "Get item data:", self.GetItemData(index)
        print "Get item position:", self.GetItemPosition(index)
        print "Get next item:", self.GetNextItem(index)
        evt.Skip()
        
    def OnItemActivated(self, evt):
        print "OnItemActivated"
        self.ToggleItem(evt.m_itemIndex)
        
    def OnCheckItem(self, index, flag):
        # TODO: use pubsub to communicate to models
        if flag:
            print "checked, ", index
        else:
            print "unchecked, ", index

    def CreateColourBitmap(self, colour):
        """
        Create a wx Image with a mask colour.
        colour: colour in rgb format(0 - 1)
        """
        print "Colour", colour
        image = self.image_gray
        new_image = Image.new("RGB", image.size)
        for x in xrange(image.size[0]):
            for y in xrange(image.size[1]):
                pixel_colour = [int(i*image.getpixel((x,y)))
                                for i in colour]
                new_image.putpixel((x,y), tuple(pixel_colour))

        wx_image = wx.EmptyImage(new_image.size[0],
                                 new_image.size[1])
        wx_image.SetData(new_image.tostring())
        return wx.BitmapFromImage(wx_image.Scale(16, 16))

    def InsertNewItem(self, index=0, label="Mask 1", threshold="(1000, 4500)",
                      colour=None):
        print "InsertNewItem"
        self.InsertStringItem(index, "")
        self.SetStringItem(index, 1, label, 
                           imageId=self.mask_list_index[index]) 
        self.SetStringItem(index, 2, threshold)
        
        print "Get item data:", self.GetItemData(index)
        print "Get item position:", self.GetItemPosition(index)
        print "Get next item:", self.GetNextItem(index)
        # FindItem
        # FindItemData
        # FindItemAtPos
        
    def AddMask(self, pubsub_evt):
        index, mask_name, threshold_range, colour = pubsub_evt.data
        image = self.CreateColourBitmap(colour)
        image_index = self.imagelist.Add(image)
        print "image_index: ", image_index
        self.mask_list_index[index] = image_index
        self.InsertNewItem(index, mask_name, str(threshold_range))
        
    def EditMaskThreshold(self, pubsub_evt):
        index, threshold_range = pubsub_evt.data
        self.SetStringItem(index, 2, str(threshold_range))

    def EditMaskColour(self, pubsub_evt):
        index, colour = pubsub_evt.data
        image = self.CreateColourBitmap(colour)
        image_index = self.mask_list_index[index]
        self.imagelist.Replace(image_index, image)
        self.Refresh()
        
    def Populate(self):
        dict = ((0,"Mask 1", "(1000,4500)"),
                (1,"Mask 2", "(2000, 4500)"),
                (2,"Background","(0,4500)"))
        for data in dict:
            self.InsertNewItem(data[0], data[1], data[2])
        
class SurfacesListCtrlPanel(wx.ListCtrl, listmix.TextEditMixin):

    def __init__(self, parent, ID=-1, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.LC_REPORT):
        
        # native look and feel for MacOS
        #if wx.Platform == "__WXMAC__":
        #    wx.SystemOptions.SetOptionInt("mac.listctrl.always_use_generic", 0)
        
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style=wx.LC_REPORT)
        listmix.TextEditMixin.__init__(self)

        self.__init_columns()
        self.__init_image_list()
        self.__init_evt()
        
        self.surface_list_index = {}
        self.surface_bmp_idx_to_name = {}

    def __init_evt(self):
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        ps.Publisher().subscribe(self.AddSurface,
                                'Update surface info in GUI')

    def __init_columns(self):
        
        self.InsertColumn(0, "", wx.LIST_FORMAT_CENTER)
        self.InsertColumn(1, "Name")
        self.InsertColumn(2, "Transparency", wx.LIST_FORMAT_RIGHT)
        
        self.SetColumnWidth(0, 20)
        self.SetColumnWidth(1, 120)
        self.SetColumnWidth(2, 90)
        
    def __init_image_list(self):
        self.imagelist = wx.ImageList(16, 16)

        image = wx.Image("../icons//object_visible.jpg")
        bitmap = wx.BitmapFromImage(image.Scale(16, 16))
        bitmap.SetWidth(16)
        bitmap.SetHeight(16)
        img_check = self.imagelist.Add(bitmap)
        
        image = wx.Image("../icons/object_invisible.jpg")
        bitmap = wx.BitmapFromImage(image.Scale(16, 16))
        bitmap.SetWidth(16)
        bitmap.SetHeight(16)
        img_null = self.imagelist.Add(bitmap)
        
        self.SetImageList(self.imagelist, wx.IMAGE_LIST_SMALL)

        self.image_gray = Image.open("../icons/object_colour.jpg")

    def AddSurface(self, pubsub_evt):
        index = pubsub_evt.data[0]
        name = pubsub_evt.data[1]
        colour = pubsub_evt.data[2]
        transparency = "%d%%"%(int(100*pubsub_evt.data[3]))

        image = self.CreateColourBitmap(colour)
        image_index = self.imagelist.Add(image)
        self.surface_list_index[index] = image_index
        
        self.InsertNewItem(index, name, str(transparency), colour)

    def InsertNewItem(self, index=0, label="Surface 1",
                      transparency="(1000, 4500)", colour=None):
        self.InsertStringItem(index, "")
        self.SetStringItem(index, 1, label,
                            imageId = self.surface_list_index[index]) 
        self.SetStringItem(index, 2, transparency)
        


    def CreateColourBitmap(self, colour):
        """
        Create a wx Image with a mask colour.
        colour: colour in rgb format(0 - 1)
        """
        image = self.image_gray
        new_image = Image.new("RGB", image.size)
        for x in xrange(image.size[0]):
            for y in xrange(image.size[1]):
                pixel_colour = [int(i*image.getpixel((x,y)))
                                for i in colour]
                new_image.putpixel((x,y), tuple(pixel_colour))

        wx_image = wx.EmptyImage(new_image.size[0],
                                 new_image.size[1])
        wx_image.SetData(new_image.tostring())
        return wx.BitmapFromImage(wx_image.Scale(16, 16))            
        
    def OnItemActivated(self, evt):
        self.ToggleItem(evt.m_itemIndex)
        
    def OnCheckItem(self, index, flag):
        # TODO: use pubsub to communicate to models
        if flag:
            print "checked, ", index
        else:
            print "unchecked, ", index


    
class MeasuresListCtrlPanel(wx.ListCtrl, listmix.TextEditMixin):
    # TODO: Change edimixin to affect third column also
    def __init__(self, parent, ID=-1, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.LC_REPORT):
        
        # native look and feel for MacOS
        #if wx.Platform == "__WXMAC__":
        #    wx.SystemOptions.SetOptionInt("mac.listctrl.always_use_generic", 0)
        
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style=wx.LC_REPORT)
        listmix.TextEditMixin.__init__(self)

        self.__init_columns()
        self.__init_image_list()
        self.__init_evt()
        
        # just testing
        self.Populate()
        
    def __init_evt(self):
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)

    def __init_columns(self):
        
        self.InsertColumn(0, "", wx.LIST_FORMAT_CENTER)
        self.InsertColumn(1, "Value")
        self.InsertColumn(2, "Type", wx.LIST_FORMAT_RIGHT)
        
        self.SetColumnWidth(0, 20)
        self.SetColumnWidth(1, 120)
        self.SetColumnWidth(2, 50)
        
    def __init_image_list(self):
        self.imagelist = wx.ImageList(16, 16)

        image = wx.Image("../icons/object_visible.jpg")
        bitmap = wx.BitmapFromImage(image.Scale(16, 16))
        bitmap.SetWidth(16)
        bitmap.SetHeight(16)
        img_check = self.imagelist.Add(bitmap)
        
        image = wx.Image("../icons/object_invisible.jpg")
        bitmap = wx.BitmapFromImage(image.Scale(16, 16))
        bitmap.SetWidth(16)
        bitmap.SetHeight(16)
        img_null = self.imagelist.Add(bitmap)

        image = wx.Image("../icons/object_colour.jpg")
        bitmap = wx.BitmapFromImage(image.Scale(16, 16))
        bitmap.SetWidth(16)
        bitmap.SetHeight(16)
        self.img_colour = self.imagelist.Add(bitmap)
        
        self.SetImageList(self.imagelist, wx.IMAGE_LIST_SMALL)
        
    def OnItemActivated(self, evt):
        self.ToggleItem(evt.m_itemIndex)
        
    def OnCheckItem(self, index, flag):
        # TODO: use pubsub to communicate to models
        if flag:
            print "checked, ", index
        else:
            print "unchecked, ", index

    def InsertNewItem(self, index=0, type_="Mask 1", value="(1000, 4500)",
                      colour=None):
        self.InsertStringItem(index, "")
        self.SetStringItem(index, 1, type_, imageId = self.img_colour) 
        self.SetStringItem(index, 2, value)
        
    def Populate(self):
        dict = ((0, "30000 mm", "/ 3D"),
                (1, "20o", "o 2D"),
                (2, "500 mm", "/ 2D"))
        for data in dict:
            self.InsertNewItem(data[0], data[1], data[2])

    
class AnnotationsListCtrlPanel(wx.ListCtrl, listmix.TextEditMixin):
    # TODO: Remove edimixin, allow only visible and invisible
    def __init__(self, parent, ID=-1, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.LC_REPORT):
        
        # native look and feel for MacOS
        #if wx.Platform == "__WXMAC__":
        #    wx.SystemOptions.SetOptionInt("mac.listctrl.always_use_generic", 0)
        
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style=wx.LC_REPORT)
        listmix.TextEditMixin.__init__(self)

        self.__init_columns()
        self.__init_image_list()
        self.__init_evt()
        
        # just testing
        self.Populate()
        
    def __init_evt(self):
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)

    def __init_columns(self):
        
        self.InsertColumn(0, "", wx.LIST_FORMAT_CENTER)
        self.InsertColumn(1, "Name")
        self.InsertColumn(2, "Type", wx.LIST_FORMAT_CENTER)
        self.InsertColumn(3, "Value")
        
        self.SetColumnWidth(0, 20)
        self.SetColumnWidth(1, 90)
        self.SetColumnWidth(2, 50)
        self.SetColumnWidth(3, 120)
        
    def __init_image_list(self):
        self.imagelist = wx.ImageList(16, 16)

        image = wx.Image("../icons/object_visible.jpg")
        #image = wx.Image("../img/object_visible-v2.jpg")
        bitmap = wx.BitmapFromImage(image.Scale(16, 16))
        bitmap.SetWidth(16)
        bitmap.SetHeight(16)
        img_check = self.imagelist.Add(bitmap)
        
        image = wx.Image("../icons/object_invisible.jpg")
        bitmap = wx.BitmapFromImage(image.Scale(16, 16))
        bitmap.SetWidth(16)
        bitmap.SetHeight(16)
        img_null = self.imagelist.Add(bitmap)

        image = wx.Image("../icons/object_colour.jpg")
        bitmap = wx.BitmapFromImage(image.Scale(16, 16))
        bitmap.SetWidth(16)
        bitmap.SetHeight(16)
        self.img_colour = self.imagelist.Add(bitmap)
        
        self.SetImageList(self.imagelist, wx.IMAGE_LIST_SMALL)
        
    def OnItemActivated(self, evt):
        self.ToggleItem(evt.m_itemIndex)
        
    def OnCheckItem(self, index, flag):
        # TODO: use pubsub to communicate to models
        if flag:
            print "checked, ", index
        else:
            print "unchecked, ", index

    def InsertNewItem(self, index=0, name="Axial 1", type_="2d",
                      value="bla", colour=None):
        self.InsertStringItem(index, "")
        self.SetStringItem(index, 1, name, imageId = self.img_colour) 
        self.SetStringItem(index, 2, type_)
        self.SetStringItem(index, 3, value)
        
    def Populate(self):
        dict = ((0, "Axial 1", "2D", "blalbalblabllablalbla"),
                (1, "Coronal 1", "2D", "hello here we are again"),
                (2, "Volume 1", "3D", "hey ho, lets go"))
        for data in dict:
            self.InsertNewItem(data[0], data[1], data[2], data[3])
