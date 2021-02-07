import yaml,base64,sys,os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import  QTableWidget,QTableWidgetItem,QMessageBox
from settingFormUI import Ui_settingForm

class settingForm(QtWidgets.QMainWindow):
    def __init__(self):
        self.dir=os.getcwd()+"\\"
        with open(self.dir+'configuration.yaml') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        self.tableIndex=len(config["Kontrol"]["eylem"])
        self.p=config["Kontrol"]

        super(settingForm,self).__init__()
        self.settingUI=Ui_settingForm()
        self.settingUI.setupUi(self)
        self.tableUI()
        self.settingUI.tableWidget.setHorizontalHeaderLabels(('Paket Sayısı','Mesaj','Eylem'))
        self.fill()
        self.settingUI.pushButton.clicked.connect(self.saveConfig)
        self.settingUI.pushButton_2.clicked.connect(self.addTable)

    def tableUI(self):
        self.header = self.settingUI.tableWidget.horizontalHeader()
        self.header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)       
        self.header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
     

    def addTable(self):
        self.settingUI.tableWidget.setRowCount(self.tableIndex+1)
        self.settingUI.tableWidget.setItem(self.tableIndex,0, QTableWidgetItem(
            self.settingUI.lineEdit.text()
        ))
        self.settingUI.tableWidget.setItem(self.tableIndex,1, QTableWidgetItem(
            self.settingUI.lineEdit_2.text()
        ))
        self.settingUI.tableWidget.setItem(self.tableIndex,2, QTableWidgetItem(
            self.settingUI.comboBox.currentText()
        ))
        
        self.p["psayisi"].append(self.settingUI.lineEdit.text())
        self.p["mesaj"].append(self.settingUI.lineEdit_2.text())
        self.p["eylem"].append(self.settingUI.comboBox.currentText())
        self.saveConfig()
        self.tableIndex+=1

    def saveConfig(self):
        config = {
            "Genel":{
                'time':self.settingUI.spinBox.value(),
                },
            "Kontrol":self.p,
            "Mail":{
                'to':self.settingUI.lineEdit_3.text(),
                'mail':self.settingUI.lineEdit_4.text(),
                'password':base64.b64encode(self.settingUI.lineEdit_5.text().encode("ascii"))
            }
        }
        with open(self.dir+'configuration.yaml', 'w') as f:
            yaml.dump(config, f)

        QMessageBox.about(self,"Basarili", "Konfigirasyon güncellendi")
        print("[+] Konfigirasyon güncellendi")



    def fill(self):
        with open(self.dir+'configuration.yaml') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        # table 
        for i in range(len(config["Kontrol"]["eylem"])):
            self.settingUI.tableWidget.setRowCount(len(config["Kontrol"]["eylem"]))
            self.settingUI.tableWidget.setItem(i,0, QTableWidgetItem(
                config["Kontrol"]["psayisi"][i]
            ))
            self.settingUI.tableWidget.setItem(i,1, QTableWidgetItem(
                config["Kontrol"]["mesaj"][i]
            ))
            self.settingUI.tableWidget.setItem(i,2, QTableWidgetItem(
                config["Kontrol"]["eylem"][i]
            ))

        self.settingUI.spinBox.setValue(config['Genel']["time"])

        self.settingUI.lineEdit_3.setText(config['Mail']["to"])
        self.settingUI.lineEdit_4.setText(config['Mail']["mail"])
        self.settingUI.lineEdit_5.setText(
            base64.b64decode(config["Mail"]["password"]).decode("ascii")
            )
        print("[+] Tablo dolduruldu")

   

