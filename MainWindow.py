from ast import main
from ctypes.wintypes import HBITMAP
import sys
import numpy as np
from PyQt5.QtWidgets import *
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtCore import QDate
from PyQt5.QtCore import QTime
import cv2
from PyQt5 import QtGui
import getdb
import base64
from datetime import datetime
from dateutil.relativedelta import relativedelta

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setLayout(self.layout)
        self.setGeometry(500, 500, 1800, 500)
    def initUI(self):
        # db 통째로 불러오기
        self.data = getdb.GetData("0","temperature")
        # 불러온 db를 날짜 기준으로 슬라이싱
        self.current_data_by_date = None

        main_layout = QVBoxLayout()
        
        info_layout = QHBoxLayout()
        
        s_dateedit = QDateEdit(self)
        s_dateedit.setDate(QDate.currentDate())
        s_dateedit.setMinimumDate(QDate(1900, 1, 1))
        s_dateedit.setMaximumDate(QDate(2100, 12, 31))
        s_timeedit = QTimeEdit(self)
        s_timeedit.setTime(QTime.currentTime())
        s_timeedit.setTimeRange(QTime(3, 00, 00), QTime(23, 30, 00))
        s_timeedit.setDisplayFormat('hh:mm:ss')
        blank = QLabel("~")
        blank.resize(100,100)
        e_dateedit = QDateEdit(self)
        e_dateedit.setDate(QDate.currentDate())
        e_dateedit.setMinimumDate(QDate(1900, 1, 1))
        e_dateedit.setMaximumDate(QDate(2100, 12, 31))
        e_timeedit = QTimeEdit(self)
        e_timeedit.setTime(QTime.currentTime())
        e_timeedit.setTimeRange(QTime(3, 00, 00), QTime(23, 30, 00))
        e_timeedit.setDisplayFormat('hh:mm:ss')

        m_id_cb = QComboBox()
        # list는 나중에 db에서 받아와야 함
        for i in ["0","1","2","3"]:
            m_id_cb.addItem(i)
        db_cb = QComboBox()
        for i in self.get_coll_from_db("test-db"):
            db_cb.addItem(i)
        submit = QPushButton('조회')


        info_layout.addWidget(s_dateedit)
        info_layout.addWidget(s_timeedit)
        #info_layout.addWidget(blank)
        info_layout.addWidget(e_dateedit)
        info_layout.addWidget(e_timeedit)
        info_layout.addWidget(m_id_cb)
        info_layout.addWidget(db_cb)
        info_layout.addWidget(submit)

        visual_layout = QHBoxLayout()
        self.data_table = QTableWidget(self)
        self.lbl_img = QLabel()
        self.fig = plt.Figure()
        self.canvas = FigureCanvas(self.fig)

        self.data_table.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.lbl_img.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.canvas.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        visual_layout.addWidget(self.data_table)
        visual_layout.addWidget(self.canvas)
        visual_layout.addWidget(self.lbl_img)


        main_layout.addLayout(info_layout)
        main_layout.addLayout(visual_layout)
        self.layout = main_layout

        # chbox_list는 table_widget에 data가 들어올때 각각의 button이 추가된다.
        self.chbox_list = []

        submit.clicked.connect(lambda _: self.onClick_to_submit(
            m_id_cb.currentText(),db_cb.currentText(),
            s_dateedit.date().toPyDate(),
            s_timeedit.time().toPyTime(),
            e_dateedit.date().toPyDate(),
            e_timeedit.time().toPyTime()
        ))



    def get_item_from_db(self,db,collection, query=""):
        m = getdb.GetMongo()
        get_db = m.read_mongo(db,collection,query,get_pd=False)
        r = []
        for i in get_db:
            r.append(str(i['m_id']))
        return r
    def get_coll_from_db(self,db):
        m = getdb.GetMongo()
        l = list(m.read_collection_list(db=db))
        l.remove('image-test')
        return l
    def onClick_to_submit(self, m_id,spec,s_date,s_time,e_date,e_time):
        # current_data_by_date 전역변수를 바꾼다.
        s_datetime = "%s %s" % (s_date,str(s_time)[:8])
        e_datetime = "%s %s" % (e_date,str(e_time)[:8])
        # m_id 와 spec이 다를때 새로 불러오기
        self.data = self.data.get_data_from_mongo(m_id,spec)
        # date를 기준으로 불러온 데이터를 슬라이싱
        self.current_data_by_date = self.data.get_data_from_mongo_by_date(s_datetime,e_datetime)
        # 새로운 테이블과 그래프를 그린다
        self.get_data_by_datetime(new_table=True)     
    def get_data_by_datetime(self,new_table=False,marker_list=[]):
        temp_pd = self.current_data_by_date
        # data_table 에 data 띄우기
        if new_table:
            self.create_table_widget(self.data_table,temp_pd)
        # graph 초기화
        self.fig.clf()
        ax = self.fig.add_subplot(111)
        ax.plot(temp_pd['datetime'],temp_pd['temp'])
        ax.invert_yaxis()
        ax.set_title("Temperature")
        #ax.legend()
        #marker_list 가 있을때만 마커 찍기
        if marker_list:
            for i,v in enumerate(temp_pd['datetime']):
                if i in marker_list:
                    # marker 찍을때 사진도 띄우기
                    self.get_photo_by_datetime(temp_pd['m_id'][i],temp_pd['datetime'][i])
                    height = temp_pd['temp'][i]
                    #ax.text(v, height, str(v) + " ~ Value : " +str(height))
                    ax.text(v, height, "V")
        self.canvas.draw()
    def create_table_widget(self, widget, df):
        widget.setRowCount(len(df.index))
        widget.setColumnCount(len(df.columns)+1)
        # table header label에 marker 추가
        widget.setHorizontalHeaderLabels(list(df.columns) + ['marker'])
        widget.setVerticalHeaderLabels(map(lambda x: str(x),df.index))
        # chbox_list 초기화
        self.chbox_list = []
        for row_index, row in enumerate(df.index):
            # chbox_list 에 새로운 check box 추가
            marker_button = QPushButton('확인')
            self.chbox_list.append(marker_button)
            widget.setCellWidget(row_index,len(df.columns), marker_button)
            for col_index, column in enumerate(df.columns):
                value = df.loc[row][column]
                item = QTableWidgetItem(str(value))
                widget.setItem(row_index, col_index, item)
        widget.resizeRowsToContents()
        #각 생성한 버튼에 동작을 추가한다.
        self.connection_signal_to_a_button(self.chbox_list,0)
    def connection_signal_to_a_button(self,list,i):
        if list:
            list[0].clicked.connect(lambda _: self.get_data_by_datetime(marker_list=[i]))
            self.connection_signal_to_a_button(list[1:],i+1)
        else:
            return 0
    def get_photo_by_datetime(self,m_id,s_datetime):       
        s_datetime = s_datetime.to_pydatetime()
        e_datetime = s_datetime + relativedelta(minutes=50)
        query = {"m_id" : m_id, "datetime" : { "$gt" : s_datetime, "$lt" : e_datetime}}
        get_photo = getdb.GetMongo().read_mongo("test-db","image-test",query=query)
        if get_photo is None:
            self.lbl_img.setText("No picture at {}".format(s_datetime.strftime("%Y-%m-%d %H:%M:%S")))
            return 0
        jpg_original = base64.b64decode(get_photo['photo'][0])
        jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
        img = cv2.imdecode(jpg_as_np, flags=1)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h,w,c = img.shape
        qImg = QtGui.QImage(img.data, w, h, w*c, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(qImg)
        self.lbl_img.setPixmap(pixmap)

            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    app.exec_()

