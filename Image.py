import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os
import cv2 as cv
import random
import numpy as np
from ctypes import *

Start_RectX,Start_RectY,End_RectX,End_RectY,UpCurrentBoxIndex,CurrentBoxIndex,ChangeBoxStatu = 0,0,0,0,0,0,0
PaintStatu,SelectedBox,PressChangeSize,MoveBox,RemindObjectNmae = float,float,float,float,float

CurrentImagePath,CurrentImageName,CurrentImageAllName = "","",""   #CurrentImageName 图片名字不包含后缀
BoxList,ImageSize,SelectedBox_Rect,NewBox_Rect,List_MatchBox,List_ColorBox,LabelObjectName = [],[],[],[],[],[],[]

ObjectNmae = ["角色","怪物","领主"]
dll = {}

Fself = 0

def Load_ListWidget_MatchImage(self):
    self.List_MatchImage.clear()
    MatchImageFiles = os.listdir(sys.path[0] + "\Match")
    MatchImageFiles.sort(key=lambda x: int(x[:-4]))
    for MatchImageFile in MatchImageFiles:
        if ".bmp" in MatchImageFile:
            self.List_MatchImage.addItem(
                QListWidgetItem(QIcon(sys.path[0] + "/Match/" + MatchImageFile), MatchImageFile))

class MyLabel(QLabel):
    def __init__(self, parent=None):
        super(MyLabel, self).__init__(parent)
        self.if_mouse_press = False
    def mouseMoveEvent(self, event): #鼠标移动事件
        global End_RectX,End_RectY,PaintStatu,SelectedBox,SelectedBox_Rect,ChangeBoxStatu,PressChangeSize
        End_RectX = event.pos().x()
        End_RectY = event.pos().y()
        # 1=左上|2=左下|3=右上|4=右下|5=左|6=右|7=顶|8=底
        if SelectedBox == True and PressChangeSize == float and MoveBox == float:  #这里操作鼠标的形状
            if SelectedBox_Rect[0] > End_RectX - 5 and SelectedBox_Rect[0] < End_RectX + 5 and SelectedBox_Rect[1] > End_RectY - 5 and SelectedBox_Rect[1] < End_RectY + 5: #左上角
                ChangeBoxStatu = 1
                self.setCursor(Qt.SizeFDiagCursor)
            elif SelectedBox_Rect[0] > End_RectX - 5 and SelectedBox_Rect[0] < End_RectX + 5 and SelectedBox_Rect[1] + SelectedBox_Rect[3] > End_RectY - 5 and SelectedBox_Rect[1] + SelectedBox_Rect[3] < End_RectY + 5: #左下角
                ChangeBoxStatu = 2
                self.setCursor(Qt.SizeBDiagCursor)
            elif SelectedBox_Rect[0] + SelectedBox_Rect[2]  > End_RectX - 5 and SelectedBox_Rect[0] + SelectedBox_Rect[2] < End_RectX + 5 and SelectedBox_Rect[1] > End_RectY - 5 and SelectedBox_Rect[1] < End_RectY + 5: #右上角
                ChangeBoxStatu = 3
                self.setCursor(Qt.SizeBDiagCursor)
            elif SelectedBox_Rect[0] + SelectedBox_Rect[2] > End_RectX - 5 and SelectedBox_Rect[0]  + SelectedBox_Rect[2] < End_RectX + 5 and SelectedBox_Rect[1] +SelectedBox_Rect[3] > End_RectY - 5 and SelectedBox_Rect[1] + SelectedBox_Rect[3] < End_RectY + 5:  # 右下角
                ChangeBoxStatu = 4
                self.setCursor(Qt.SizeFDiagCursor)
            elif SelectedBox_Rect[0] > End_RectX - 3 and SelectedBox_Rect[0] < End_RectX + 3 and SelectedBox_Rect[1] < End_RectY and SelectedBox_Rect[1] + SelectedBox_Rect[3] > End_RectY: #左边，左右
                ChangeBoxStatu = 5
                self.setCursor(Qt.SizeHorCursor)
            elif SelectedBox_Rect[0] + SelectedBox_Rect[2]  > End_RectX - 3 and SelectedBox_Rect[0] + SelectedBox_Rect[2] < End_RectX + 3 and SelectedBox_Rect[1] < End_RectY and SelectedBox_Rect[1] + SelectedBox_Rect[3] > End_RectY: #右边，左右:
                ChangeBoxStatu = 6
                self.setCursor(Qt.SizeHorCursor)
            elif SelectedBox_Rect[1] > End_RectY - 3 and SelectedBox_Rect[1] < End_RectY + 3 and SelectedBox_Rect[0] < End_RectX and SelectedBox_Rect[0] + SelectedBox_Rect[2] > End_RectX:      #顶，上下
                ChangeBoxStatu = 7
                self.setCursor(Qt.SizeVerCursor)
            elif SelectedBox_Rect[1] + SelectedBox_Rect[3]  > End_RectY - 3 and SelectedBox_Rect[1] + SelectedBox_Rect[3] < End_RectY + 3 and SelectedBox_Rect[0] < End_RectX and SelectedBox_Rect[0] + SelectedBox_Rect[2] > End_RectX: #底，上下
                ChangeBoxStatu = 8
                self.setCursor(Qt.SizeVerCursor)
            else:
                if PressChangeSize == True:
                    self.update()
                    return
                ChangeBoxStatu = 0
                self.setCursor(Qt.ArrowCursor)
        self.update()
    def mousePressEvent(self, e):  #鼠标按住
        global Start_RectX,Start_RectY,PaintStatu,ImageSize,CurrentBoxIndex,SelectedBox,UpCurrentBoxIndex,BoxList,SelectedBox_Rect,PressChangeSize,NewBox_Rect,MoveBox,Fself,CurrentImageName,RemindObjectNmae,CurrentImageAllName,CurrentImagePath
        if RemindObjectNmae == float:
            QMessageBox.information(self,"提示","请注意当前标注对象类别为：" + Fself.ComboBox_ObjectName.currentText(), QMessageBox.Ok)
            RemindObjectNmae = True
            return
        Start_RectX = e.pos().x()
        Start_RectY = e.pos().y()
        if Start_RectX > ImageSize[1] - 15 and Start_RectX < ImageSize[1] and Start_RectY < 15 and Start_RectY > 0: #点击区域为删除该图片,同时更新ImageNameList
            os.remove(CurrentImagePath + "/" + CurrentImageAllName)
            if os.path.exists(CurrentImagePath + "/" + CurrentImageAllName[:-3] + "txt"):
                os.remove(CurrentImagePath + "/" + CurrentImageAllName[:-3] + "txt")
            if Fself.List_ImageNmae.count() == 1:
                Fself.Label_ShowImage.close()
                Fself.List_ImageNmae.clear()
                return
            Currentindex = Fself.List_ImageNmae.currentRow()
            Fself.List_ImageNmae.clear()
            filenames = os.listdir(CurrentImagePath)
            filenames.sort(key=lambda x: int(x[:-4]))
            for filename in filenames:
                if ".jpg" in filename or ".bmp" in filename:
                    Fself.List_ImageNmae.addItem(filename)

            if Fself.List_ImageNmae.count() == 0: return
            if Currentindex == Fself.List_ImageNmae.count():
                Fself.List_ImageNmae.setCurrentRow(Currentindex - 1)
            else:
                Fself.List_ImageNmae.setCurrentRow(Currentindex)
            return
        if ChangeBoxStatu != 0: #按住了调整框,不往下处理
            PressChangeSize = True
            return
        PressChangeSize = float
        PaintStatu = True
        # 鼠标点击范围是否有box,下面是获取当前点击的box
        CurrentBoxIndex = 0
        SelectedBox = float
        for i in BoxList:
            CurrentBoxIndex = CurrentBoxIndex + 1
            x = float(i.split()[1]) * ImageSize[1]
            y = float(i.split()[2]) * ImageSize[0]
            width = float(i.split()[3]) * ImageSize[1]
            high = float(i.split()[4]) * ImageSize[0]
            left = x - width / 2
            top = y - high / 2
            if left < Start_RectX and (left + width) > Start_RectX:
                if top < Start_RectY and (top + high) > Start_RectY:
                    SelectedBox = True
                    MoveBox = True
                    self.setCursor(Qt.SizeAllCursor)
                    PaintStatu = float
                    SelectedBox_Rect = left, top, width, high
                    if UpCurrentBoxIndex == CurrentBoxIndex:  # 上次点击的box和本次点击的box一致,可以点击x删除当前box
                        # 点击区域为删除Box
                        if Start_RectX > (left + width - 15) and Start_RectX < left + width and Start_RectY < (top + 15) and Start_RectY > top:
                            SelectedBox = float
                            MoveBox = float
                            del BoxList[CurrentBoxIndex - 1]
                            file = open(CurrentImagePath + "/" + CurrentImageName + ".txt", 'w',newline="")
                            file.truncate()
                            file.close()
                            file2 = open(CurrentImagePath + "/" + CurrentImageName + ".txt", 'a+',newline="")
                            for ii in BoxList:
                                file2.write(ii.strip() + "\n")
                            file2.close()
                        #点击区域为添加模板
                        elif Start_RectX > left and Start_RectX < left + 15 and Start_RectY < top + 15 and Start_RectY > top:
                            #截图保存模板
                            img = cv.imread(str(CurrentImagePath + "/" + CurrentImageAllName))
                            for i in range(3000):
                                path = sys.path[0] + "\\Match\\" + str(i) + ".bmp"
                                if os.path.exists(path) != True:
                                    cv.imwrite(path,img[int(top):int(top + high), int(left):int(left + width)])
                                    TabDemo.Load_ListWidget_MatchImage(Fself)
                                    break
                    UpCurrentBoxIndex = CurrentBoxIndex
                    self.update()
                    return
    def mouseReleaseEvent(self, e):#鼠标释放
        global Start_RectX,Start_RectY,End_RectX,End_RectY,ImageSize,CurrentImagePath,PaintStatu,CurrentBoxIndex,PressChangeSize,BoxList,CurrentBoxIndex,NewBox_Rect,SelectedBox_Rect,MoveBox,CurrentImageName
        self.setCursor(Qt.ArrowCursor)
        if PressChangeSize == True:
            #修改Box大小
            print(NewBox_Rect)
            C_X = (NewBox_Rect[0] + NewBox_Rect[2] / 2) / ImageSize[1]
            C_Y = (NewBox_Rect[1] + NewBox_Rect[3] / 2) / ImageSize[0]
            w_h = NewBox_Rect[2] / ImageSize[1]
            h_h = NewBox_Rect[3] / ImageSize[0]
            if w_h < 0.01 or h_h < 0.01:
                print("无效的操作")
                PressChangeSize = float
                self.update()
                return
            del BoxList[CurrentBoxIndex - 1]
            file = open(CurrentImagePath + "/" + CurrentImageName + ".txt", 'w',newline="")
            file.truncate()
            file.close()
            file2 = open(CurrentImagePath + "/" + CurrentImageName + ".txt", 'a+',newline="")
            BoxList.insert(CurrentBoxIndex - 1,str(Fself.ComboBox_ObjectName.currentIndex()) + " " + str(C_X) + " " + str(C_Y) + " " + str(w_h) + " " + str(h_h) + " " + "\r")
            for ii in BoxList:
                file2.write(ii.strip() + "\n")
            file2.close()
            PressChangeSize = float
            SelectedBox_Rect = NewBox_Rect
            self.update()
            return
        if MoveBox == True:
            MoveBox = float
            C_X = (NewBox_Rect[0] + NewBox_Rect[2] / 2) / ImageSize[1] #ImageSize[0] = width；ImageSize[1] = high；NewBox_Rect = left，top，width，high
            C_Y = (NewBox_Rect[1] + NewBox_Rect[3] / 2) / ImageSize[0]
            w_h = NewBox_Rect[2] / ImageSize[1]
            h_h = NewBox_Rect[3] / ImageSize[0]
            if w_h < 0.01 or h_h < 0.01:
                print("无效的操作")
                PressChangeSize = float
                self.update()
                return
            del BoxList[CurrentBoxIndex - 1]
            file = open(CurrentImagePath + "/" + CurrentImageName + ".txt", 'w')
            file.truncate()
            file.close()
            file2 = open(CurrentImagePath + "/" + CurrentImageName + ".txt", 'a+',newline="")
            BoxList.insert(CurrentBoxIndex - 1,str(Fself.ComboBox_ObjectName.currentIndex()) + " " + str(C_X) + " " + str(C_Y) + " " + str(w_h) + " " + str(h_h) + " " + "\r")
            for ii in BoxList:
                file2.write(ii.strip() + "\n")
            file2.close()
            PressChangeSize = float
            SelectedBox_Rect = NewBox_Rect
            self.update()
            return
        if SelectedBox == True:
            PaintStatu = float
            MoveBox = float
            return  #刚才鼠标点击的是box，不需要其他操作
        End_RectX = e.pos().x()
        End_RectY = e.pos().y()
        if Start_RectX > End_RectX or Start_RectY > End_RectY:
            print("不支持反向操作")
            PaintStatu = float
            return
        Center_X = (Start_RectX + ((End_RectX - Start_RectX) / 2)) / ImageSize[1]
        Center_Y = (Start_RectY + ((End_RectY - Start_RectY) / 2)) / ImageSize[0]
        width = (End_RectX - Start_RectX) / ImageSize[1]
        high = (End_RectY - Start_RectY) / ImageSize[0]
        if width < 0.01 or high < 0.01:
            print("选择区域太小")
            PaintStatu = float
            return
        file = open(CurrentImagePath + "/" + CurrentImageName + ".txt", 'a+',newline="")
        file.write(str(Fself.ComboBox_ObjectName.currentIndex()) + " " + str(Center_X) + " " + str(Center_Y) + " " + str(width) + " " + str(high) + "\n")
        file.close()
        self.update()
        PaintStatu = float
    def paintEvent(self, event):
        global Start_RectX,Start_RectY,End_RectX,End_RectY,ImageSize,PaintStatu,SelectedBox,CurrentBoxIndex,BoxList,PressChangeSize,SelectedBox_Rect,NewBox_Rect,MoveBox,List_MatchBox
        QLabel.paintEvent(self, event)   #调用原始qlabel绘制函数，添加图片背景
        painter = QPainter(self)
        painter.setPen(QPen(Qt.red, 1))
        #下面绘制匹配box
        for i in range(len(List_MatchBox)):
            painter.setPen(QPen(Qt.green, 1))
            painter.drawRect(QRect(List_MatchBox[i][0] - 3, List_MatchBox[i][1] - 3, List_MatchBox[i][2] + 6, List_MatchBox[i][3] + 6))
        if len(ImageSize):
            painter.drawText(ImageSize[1] - 15, 15, "×")
        #下面绘制保存好的box
        BoxList = []
        i = 0
        if os.path.exists(CurrentImagePath + "/" + CurrentImageName + '.txt'):
            #painter.setPen(QPen(List_ColorBox[0], 1))
            for line in open(CurrentImagePath + "/" + CurrentImageName + '.txt'):
                BoxList.append(line)
                i = i + 1
                x = float(line.split()[1]) * ImageSize[1]
                y = float(line.split()[2]) * ImageSize[0]
                width = float(line.split()[3]) * ImageSize[1]
                high = float(line.split()[4]) * ImageSize[0]
                left = x - width / 2
                top = y - high / 2
                if SelectedBox == True: #将当前选中的box框加大处理
                    if i == CurrentBoxIndex and SelectedBox == True:
                        painter.drawText(left + width - 15, top + 15, "×")
                        painter.drawText(left + 5, top + 15, "＋")
                        painter.setPen(QPen(List_ColorBox[int(line.split()[0])], 3))
                    else:
                        painter.setPen(QPen(List_ColorBox[int(line.split()[0])], 1))
                if (PressChangeSize == True and i == CurrentBoxIndex) or (MoveBox == True and i == CurrentBoxIndex):  #这里尝试一下，当前模式为调整大小的时候，当前选择框不在这里绘制
                    continue
                painter.setPen(QPen(List_ColorBox[int(line.split()[0])], 1))
                painter.drawRect(QRect(left, top, width, high))

        Fself.Label_Box_Match_Info.setText("LabelBox:" + str(i) + " | MatchBox:" + str(len(List_MatchBox)))
        if PaintStatu == True:  #当前绘制
            painter.drawRect(QRect(Start_RectX,Start_RectY,End_RectX - Start_RectX,End_RectY - Start_RectY))
        # 1=左上|2=左下|3=右上|4=右下|5=左|6=右|7=顶|8=底
        elif PressChangeSize == True:
            painter.setPen(QPen(Qt.red, 3))
            if ChangeBoxStatu == 1:#左上
                NewBox_Rect = End_RectX, End_RectY, SelectedBox_Rect[2] + SelectedBox_Rect[0] - End_RectX,SelectedBox_Rect[3] + SelectedBox_Rect[1] - End_RectY
            elif ChangeBoxStatu == 2:#左下
                NewBox_Rect = End_RectX, SelectedBox_Rect[1], SelectedBox_Rect[0] - End_RectX + SelectedBox_Rect[2],End_RectY - SelectedBox_Rect[1]
            elif ChangeBoxStatu == 3:#右上
                NewBox_Rect = SelectedBox_Rect[0], End_RectY,End_RectX - SelectedBox_Rect[0], SelectedBox_Rect[3] + SelectedBox_Rect[1] - End_RectY
            elif ChangeBoxStatu == 4:
                NewBox_Rect = SelectedBox_Rect[0], SelectedBox_Rect[1], End_RectX - SelectedBox_Rect[0], End_RectY - SelectedBox_Rect[1]
            elif ChangeBoxStatu == 5: #left change
                NewBox_Rect = End_RectX,SelectedBox_Rect[1],SelectedBox_Rect[0] - End_RectX + SelectedBox_Rect[2],SelectedBox_Rect[3]
            elif ChangeBoxStatu == 6: #right change
                NewBox_Rect = SelectedBox_Rect[0], SelectedBox_Rect[1], End_RectX - SelectedBox_Rect[0],SelectedBox_Rect[3]
            elif ChangeBoxStatu == 7: #top change
                NewBox_Rect = SelectedBox_Rect[0], End_RectY, SelectedBox_Rect[2],SelectedBox_Rect[3] + SelectedBox_Rect[1] - End_RectY
            elif ChangeBoxStatu == 8:  # bottom change
                NewBox_Rect = SelectedBox_Rect[0], SelectedBox_Rect[1], SelectedBox_Rect[2], End_RectY - SelectedBox_Rect[1]
            painter.drawRect(QRect(NewBox_Rect[0], NewBox_Rect[1], NewBox_Rect[2], NewBox_Rect[3]))
        elif MoveBox == True:
            NewBox_Rect = SelectedBox_Rect[0] + End_RectX -Start_RectX,SelectedBox_Rect[1] + End_RectY - Start_RectY , SelectedBox_Rect[2], SelectedBox_Rect[3]
            painter.drawRect(QRect(NewBox_Rect[0], NewBox_Rect[1], NewBox_Rect[2], NewBox_Rect[3]))

# 重载ListImage显示匹配模板图片,用于响应删除按键
class MyListMatchWidget(QListWidget):
    global Fself
    def keyPressEvent(self,event):
        QListWidget.keyPressEvent(self,event)
        if event.key() == 16777223:   #按下了删除键
            if Fself.List_MatchImage.currentItem() != None:
                os.remove(sys.path[0] + "\\Match\\" + Fself.List_MatchImage.currentItem().text())
                Load_ListWidget_MatchImage(Fself)

class TabDemo(QTabWidget):
    def __init__(self, parent=None):
        super(TabDemo, self).__init__(parent)
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.addTab(self.tab1, "Tab 1")
        self.addTab(self.tab2, "Tab 2")
        self.addTab(self.tab3, "Tab 3")
        self.tab1UI()
        self.tab2UI()
        self.tab3UI()
        self.setGeometry(300, 300, 1300, 600)
        self.setWindowTitle("Buttons")
        self.pos_xy = []
        self.Load_ListWidget_MatchImage()
    def tab1UI(self):
        self.Button_ImportVideo = QPushButton("Import Video")
        self.Label_VideoPath = QLabel("Video Path")
        self.Label_Conversion_Ratio = QLabel("GetFrameRate:1")
        self.Slider_Conversion_Ratio = QSlider(Qt.Horizontal)
        self.Slider_Conversion_Ratio.setMinimum(1)
        self.Slider_Conversion_Ratio.setMaximum(100)
        self.Slider_Conversion_Ratio.setTickPosition(QSlider.TicksAbove)
        self.Button_StartCreateImage = QPushButton("Start Create")
        self.ProgressBar_pbar = QProgressBar(self)
        self.Button_ImportVideo.clicked.connect(self.ButtonImportVideo)
        self.Button_StartCreateImage.clicked.connect(self.Signal_StartCreateImage)
        self.Slider_Conversion_Ratio.valueChanged[int].connect(self.Slider_Conversion_RatioChangevalue)
        Layout = QGridLayout(self)
        v1_1 = QHBoxLayout()
        v2_1 = QHBoxLayout()
        v3_1 = QHBoxLayout()
        v1_1.addWidget(self.Button_ImportVideo)
        v1_1.addWidget(self.Label_VideoPath)
        v2_1.addWidget(self.Label_Conversion_Ratio)
        v2_1.addWidget(self.Slider_Conversion_Ratio)
        v3_1.addWidget(self.Button_StartCreateImage)
        v3_1.addWidget(self.ProgressBar_pbar)
        Layout.addLayout(v1_1, 0, 0)
        Layout.addLayout(v2_1, 1, 0)
        Layout.addLayout(v3_1, 2, 0)

        self.setTabText(0, "视频拆分成图片")
        self.tab1.setLayout(Layout)
    def tab2UI(self):
        global ImageSize,CurrentImagePath,SelectedBox,Fself,LabelObjectName
        Fself = self
        SelectedBox = float
        self.Button_NULL = QPushButton("*")  #无用，方便聚焦
        self.Button_NULL.setMaximumHeight(20)
        self.Button_NULL.setMaximumWidth(20)
        self.Button_OpenImgPath = QPushButton("打开图片文件夹")
        self.Button_OpenImgPath.clicked.connect(self.MesButton_OpenImgPath)
        self.Button_Validation = QPushButton("验证标记")         #用于验证，将标注好的图片显示在Tabel
        self.Button_Validation.clicked.connect(self.MesButton_Validation)
        self.Button_Delete = QPushButton("删除没有标记过的图片")
        self.Button_Delete.clicked.connect(self.Del_NoMartImgButton)
        self.Button_CreateConfigureFile = QPushButton("Create Configure File")
        self.Button_CreateConfigureFile.clicked.connect(self.CreateConfigureFile)
        # initialize Slider_Match
        self.Label_Match = QLabel('Match :0 %', self)
        self.Slider_Match = QSlider(Qt.Horizontal, self)
        self.Slider_Match.setMinimum(0)
        self.Slider_Match.setMaximum(20)
        self.Slider_Match.setTickPosition(QSlider.TicksAbove)
        self.Slider_Match.valueChanged[int].connect(self.Slider_changevalue)
        self.Slider_Match.setValue(20)
        self.Slider_Match.valueChanged[int].connect(self.Slider_MatchValurChang)
        #initialize Label ShowImage
        self.Label_ShowImage = MyLabel(self)
        self.Label_ShowImage.setMouseTracking(True)
        self.Label_ShowImage.setAlignment(Qt.AlignLeft)

        #List_ImageNmae控件初始化
        self.List_ImageNmae = QListWidget(self)
        self.List_ImageNmae.setMaximumSize(200,3100)
        self.List_ImageNmae.currentRowChanged.connect(self.List_ImageNmae_clickitem)

        self.Qtabel_ShowLabelImage = QTableWidget(self)
        self.List_MatchImage = MyListMatchWidget(self)
        self.List_MatchImage.setViewMode(QListView.IconMode)
        self.List_MatchImage.setIconSize(QSize(100,100))

        self.Load_ListWidget_MatchImage()
        self.Label_Box_Match_Info = QLabel()
        self.ComboBox_ObjectName = QComboBox(self)
        #ComboBox_initialize

        for line in ObjectNmae:
            self.ComboBox_ObjectName.addItem(line)

        # if os.path.exists(sys.path[0] + "/wzx.names"):
        #     for line in open(sys.path[0] + "/wzx.names"):
        #         LabelObjectName.append(line.strip())
        #         self.ComboBox_ObjectName.addItem(line.strip())


        for i in range(self.ComboBox_ObjectName.count()):#初始化标注对象框框的颜色，达到每个对象使用不同颜色
            List_ColorBox.append(QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        #布局
        Layout = QGridLayout(self)
        v1_1 = QHBoxLayout()
        v1_2 = QHBoxLayout()
        v1_3 = QHBoxLayout()
        v2_1 = QVBoxLayout()
        v2_2 = QVBoxLayout()
        v2_3 = QVBoxLayout()
        v1_1.addWidget(self.Button_NULL)
        v1_1.addWidget(self.Button_OpenImgPath)
        v1_1.addWidget(self.Button_Delete)
        v1_2.addWidget(self.Label_Match)
        v1_2.addWidget(self.Slider_Match)
        v1_2.addWidget(self.Label_Box_Match_Info)
        v1_3.addWidget(self.Button_Validation)
        v2_1.addWidget(self.List_ImageNmae)
        v2_1.addWidget(self.Button_CreateConfigureFile)
        v2_2.addWidget(self.ComboBox_ObjectName)
        v2_2.addWidget(self.Label_ShowImage)
        # v2_2.addWidget(self.Slider_Match)
        v2_2.addWidget(self.List_MatchImage)
        v2_3.addWidget(self.Qtabel_ShowLabelImage)
        Layout.addLayout(v1_1, 0, 0)
        Layout.addLayout(v1_2, 0, 1)
        Layout.addLayout(v1_3, 0, 2)
        Layout.addLayout(v2_1, 1, 0)
        Layout.addLayout(v2_2, 1, 1)
        Layout.addLayout(v2_3, 1, 2)

        self.setTabText(1, "标注图片")
        self.tab2.setLayout(Layout)
    def tab3UI(self):
        layout1 = QFormLayout()
        layout1.addRow("姓名", QLineEdit())
        layout1.addRow("地址", QLineEdit())
        self.setTabText(2, "测试")
        self.tab3.setLayout(layout1)
    def Slider_changevalue(self,value):
        self.Label_Match.setText("Match :" + str(value * 5) + "%")
    def Slider_Conversion_RatioChangevalue(self,value):
        self.Label_Conversion_Ratio.setText("GetFrameRate:" + str(value))
    def List_ImageNmae_clickitem(self, obj):   #List ImageName组件选中行被改变
        if self.List_ImageNmae.currentRow() == -1:
            return
        global ImageSize,CurrentImagePath,CurrentImageName,SelectedBox,ChangeBoxStatu,CurrentBoxIndex,UpCurrentBoxIndex,List_MatchBox,CurrentImageAllName,LabelObjectName
        SelectedBox = float
        ChangeBoxStatu,CurrentBoxIndex,UpCurrentBoxIndex = 0,-1,-1
        CurrentImageAllName = self.List_ImageNmae.currentItem().text()
        CurrentImageName = self.List_ImageNmae.currentItem().text()[:-4]
        AllName = self.List_ImageNmae.currentItem().text()
        self.Label_ShowImage.setPixmap(QPixmap(CurrentImagePath + "/" + CurrentImageName))
        self.Label_ShowImage.setCursor(Qt.ArrowCursor)  #恢复鼠标初始形状
        #以下是Tabel操作
        self.Qtabel_ShowLabelImage.clear()
        #标注对象坐标,先获取数据在排序
        BufObjectInfo,ObjectInfo = [],[]

        if os.path.exists(CurrentImagePath + "\\" + AllName[:-3] + "txt") == False:
            return #此图片未标注
        for line in open(CurrentImagePath + "\\" + AllName[:-3] + "txt"): #获取标注信息
            BufObjectInfo.append(line)

        for i in range(len(BufObjectInfo)):
            MaxValue = 0
            MaxValueIndex = 0
            for index,line in enumerate(BufObjectInfo):
                if int(line.split()[0]) > MaxValue:
                    MaxValue = int(line.split()[0])
                    MaxValueIndex = index
            ObjectInfo.append(BufObjectInfo[MaxValueIndex])
            del(BufObjectInfo[MaxValueIndex])
        #ObjectInfo = sorted(BufObjectInfo,key=(lambda x:x[0])) #排序

        self.Qtabel_ShowLabelImage.verticalHeader().setDefaultSectionSize(130)
        #获取类别索引
        ObjectIndexList = []
        for i in range(len(ObjectInfo)):
            ObjectIndexList.append(ObjectInfo[i].split()[0])   #   这个位置出现问题
        #根据对象总类，设定对应的行
        self.Qtabel_ShowLabelImage.setRowCount(len(set(ObjectIndexList)))
        #设置行名,先去掉重复，这里不使用set是因为set会打乱列表顺序
        TableRowName = []

        for i in ObjectIndexList:
            if ObjectNmae[int(i)] in TableRowName:
                continue
            TableRowName.append(ObjectNmae[int(i)])

        self.Qtabel_ShowLabelImage.setVerticalHeaderLabels(TableRowName)
        #根据对象数量,设定对应列
        MaxObjectCount = 0
        for i in (set(ObjectIndexList)):
            if ObjectIndexList.count(i) > MaxObjectCount:MaxObjectCount = ObjectIndexList.count(i)
        self.Qtabel_ShowLabelImage.setColumnCount(MaxObjectCount)
        #插入图片
        TabelItemShowImage = []
        for i in range(len(ObjectIndexList)):
            TabelItemShowImage.append(QLabel())
        TabelItemShowImageIndex = 0
        ColumIndnx = 0
        for i in range(len(set(ObjectIndexList))):
            NowColumnCount = ObjectIndexList.count(ObjectIndexList[ColumIndnx])
            ColumIndnx = ColumIndnx + NowColumnCount
            for ii in range(NowColumnCount):
                x = float(ObjectInfo[TabelItemShowImageIndex].split()[1]) * ImageSize[1]
                y = float(ObjectInfo[TabelItemShowImageIndex].split()[2]) * ImageSize[0]
                width = float(ObjectInfo[TabelItemShowImageIndex].split()[3]) * ImageSize[1]
                high = float(ObjectInfo[TabelItemShowImageIndex].split()[4]) * ImageSize[0]
                left = x - width / 2
                top = y - high / 2
                TabelItemShowImage[TabelItemShowImageIndex].setPixmap(QPixmap(CurrentImagePath + "/" + CurrentImageName).copy(left,top,width,high).scaled(100, 100))
                self.Qtabel_ShowLabelImage.setCellWidget(i, ii, TabelItemShowImage[TabelItemShowImageIndex])
                TabelItemShowImageIndex = TabelItemShowImageIndex + 1

        #下面模板匹配
        if self.List_MatchImage.count() == 0:
            return
        List_MatchBox = []
        img = cv.imread(str(CurrentImagePath + "/" + AllName))
        ImageSize = img.shape[0], img.shape[1]
        img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)  # 灰度原图
        MatchPath = os.listdir(sys.path[0] + "\Match")
        MatchPath.sort(key=lambda x: int(x[:-4]))
        i = 0
        for filename in MatchPath:
            if ".bmp" in filename:
                template = cv.imread(sys.path[0] + "\\Match\\" + filename, 0)  # 读模板,并转换灰度
                w, h = template.shape[::-1]
                res = cv.matchTemplate(img_gray, template, cv.TM_CCOEFF_NORMED)
                locs = np.where(res >= self.Slider_Match.value() * 5 / 100)
                for loc in zip(*locs[::-1]):
                    Add_Status = True
                    for ii in range(len(List_MatchBox)):  #这里查看一下列表里面是否已经有相似的元素
                        if List_MatchBox[ii][0] > loc[0] - 10  and List_MatchBox[ii][0] < loc[0] + 10 and List_MatchBox[ii][1] > loc[1] - 10 and List_MatchBox[ii][1] < loc[1] + 10:
                            Add_Status = float
                            break
                    if Add_Status == True:
                        List_MatchBox.append([])
                        List_MatchBox[i].append(loc[0])
                        List_MatchBox[i].append(loc[1])
                        List_MatchBox[i].append(w)
                        List_MatchBox[i].append(h)
                        i = i + 1
    def Load_ListWidget_MatchImage(self):
        a = 10
        # self.List_MatchImage.clear()
        # MatchImageFiles = os.listdir(sys.path[0] + "\Match")
        # MatchImageFiles.sort(key=lambda x: int(x[:-4]))
        # for MatchImageFile in MatchImageFiles:
        #     if ".bmp" in MatchImageFile:
        #         self.List_MatchImage.addItem(QListWidgetItem(QIcon(sys.path[0] + "/Match/" + MatchImageFile),MatchImageFile))
    def Slider_MatchValurChang(self):
        global ImageSize, CurrentImagePath, SelectedBox, ChangeBoxStatu, CurrentBoxIndex, UpCurrentBoxIndex,List_MatchBox
        List_MatchBox = []
        img = cv.imread(str(CurrentImagePath + "/" + CurrentImageName + ".jpg"))
        img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)  # 灰度原图
        MatchPath = os.listdir(sys.path[0] + "\Match")
        MatchPath.sort(key=lambda x: int(x[:-4]))
        i = 0
        for filename in MatchPath:
            if ".bmp" in filename:
                template = cv.imread(sys.path[0] + "\\Match\\" + filename, 0)  # 读模板,并转换灰度
                w, h = template.shape[::-1]
                res = cv.matchTemplate(img_gray, template, cv.TM_CCOEFF_NORMED)
                locs = np.where(res >= self.Slider_Match.value() * 5 / 100)
                for loc in zip(*locs[::-1]):
                    Add_Status = True
                    for ii in range(len(List_MatchBox)):  # 这里查看一下列表里面是否已经有相似的元素
                        if List_MatchBox[ii][0] > loc[0] - 10 and List_MatchBox[ii][0] < loc[0] + 10 and \
                                List_MatchBox[ii][1] > loc[1] - 10 and List_MatchBox[ii][1] < loc[1] + 10:
                            Add_Status = float
                            break
                    if Add_Status == True:
                        List_MatchBox.append([])
                        List_MatchBox[i].append(loc[0])
                        List_MatchBox[i].append(loc[1])
                        List_MatchBox[i].append(w)
                        List_MatchBox[i].append(h)
                        i = i + 1
    def keyPressEvent(self, event):
        if event.key() == 83:  # 按下S
            if self.List_ImageNmae.count() > self.List_ImageNmae.currentRow() + 1:
                self.List_ImageNmae.setCurrentRow(self.List_ImageNmae.currentRow() + 1)
        if event.key() == 87:  # 按下W
            if self.List_ImageNmae.currentRow() != 0:
                self.List_ImageNmae.setCurrentRow(self.List_ImageNmae.currentRow() - 1)
        if event.key() == 65:  # 按下A
            if self.Slider_Match.value() != 0:
                self.Slider_Match.setValue(self.Slider_Match.value() - 1)
        if event.key() == 68:  # 按下D
            if self.Slider_Match.value() != 20:
                self.Slider_Match.setValue(self.Slider_Match.value() + 1)
        if event.key() == 73:  # 按下I(插入匹配值到的坐标)
            global List_MatchBox
            file = open(CurrentImagePath + "/" + CurrentImageName + ".txt", 'a+',newline="")
            for i in range(len(List_MatchBox)):
                Center_X = (List_MatchBox[i][0] + (List_MatchBox[i][2] / 2)) / ImageSize[1]
                Center_Y = (List_MatchBox[i][1] + (List_MatchBox[i][3] / 2)) / ImageSize[0]
                width = List_MatchBox[i][2] / ImageSize[1]
                high = List_MatchBox[i][3] / ImageSize[0]
                file.write(str(self.ComboBox_ObjectName.currentIndex()) + " " + str(Center_X) + " " + str(Center_Y) + " " + str(width) + " " + str(high) + "\n")
            file.close()
            self.update()
    def Del_NoMartImgButton(self):
        print(CurrentImagePath)
        if len(CurrentImagePath) == 0:
            QMessageBox.information(self, "提示", "请选择处理文件夹",QMessageBox.Ok)
            return
        filenames =os.listdir(CurrentImagePath)
        filenames.sort(key=lambda x: int(x[:-4]))
        for filename in filenames:#删除无效文本
            if ".txt" in filename:
                if os.path.getsize(CurrentImagePath + "/" + filename) == 0:#该txt文件大小为0，没有标注内容，删除
                    os.remove(CurrentImagePath + "/" + filename)
        filenames = os.listdir(CurrentImagePath)
        filenames.sort(key=lambda x: int(x[:-4]))
        for filename in filenames: #删除没有文本的图片
            if ".bmp" in filename or ".jpg" in filename or ".png" in filename:
                if os.path.exists(CurrentImagePath + "/" + filename[:-3] + "txt") == False:
                    os.remove(CurrentImagePath + "/" + filename)
    def CreateConfigureFile(self):
        if len(CurrentImagePath) == 0:
            QMessageBox.information(self, "提示", "请选择处理文件夹",QMessageBox.Ok)
            return

        # 这里将选择的文件夹全部标注图片路径添加到txt，用于训练
        TrainPath = []
        filenames = os.listdir(CurrentImagePath)
        filenames.sort(key=lambda x: int(x[:-4]))
        for filename in filenames:
            if ".bmp" in filename or ".jpg" in filename or ".png" in filename:
                TrainPath.append(CurrentImagePath + "/" + filename)
        file = open(sys.path[0] + "\\" + "train.txt", 'w')
        file.truncate()  #清空txt
        file.close()
        file = open(sys.path[0] + "\\" + "train.txt", 'a+',newline="")
        for ii in TrainPath:
            file.write(ii.strip() + "\n") #添加数据到txt
        file.close()
        #这里将创建Object.names文件
        file = open(sys.path[0] + "\\" + "wzx.names", 'w')
        file.truncate()  #清空txt
        file.close()
        file = open(sys.path[0] + "\\" + "wzx.names", 'a+',newline="")
        for ii in range(len(ObjectNmae)) :
            file.write(str(ii) + "\n") #添加数据到txt
        file.close()
    def ButtonImportVideo(self):
        fname, ftype = QFileDialog.getOpenFileName(self, '打开文件', './')
        if len(fname) != 0:
            self.Label_VideoPath.setText(fname)
    def Signal_StartCreateImage(self):
        cap = cv.VideoCapture(self.Label_VideoPath.text())
        FrameRateTotal = int(cap.get(7))
        FrameRateCount = 0
        GetFramerate = int(self.Slider_Conversion_Ratio.value())
        self.ProgressBar_pbar.setMaximum(FrameRateTotal - 1)
        while (1):
            ret, frame = cap.read()
            if FrameRateCount % GetFramerate == 0:
                cv.imwrite(sys.path[0] + "\\OutImage\\" + str(FrameRateCount) + ".jpg", frame)
            if FrameRateCount == FrameRateTotal - 1:
                break
            FrameRateCount = FrameRateCount + 1
            self.ProgressBar_pbar.setValue(FrameRateCount)
        cap.release()
        cv.destroyAllWindows()
    def MesButton_OpenImgPath(self):

        global ImageSize,CurrentImagePath,CurrentImageName,CurrentImageAllName
        path = QFileDialog.getExistingDirectory(self, "choose directory", "C:\\Users\\Administrator\\Desktop")
        if len(path) != 0:
            CurrentImagePath = path
            filenames = os.listdir(path)
            # print(x[:-4])
            filenames.sort(key=lambda x: int(x[:-4]))
            self.List_ImageNmae.clear()
            for filename in filenames:
                if ".jpg" in filename or ".bmp" in filename or ".png" in filename:
                    self.List_ImageNmae.addItem(filename)
                    if len(ImageSize) == 0: #如果没有获取到图片大小，下面获取
                        CurrentImageAllName = filename
                        CurrentImageName = filename[:-4]
                        self.Label_ShowImage.setPixmap(QPixmap(path + "/" + filename))
                        image = cv.imread(path + "/" + filename)
                        ImageSize = image.shape[0], image.shape[1]
    def MesButton_Validation(self):
        global LabelObjectName,ImageSize,ObjectNmae
        self.Qtabel_ShowLabelImage.clear()
        #获取train.txt路径
        path = QFileDialog.getOpenFileName(self, "choose directory", "C:\\Users\\Administrator\\train.txt")
        if len(path) == 0:
            return
        self.Qtabel_ShowLabelImage.setRowCount(len(ObjectNmae))
        self.Qtabel_ShowLabelImage.verticalHeader().setDefaultSectionSize(130)
        # 记录每个对象的插入计数
        ObjectIndex = []
        for i in range(len(ObjectNmae)):
            ObjectIndex.append(0)
        #用于存储图片，插入到TabelItem中
        TabelItem_List = []
        if os.path.exists(path[0]):
            for i,line in enumerate(open(path[0])):#这里是训练图片路径，依次打开对应txt获取坐标信息,line返回图片路径
                image = cv.imread(line[:-1])
                ImageSize = image.shape[0], image.shape[1]
                if os.path.exists(line[:-4] + "txt"):  #打开txt文件获取标注信息
                    for line2 in open(line[:-4] + "txt"):#line2返回图片坐标信息
                        if self.Qtabel_ShowLabelImage.columnCount() == max(ObjectIndex):
                            self.Qtabel_ShowLabelImage.insertColumn(self.Qtabel_ShowLabelImage.columnCount())
                        x = float(line2.split()[1]) * ImageSize[1]
                        y = float(line2.split()[2]) * ImageSize[0]
                        width = float(line2.split()[3]) * ImageSize[1]
                        high = float(line2.split()[4]) * ImageSize[0]
                        left = x - width / 2
                        top = y - high / 2
                        TabelItem_List.append(QLabel())
                        TabelItem_List[len(TabelItem_List) - 1].setPixmap(QPixmap(line[:-1]).copy(left, top, width, high).scaled(130, 130))
                        self.Qtabel_ShowLabelImage.setCellWidget(int(line2.split()[0]), ObjectIndex[int(line2.split()[0])], TabelItem_List[len(TabelItem_List) - 1])
                        ObjectIndex[int(line2.split()[0])] = ObjectIndex[int(line2.split()[0])] + 1
        NewName = [] #设置新行名，行名增加对象数量
        for i in range(len(ObjectNmae)):
            NewName.append(ObjectNmae[i] + str(ObjectIndex[i]))
        self.Qtabel_ShowLabelImage.setVerticalHeaderLabels(NewName)

class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.statusBar().showMessage('这里是状态栏...')
        self.setGeometry(300, 300, 300, 220)
        self.setWindowTitle('状态栏')
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = TabDemo()
    demo.show()
    sys.exit(app.exec_())

