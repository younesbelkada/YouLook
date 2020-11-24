# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialog.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
import glob
import os
from utils_predict import *
import openpifpaf
import PIL

use_cuda = torch.cuda.is_available()
device = torch.device("cuda" if use_cuda else "cpu")
print('Device: ', device)

def load_pifpaf():
    print('Loading Pifpaf')
    net_cpu, _ = openpifpaf.network.factory(checkpoint='shufflenetv2k16w', download_progress=False)
    net = net_cpu.to(device)
    openpifpaf.decoder.CifSeeds.threshold = 0.5
    openpifpaf.decoder.nms.Keypoints.keypoint_threshold = 0.0
    openpifpaf.decoder.nms.Keypoints.instance_threshold = 0.2
    openpifpaf.decoder.nms.Keypoints.keypoint_threshold_rel = 0.0
    openpifpaf.decoder.CifCaf.force_complete = True
    processor = openpifpaf.decoder.factory_decode(net.head_nets, basenet_stride=net.base_net.stride)
    preprocess = openpifpaf.transforms.Compose([openpifpaf.transforms.NormalizeAnnotations(),openpifpaf.transforms.CenterPadTight(16),openpifpaf.transforms.EVAL_TRANSFORM])
    return net, processor, preprocess



class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1200, 800)

        self.tab_im = []
        self.path = ""
        self.i = 0
        self.model_path = ""
        self.model = []

        self.model_loaded = False
        self.saved = False

        self.X = None
        self.Y = None
        self.img = None
        self.bboxes = None

        self.size = (0,0)




        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.pushButton_4 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_4.setObjectName("pushButton_4")
        self.verticalLayout.addWidget(self.pushButton_4)
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.verticalLayout.addWidget(self.pushButton_2)
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setObjectName("pushButton_3")
        self.verticalLayout.addWidget(self.pushButton_3)
        self.pushButton_5 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_5.setObjectName("pushButton_5")
        self.verticalLayout.addWidget(self.pushButton_5)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.photo = QtWidgets.QLabel(self.centralwidget)
        self.photo.setMaximumSize(QtCore.QSize(self.size[0], self.size[1]))
        self.photo.setText("")
        self.photo.setPixmap(QtGui.QPixmap(""))
        #self.photo.setScaledContents(True)
        self.photo.setObjectName("photo")
        self.horizontalLayout.addWidget(self.photo)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1125, 20))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionOpen = QtWidgets.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.menuFile.addAction(self.actionOpen)
        self.menubar.addAction(self.menuFile.menuAction())
        self.last_x, self.last_y = None, None
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.pushButton.clicked.connect(self.click)
        self.pushButton_3.clicked.connect(self.predict)
        self.pushButton_4.clicked.connect(self.click_back)
        self.pushButton_5.clicked.connect(self.selectFile)
        self.pushButton_2.clicked.connect(self.save)
        self.actionOpen.triggered.connect(self.click_directory)

        self.photo.mousePressEvent = self.mouseMoveEvent
        self.net, self.processor, self.preprocess = load_pifpaf()

    def alert(self):
        if self.model_loaded == False:
            alert = QtWidgets.QMessageBox()
            alert.setText('Please Load a model before')
            alert.exec_()
        
    def save(self):
        self.saved = True
        directory_anno = self.path+'/anno_'+self.path.split('/')[-1]
        if not os.path.exists(directory_anno):
            os.makedirs(directory_anno)
        if self.X != None:    
            data = {'X':self.X, 'Y':self.Y, 'bbox':self.bboxes}
            print(data)
            with open(directory_anno+'/'+self.get_image().split('/')[-1]+'.json', 'w') as file:
                json.dump(data, file)


    def mouseMoveEvent(self, e):
        #print('heho')
        #print(e.x(), e.y())
        """if self.last_x is None: # First event.
            self.last_x = e.x()
            self.last_y = e.y()
            return # Ignore the first time."""

        #ratio_x = self.size[0]/self.size[0]
        #ratio_y = self.size[1]/self.size[1]
        self.last_x = e.x()
        self.last_y = e.y()
        #print(self.last_y, self.last_x)
        if self.X != None:
            size_true = self.img.shape

            resize_ratio = min(self.size[0]/size_true[0], self.size[1]/size_true[1])

            padd_y = (self.size[0]-size_true[0]*resize_ratio)/2
            padd_x = (self.size[1]-size_true[1]*resize_ratio)/2
            """print(self.size)
            print(size_true)
            print((self.size[1]/size_true[0], self.size[0]/size_true[1]))
            print('padd :', padd)"""
            ratio_x = size_true[1]/self.size[1]
            ratio_y = size_true[0]/self.size[0]
            self.last_x = e.x()*ratio_x+padd_x
            self.last_y = e.y()*ratio_y+padd_y
            #print(self.last_x, self.last_y)
            #print(self.bboxes)
            self.update_rects()
            self.update_image()
            self.saved = False
    def mouseReleaseEvent(self, e):
        self.last_x = None
        self.last_y = None

    def update_rects(self):
        for i in range(len(self.bboxes)):
            point = (self.last_x, self.last_y)
            b = self.bboxes[i]
            if(pointInRect(point, b)):
                self.Y[i] = 1-self.Y[i]


    def update_image(self):
        for i in range(len(self.bboxes)):
            bb = self.bboxes[i]
            if self.Y[i] == 1:
                img = cv2.rectangle(self.img, (int(bb[0]), int(bb[1])), (int(bb[0]+bb[2]), int(bb[1]+bb[3])), (0,255,0), 1)
                img = cv2.rectangle(img, (int(bb[0]), int(bb[1])-10), (int(bb[0]+30), int(bb[1])), (0,255,0), -1)
            else:
                img = cv2.rectangle(self.img, (int(bb[0]), int(bb[1])), (int(bb[0]+bb[2]), int(bb[1]+bb[3])), (0,0,255), 1)
                img = cv2.rectangle(img, (int(bb[0]), int(bb[1])-10), (int(bb[0]+30), int(bb[1])), (0,0,255), -1)
        directory_look = self.path+'/look_'+self.path.split('/')[-1]
        if not os.path.exists(directory_look):
            os.makedirs(directory_look)
        cv2.imwrite(directory_look+'/'+self.get_image().split('/')[-1], img)
        #self.photo.setPixmap(QtGui.QPixmap(directory_look+'/'+self.get_image().split('/')[-1]))

        pixmap = QtGui.QPixmap(directory_look+'/'+self.get_image().split('/')[-1])
        pixmap = pixmap.scaled(self.size[1], self.size[0], QtCore.Qt.KeepAspectRatio)
        self.photo.setPixmap(pixmap)



    def predict(self):
        if self.model_loaded:
            directory_out = self.path+'/out_'+self.path.split('/')[-1]
            if not os.path.exists(directory_out):
                os.makedirs(directory_out)
            #command = "python -m openpifpaf.predict --glob {} --image-output {} --json-output {} --force-complete-pose".format(self.get_image(), directory_out, directory_out)
            #print(command)
            #os.system(command)
            pil_im = PIL.Image.open(self.get_image()).convert('RGB')
            im = np.asarray(pil_im)

            data = openpifpaf.datasets.PilImageList([pil_im], preprocess=self.preprocess)

            loader = torch.utils.data.DataLoader(data, batch_size=1, pin_memory=True, collate_fn=openpifpaf.datasets.collate_images_anns_meta)
            for images_batch, _, __ in loader:
                predictions = self.processor.batch(self.net, images_batch, device=device)[0]
            tab_predict = [p.json_data() for p in predictions]
            with open(directory_out+'/{}.predictions.json'.format(self.get_image().split('/')[-1]), 'w') as outfile:
                json.dump(tab_predict, outfile)
            #predictions = self.processor.batch(self.net, im, device=device)[0]
            #exit(0)
            



            with open(directory_out+'/{}.predictions.json'.format(self.get_image().split('/')[-1]), 'r') as file:
                data = json.load(file)
            #print(data)
            img = cv2.imread(self.get_image())
            self.img = img
            img_out, Y, X, bboxes = run_and_rectangle(img, data, self.model)
            #print(Y, X)
            #exit(0)
            self.Y = Y
            self.X = X
            self.bboxes = bboxes

            directory_look = self.path+'/look_'+self.path.split('/')[-1]
            if not os.path.exists(directory_look):
                os.makedirs(directory_look)
            cv2.imwrite(directory_look+'/'+self.get_image().split('/')[-1], img_out)
            #self.photo.setPixmap(QtGui.QPixmap(directory_look+'/'+self.get_image().split('/')[-1]))

            pixmap = QtGui.QPixmap(directory_look+'/'+self.get_image().split('/')[-1])
            pixmap = pixmap.scaled(self.size[1], self.size[0], QtCore.Qt.KeepAspectRatio)
            self.photo.setPixmap(pixmap)
            self.photo.setMaximumSize(QtCore.QSize(self.size[1], self.size[0]))

        else:
            self.alert()
    def get_image(self):
        return self.tab_im[self.i]

    def click_directory(self):
        self.path = str(QFileDialog.getExistingDirectory(self.menuFile, "Select Directory"))
        self.tab_im = sorted(glob.glob(self.path+'/*.jpg'))+sorted(glob.glob(self.path+'/*.png'))
        #print(self.tab_im)
        self.i = 0
        if len(self.tab_im) > 0:
            #self.photo.setPixmap(QtGui.QPixmap(self.tab_im[self.i]))
            self.size = cv2.imread(self.tab_im[self.i]).shape
            if self.size[0] > 900 and self.size[1] > 1200:
                self.size = (800, 1200)
            #print(self.size)
            pixmap = QtGui.QPixmap(self.tab_im[self.i])
            pixmap = pixmap.scaled(self.size[1], self.size[0], QtCore.Qt.KeepAspectRatio)
            self.photo.setPixmap(pixmap)
            self.photo.setMaximumSize(QtCore.QSize(self.size[1], self.size[0]))

    def click(self):
        if self.saved == False:
            alert = QtWidgets.QMessageBox()
            alert.setText('Please Save your predictions first')
            alert.exec_()
        elif len(self.tab_im) != 0:

            self.size = cv2.imread(self.tab_im[self.i]).shape
            #print(self.size)
            #self.photo.setMaximumSize(QtCore.QSize(self.size[1], self.size[0]))
            
            if self.size[1] > 1300 and self.size[0] > 900:
                self.size = (800, 1200)

            #print(self.size)
            if self.i < len(self.tab_im)-1:
                self.i += 1

                pixmap = QtGui.QPixmap(self.tab_im[self.i])
                pixmap = pixmap.scaled(self.size[1], self.size[0], QtCore.Qt.KeepAspectRatio)
                self.photo.setPixmap(pixmap)
                #self.photo.setMaximumSize(QtCore.QSize(self.size[1], self.size[0]))
                
            else:
                self.i = 0
                pixmap = QtGui.QPixmap(self.tab_im[self.i])
                pixmap = pixmap.scaled(self.size[1], self.size[0], QtCore.Qt.KeepAspectRatio)
                self.photo.setPixmap(pixmap)
                #self.photo = self.photo.scaled(self.size[1], self.size[0], QtCore.Qt.KeepAspectRatio)
                #self.i += 1

            self.X = None
            self.Y = None
            self.img = None
            self.bboxes = None
            self.saved = False

    def click_back(self):
        if self.saved == False:
            alert = QtWidgets.QMessageBox()
            alert.setText('Please Save your predictions first')
            alert.exec_()
        elif len(self.tab_im) != 0:

            self.size = cv2.imread(self.tab_im[self.i]).shape

            if self.size[1] > 1300 and self.size[0] > 900:
                self.size = (800, 1200)

            if self.i == 0:
                self.i += len(self.tab_im)-1
                self.photo.setPixmap(QtGui.QPixmap(self.tab_im[self.i]))
            else:
                self.i -= 1
                self.photo.setPixmap(QtGui.QPixmap(self.tab_im[self.i]))
            self.size = cv2.imread(self.tab_im[self.i]).shape
            #print(self.size)
            self.photo.setMaximumSize(QtCore.QSize(self.size[1], self.size[0]))
            self.X = None
            self.Y = None
            self.img = None
            self.bboxes = None
            self.saved = False

    def selectFile(self):
        self.model_path = QFileDialog.getOpenFileName()[0]
        print("Trying to load the Model at :{}".format(self.model_path))
        try:
            self.model = torch.load(self.model_path, map_location=torch.device(device))
            self.model.eval()
            self.model_loaded = True
            print("SUCCESS")
        except Exception as e:
            print("ERROR while loading the model : ", e)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("YouLook - Fast annotator", "YouLook - Fast annotator"))
        self.pushButton.setText(_translate("MainWindow", "Next Image"))
        self.pushButton_2.setText(_translate("MainWindow", "Save"))
        self.pushButton_3.setText(_translate("MainWindow", "Predict"))
        self.pushButton_4.setText(_translate("MainWindow", "Previous Image"))
        self.pushButton_5.setText(_translate("MainWindow", "Load Model"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionOpen.setText(_translate("MainWindow", "Open"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    MainWindow.setWindowIcon(QtGui.QIcon('logo.png'))
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

