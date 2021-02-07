from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import  QTableWidget,QTableWidgetItem,QMessageBox
from scapy.all import *
from settingForm import settingForm
from mainFormUI import Ui_MainWindow
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from win10toast  import ToastNotifier
import sys,threading,time,socket,yaml,base64,smtplib,random,os


class mainForm(QtWidgets.QMainWindow):
  
    def __init__(self):
        # >>>> Varables <<<<
        self.dir=os.getcwd()+"\\"
        self.errordata=""
        self.filterP=""
        self.tableIndex=0
        self.listIndex=0
        self.packetList={}
        self.color={}
        self.toplamPaket=0
        with open(self.dir+'configuration.yaml') as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)
        self.table = {num:name[8:] for name,num in vars(socket).items() if name.startswith("IPPROTO")}
        # >>>> Form <<<<
        super(mainForm,self).__init__()
        self.mainUI=Ui_MainWindow()
        self.mainUI.setupUi(self)
        self.tableUI()
        self.mainUI.menubar.triggered.connect(self.openFromConf)
        self.mainUI.tableWidget.setHorizontalHeaderLabels(('No','Time','Source','Destination','Protocol','Length','Info'))
        # >>>> Time <<<<
        self.startTime=time.time()
        self.countTime=time.time()


    def tableUI(self):
        self.header = self.mainUI.tableWidget.horizontalHeader()
        self.header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)       
        self.header.setSectionResizeMode(0,QtWidgets.QHeaderView.ResizeToContents )
        self.header.setSectionResizeMode(1,QtWidgets.QHeaderView.Stretch )
        self.header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        self.header.setSectionResizeMode(4,QtWidgets.QHeaderView.ResizeToContents )
        self.header.setSectionResizeMode(5,QtWidgets.QHeaderView.ResizeToContents )  
        self.header.setSectionResizeMode(6, QtWidgets.QHeaderView.Stretch)
          
    def start(self):
        threading.Thread(target=self.run).start()    
    def run(self,Store=False,Filter=["tcp","udp","icmp"]):
        for i in Filter:
            i.upper()
            self.filterP+=i+" or "
        self.filterP=self.filterP.rstrip(" or")
        sniff(prn=self.filter, store=Store,filter=self.filterP)

    def filter(self,data): 
        try:
            self.ip =data[1].src if data[1].src!="192.168.1.106" else data[1].dst
            self.protokol=self.table[data[1].proto]
            
            # >>>> Listeye ekleme <<<<
            if self.ip not in self.packetList:
                self.packetList.update({
                    self.ip:{
                        "protokol":{
                            self.protokol:0
                        },
                        "id":self.listIndex,
                        "toplam":self.toplamPaket
                    }
                })
                self.listIndex+=1
            elif self.protokol not in self.packetList[self.ip]['protokol']:
                self.packetList[self.ip]['protokol'].update({self.protokol:0})
            
            self.packetList[self.ip]['protokol'][self.protokol]+=1
            self.packetList[self.ip]['toplam']+=1

            self.updateTable(data)
            
            if((time.time()-self.countTime)>=self.config["Genel"]["time"]):
                for j in self.packetList.values():
                    self.control(j["toplam"],j["id"])
                
                self.countTime=time.time()
                self.packetList.clear()
                self.listIndex=0
        except AttributeError:
            self.errordata=f"{time.time()}|{data}\n"
            with open("systemerror.log","a") as log:
                log.write(self.errordata)

    def optimize(self):
        fullPaket=0
        for i in self.packetList.values():
            fullPaket+=i["toplam"]
        print(f"Pacge Full:{fullPaket}\nLength:{len(self.packetList.values())}\nAvg:{int(fullPaket/len(self.packetList.values()))}")
        
    # fonkisyonların ayrı threedlere çalıştırılması tavsiye edilmektedir !
    def control(self,toplamPaket,id):
        for i in range(len(self.config["Kontrol"]["eylem"])):
            if self.config["Kontrol"]["eylem"][i]=="Console Log" and int(self.config["Kontrol"]["psayisi"][i])<= toplamPaket:
                self.log(id,self.config["Kontrol"]["mesaj"][i])
            elif self.config["Kontrol"]["eylem"][i]=="Popup" and int(self.config["Kontrol"]["psayisi"][i])<= toplamPaket:
                self.log(id,self.config["Kontrol"]["mesaj"][i])
            elif self.config["Kontrol"]["eylem"][i]=="Alarm" and int(self.config["Kontrol"]["psayisi"][i])<= toplamPaket:
                self.log(id,self.config["Kontrol"]["mesaj"][i])
            elif self.config["Kontrol"]["eylem"][i]=="Mail" and int(self.config["Kontrol"]["psayisi"][i])<= toplamPaket:
               self.log(id,self.config["Kontrol"]["mesaj"][i])#self.funcMail("Uyarı !",self.config["Kontrol"]["mesaj"][i])  

    def log(self,id,msg):
        with open("unexpected.log","a") as log:
            log.write(f"[+] {msg} | {self.getitem(id)} | {self.startTime}\n")

    def funcMail(self,status,msg):
        self.mail = smtplib.SMTP("smtp.gmail.com",587)
        self.mail.ehlo()
        self.mail.starttls()
        self.mail.login(self.config["Mail"]["mail"], base64.b64decode(self.config["Mail"]["password"]).decode("ascii"))
        self.mesaj = MIMEMultipart()
        self.mesaj["To"]=self.config["Mail"]["to"]
        self.mesaj["From"] = self.config["Mail"]["mail"]
        self.mesaj["Subject"] = status   
        body_text = MIMEText(msg, "plain")  
        self.mesaj.attach(body_text)
        self.mail.sendmail(self.mesaj["From"], self.mesaj["To"], self.mesaj.as_string())
        print("Mail başarılı bir şekilde gönderildi.")
        self.mail.close()

    def funcLog(self,id,msg):
        print(f"[+] {msg} .Pkaet bilgileri: {self.getitem(id)}")
    def funcAlarm(self,id,msg):
        print(f"[+] {msg} .Pkaet bilgileri: {self.getitem(id)}")
    def funcPopup(self,id,msg):
        toast=ToastNotifier()
        title="Uyarı"
        icon="icon.ico"
        toast.show_toast(title,msg,icon_path=icon,duration=4000)

    def getitem(self,id):
        for item in self.packetList.items():
            if(item[1]['id']==id):
                return item

    def updateTable(self,data):
        self.mainUI.tableWidget.setRowCount(self.tableIndex+1)
        self.mainUI.tableWidget.setItem(self.tableIndex,0, QTableWidgetItem(str(self.tableIndex)))
        self.mainUI.tableWidget.setItem(self.tableIndex,1, QTableWidgetItem(str(time.time()-self.startTime)[:7]))
        self.mainUI.tableWidget.setItem(self.tableIndex,2, QTableWidgetItem(str(data[1].src)))
        self.mainUI.tableWidget.setItem(self.tableIndex,3, QTableWidgetItem(str(data[1].dst)))
        self.mainUI.tableWidget.setItem(self.tableIndex,4, QTableWidgetItem(str(self.table[data[1].proto])))
        self.mainUI.tableWidget.setItem(self.tableIndex,5, QTableWidgetItem(str(data[1].len)))
        try:
            self.mainUI.tableWidget.setItem(self.tableIndex,6, QTableWidgetItem(f"{data[1].sport} → {data[1].dport} Window={data[1].window} Seq={data[1].seq}"))
        except AttributeError:
            self.mainUI.tableWidget.setItem(self.tableIndex,6, QTableWidgetItem(" "))
        finally:
            # >>>> Coloring <<<<
            if self.ip not in self.color:
                self.color.update({self.ip:[random.randint(150,254),random.randint(100,254),random.randint(150,254)]})
    
            c=self.color[self.ip]
                          #┌> table row sayısı
            for i in range(7):
                self.mainUI.tableWidget.item(self.tableIndex,i).setBackground(QtGui.QColor(c[0],c[1],c[2]))
            self.mainUI.tableWidget.scrollToBottom()
            self.tableIndex+=1

   

    def openFromConf(self):
        self.app=QtWidgets.QMainWindow()
        self.window=settingForm()
        self.window.show()
    
    
app=QtWidgets.QApplication(sys.argv)
window=mainForm()
window.start()
window.show()
sys.exit(app.exec_())

