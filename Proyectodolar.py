# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Proyecto.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.



from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QDateEdit, QPushButton
from PyQt5 import QtCore, QtGui, QtWidgets

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import requests
import json
import pandas as pd
import sys


def read(fechainicial, fechafinal):
    try:
        url = "https://www.banxico.org.mx/SieAPIRest/service/v1/series/SF43718/datos/" + fechainicial + "/" + fechafinal
        headers = {"Accept": "application/json",
                   "Bmx-Token": "69260904c3e398685c78e54928e7129fb21c7f79443e3c8b59e5c91f8319ef47"}
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise Exception("Server error (HTTP {} - {}).".format(response.status_code, response.reason))

        jsonResponse = json.loads(response.content)
        return jsonResponse
    except Exception as e:
        print(e)

    return None


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        self.DTFechaInicial = QtWidgets.QDateEdit(Dialog)
        self.DTFechaInicial.setGeometry(QtCore.QRect(120, 10, 110, 22))
        self.DTFechaInicial.setObjectName("DTFechaInicial")
        self.DTFechaFinal = QtWidgets.QDateEdit(Dialog)
        self.DTFechaFinal.setGeometry(QtCore.QRect(120, 30, 110, 22))
        self.DTFechaFinal.setObjectName("DTFechaFinal")
        self.graphicsView = QtWidgets.QGraphicsView(Dialog)
        self.graphicsView.setGeometry(QtCore.QRect(200, 70, 191, 141))
        self.graphicsView.setObjectName("graphicsView")
        self.TVDatos = QtWidgets.QTreeView(Dialog)
        self.TVDatos.setGeometry(QtCore.QRect(10, 90, 171, 191))
        self.TVDatos.setObjectName("TVDatos")
        self.LbFechaInicial = QtWidgets.QLabel(Dialog)
        self.LbFechaInicial.setGeometry(QtCore.QRect(10, 10, 81, 20))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.LbFechaInicial.setFont(font)
        self.LbFechaInicial.setObjectName("LbFechaInicial")
        self.LbFechaFinal = QtWidgets.QLabel(Dialog)
        self.LbFechaFinal.setGeometry(QtCore.QRect(10, 30, 71, 20))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.LbFechaFinal.setFont(font)
        self.LbFechaFinal.setObjectName("LbFechaFinal")
        self.BtnConsultar = QtWidgets.QPushButton(Dialog)
        self.BtnConsultar.setGeometry(QtCore.QRect(250, 20, 75, 23))
        self.BtnConsultar.setObjectName("BtnConsultar")


        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.LbFechaInicial.setText(_translate("Dialog", "Fecha Inicial"))
        self.LbFechaFinal.setText(_translate("Dialog", "Fecha Final"))
        self.BtnConsultar.setText(_translate("Dialog", "Consultar"))



# Resto del código...

class VentanaPrincipal(object):
    def __init__(self):
        self.dialog = QtWidgets.QDialog()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self.dialog)
        self.dialog.show()

        self.ui.BtnConsultar.clicked.connect(self.load_data)

        self.is_maximized = False
        self.ui.graphicsView.mousePressEvent = self.toggle_maximize

    def toggle_maximize(self, event):
        if not self.is_maximized:
            self.dialog.showMaximized()
            self.is_maximized = True
        else:
            self.dialog.showNormal()
            self.is_maximized = False

    def load_data(self):
        fechaDesde = self.ui.DTFechaInicial.date().toString("yyyy-MM-dd")
        fechaHasta = self.ui.DTFechaFinal.date().toString("yyyy-MM-dd")

        resultado = read(fechaDesde, fechaHasta)
        if resultado is not None:
            df = pd.DataFrame(resultado['bmx']['series'][0]['datos'])
            df['dato'] = df['dato'].astype(float)
            self.plot_data(df)

            # Obtener el precio del dólar actual
            precio_dolar = self.get_current_dollar_price()
            print("Precio del dólar al momento:", precio_dolar)

            # Mostrar los cambios de precios del dólar en el TVDatos
            self.show_dollar_price_changes(df)

    def show_dollar_price_changes(self, data):
        model = QtGui.QStandardItemModel()
        model.setHorizontalHeaderLabels(["Fecha", "Dato"])

        # Obtener los datos de fecha y precio del DataFrame
        fechas = data['fecha']
        datos = data['dato']

        # Calcular los cambios de precios del dólar
        cambios = datos.diff().fillna(0)

        # Agregar las filas al modelo
        for fecha, cambio in zip(fechas, cambios):
            item_fecha = QtGui.QStandardItem(fecha)
            item_cambio = QtGui.QStandardItem(str(cambio))
            model.appendRow([item_fecha, item_cambio])

        self.ui.TVDatos.setModel(model)

    def get_current_dollar_price(self):
        try:
            access_key = "TU_ACCESS_KEY"  # Reemplaza con tu clave de acceso a Fixer.io
            base_currency = "USD"

            # Realizar la solicitud GET a la API de tipo de cambio
            url = f"http://data.fixer.io/api/latest?access_key={access_key}&base={base_currency}"
            response = requests.get(url)

            if response.status_code != 200:
                raise Exception("Error en la solicitud HTTP.")

            # Analizar la respuesta JSON
            jsonResponse = json.loads(response.content)
            rates = jsonResponse.get("rates", {})
            precio_dolar = rates.get("MXN")

            return precio_dolar

        except Exception as e:
            print("Error al obtener el precio del dólar:", e)

        return None

    def plot_data(self, data):
        fechas = data['fecha']
        datos = data['dato']

        # Crear un nuevo gráfico de línea
        fig = Figure()
        ax = fig.add_subplot(111)
        ax.plot(fechas, datos)

        # Configurar las etiquetas de los ejes y el título del gráfico
        ax.set_xlabel('Fecha')
        ax.set_ylabel('Dato')
        ax.set_title('Datos de cambio de divisas')
        ax.tick_params(axis='x', rotation=90)

        # Crear el widget de Matplotlib
        canvas = FigureCanvas(fig)

        # Agregar el widget de Matplotlib al diálogo
        layout = QVBoxLayout()
        layout.addWidget(canvas)
        self.ui.graphicsView.setLayout(layout)


# Crear la aplicación PyQt y la ventana principal
app = QApplication(sys.argv)
ventana = VentanaPrincipal()
sys.exit(app.exec_())
