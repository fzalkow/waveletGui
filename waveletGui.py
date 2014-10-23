from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QApplication, QCursor
from PyQt4.QtCore import Qt

import pywt
import numpy as np
from scipy.io import wavfile

wavelet_coefficients = None

class PaintWidget(QtGui.QWidget):

    def __init__(self, boxborder=True, bordersize=0, xsize=300, ysize=300, coeff_range=[-3.,3.]):
        QtGui.QWidget.__init__(self)
        
        global wavelet_coefficients
        
        self.coeffs_color = None
        self.coeff_range=coeff_range
        
        self.bordersize = bordersize
        self.boxborder = boxborder
        
        self.box_height = None
        self.box_width = []
        
        self.xsize = xsize
        self.ysize = ysize
        
        self.drawWavelets()
    
    def paintEvent(self, event):
        paint = QtGui.QPainter()
        paint.begin(self)
        paint.drawPixmap(0, 0, self.pixmap) #load graph from pixmap
        paint.end()

    def drawWavelets(self):
    
        QApplication.setOverrideCursor(QCursor(Qt.BusyCursor))
        self.coeffs_color = self.coeffsToColor()
        self.box_width = []
                        
        ypadder = -15
        
        xsize = self.xsize
        ysize = self.ysize - (2*self.bordersize) + ypadder
        
        xwithborder = xsize + (2*self.bordersize)
        ywithborder = self.ysize + ypadder
        
        self.setFixedSize(xwithborder, ywithborder)
        
        self.pixmap = QtGui.QPixmap(xwithborder, ywithborder)
        self.pixmap.fill(QtGui.QColor('black'))
        
        paint = QtGui.QPainter()
        paint.begin(self.pixmap)
        
        coeffs_len = len(self.coeffs_color)
        
        if coeffs_len != 0:
        
            self.box_height = int(ysize / float(coeffs_len))
            
            for i, level in enumerate(self.coeffs_color):
                
                level_len = len(level)
                current_width = self.bordersize
                self.box_width.append(int(round(xsize / float(level_len))))
                
                for j, coeff in enumerate(level):
                    paint.setBrush(coeff)
                    if not self.boxborder: paint.setPen(coeff)
                    
                    paint.drawRect(current_width, (coeffs_len - i - 1)*self.box_height + self.bordersize, self.box_width[i], self.box_height)
                    current_width += self.box_width[i]
                    
        paint.end()
        self.update()
        QApplication.restoreOverrideCursor()
        
    def drawParticularWavelet(self, level, time_point):
    
        global wavelet_coefficients
    
        QApplication.setOverrideCursor(QCursor(Qt.BusyCursor))
        
        color=blue_colormap((wavelet_coefficients[level][time_point] - self.coeff_range[0]) / (self.coeff_range[1] - self.coeff_range[0]))
        
        paint = QtGui.QPainter()
        paint.begin(self.pixmap)
        paint.setBrush(color)
        if not self.boxborder: paint.setPen(color)
        
        current_width = self.bordersize + (time_point*self.box_width[level])
        coeffs_len = len(self.coeffs_color)
        
        paint.drawRect(current_width, (coeffs_len - level - 1)*self.box_height + self.bordersize, self.box_width[level], self.box_height)
        paint.end()
        
        self.update()
        QApplication.restoreOverrideCursor()
        
    def mousePressEvent(self, event):       
        global wavelet_coefficients
    
        coeffs_len = len(wavelet_coefficients) 
        level = coeffs_len - ((event.pos().y() - self.bordersize) / self.box_height) - 1
        
        if (level >= 0) and (level < coeffs_len):

            time_point = (event.pos().x() - self.bordersize) / self.box_width[level]
            
            new_number, ok = QtGui.QInputDialog.getDouble(self, 'Change Wavelet Coefficient', 'Change Wavelet Coefficient (Index %d, %d) between %f and %f:' % (level, time_point, self.coeff_range[0], self.coeff_range[1]) , wavelet_coefficients[level][time_point], self.coeff_range[0], self.coeff_range[1], 12)
            
            if ok and (new_number != wavelet_coefficients[level][time_point]):
                wavelet_coefficients[level][time_point] = new_number
                self.drawParticularWavelet(level, time_point)
          
    def coeffsToColor(self):
    
        global wavelet_coefficients
        
        vcmap = np.vectorize(blue_colormap)
        normalized = map(lambda (level): (level - self.coeff_range[0]) / (self.coeff_range[1] - self.coeff_range[0]), wavelet_coefficients)
        return map(lambda (level): vcmap(level), normalized)
          

class PlotWindow(QtGui.QMainWindow):

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        
        global wavelet_coefficients    
        
        self.signal = np.float64(np.zeros(2048))
        self.sampleRate = 44100
        self.wavelet = 'dmey'
        self.mode = 'per' # only in this mode powers of 2 give clear divisions of signal length at any scale!
        
        self.boxborder = True
        self.bordersize = 10
        
        self.coeff_range=[-3.0,3.0]
        
        wavelet_coefficients = self.getWaveletCoeffs()
        
        self.initUI()
        self.initMenu()
        
    def initUI(self):
    
        self.showMaximized()
        
        scroll = QtGui.QScrollArea()
        scroll.setWidgetResizable(True)
        
        scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        
        self.setCentralWidget(scroll)
        
        self.painter = PaintWidget(self.boxborder, self.bordersize, len(self.signal), self.geometry().height())
        
        scroll.setWidget(self.painter)
        
    def initMenu(self):
        menubar = QtGui.QMenuBar()
        fileMenu = QtGui.QMenu(menubar)
        fileMenu.setTitle('File')
        
        menuNew = QtGui.QAction('New empty Wavelet-Plane', self)
        menuNew.triggered.connect(self.newSignal)
        
        menuImport = QtGui.QAction('Import Wave-File', self)
        menuImport.triggered.connect(self.importFile)
        
        menuExport = QtGui.QAction('Export Wave-File', self)
        menuExport.triggered.connect(self.exportFile)
        
        menuSettings = QtGui.QAction('Wavelet Settings', self)
        menuSettings.triggered.connect(self.settings)
        
        menuClose = QtGui.QAction('Close', self)
        menuClose.triggered.connect(self.close)
        
        fileMenu.addAction(menuNew)
        fileMenu.addAction(menuImport)
        fileMenu.addAction(menuExport)
        fileMenu.addAction(menuSettings)
        fileMenu.addAction(menuClose)

        menubar.addAction(fileMenu.menuAction())
        
        self.setMenuBar(menubar)
        
    def getWaveletCoeffs(self):
        """level = 0
        wavelet = pywt.Wavelet(self.wavelet)
        len_sig = len(self.signal)
        for i in range(0, pywt.dwt_max_level(len_sig, wavelet)):
            if (pywt.dwt_coeff_len(len_sig, wavelet, self.mode) > self.width) or (i > self.height):
                break;
            level = i
        return pywt.wavedec(self.signal, self.wavelet, mode=self.mode, level=level)"""
        return pywt.wavedec(self.signal, pywt.Wavelet(self.wavelet), mode=self.mode)
        
    def importFile(self):
    
        global wavelet_coefficients
    
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Import Wave File', '.', '*.wav')
        if filename != '':
            self.sampleRate, data = wavfile.read(filename)
            if len(np.shape(data)) != 1:
                data = np.mean(data, axis=1)
            self.signal = np.float64(data)/np.abs(np.max(data))
            
            length = len(self.signal)
            
            if not check_power_of_two(length):
                nextpow = next_power_of_two(length)
                reply = QtGui.QMessageBox.question(self, 'Padding signal?', 'For best display your signal length has to be a power of 2. Should we pad %d zeros to your signal?\n\n(Current length: %d, next Power of 2: %d)' % (nextpow-length, length, nextpow), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
                if reply == QtGui.QMessageBox.Yes:
                    self.signal = np.append(self.signal, np.zeros(nextpow-length))
                    
            wavelet_coefficients = self.getWaveletCoeffs()
            self.painter.xsize = len(self.signal)
            
            myrange = range_of_coeffs(wavelet_coefficients)
            if myrange[0] < self.coeff_range[0]: self.coeff_range[0] = myrange[0]
            if myrange[1] > self.coeff_range[1]: self.coeff_range[1] = myrange[1]
            self.painter.coeff_range = self.coeff_range
            
            self.painter.drawWavelets()
            
    def newSignal(self):
        global wavelet_coefficients
        sizes = map(lambda(x): str(2**x), range(7, 23))
        size, ok =  QtGui.QInputDialog.getItem(self, 'Signal Size' , 'Choose your signal size:', sizes, 0, False)
        if ok:
            length = int(size)
            self.sampleRate = 44100
            self.signal = np.float64(np.zeros(length))
            wavelet_coefficients = self.getWaveletCoeffs()
            self.painter.xsize = length
            self.painter.drawWavelets()
            
    def writeFile(self, path):
        new_signal = pywt.waverec(wavelet_coefficients, pywt.Wavelet(self.wavelet), self.mode)
        new_signal *= ((2**31) - 1) / np.max(np.abs(new_signal))
        new_signal = np.int32(np.round(new_signal))
        wavfile.write(path, self.sampleRate, new_signal)
        
            
    def exportFile(self):
    
        global wavelet_coefficients
        
        filename = QtGui.QFileDialog.getSaveFileName(self, 'Export Wave File', '.', '*.wav')
        if filename != '':
            self.writeFile(filename)
            
    def settings(self):
    
        global wavelet_coefficients
        
        wavelets = pywt.wavelist()
        wavelet, ok =  QtGui.QInputDialog.getItem(self, 'Change Wavelet' , 'Change your current mother wavelet:', wavelets, wavelets.index(self.wavelet), False)
        if ok:
            self.wavelet = str(wavelet)
        
            wavelet_coefficients = self.getWaveletCoeffs()
            
            self.painter.drawWavelets()

        
def blue_colormap(brightness):
    brightness = round(255 * brightness)
    return QtGui.QColor(255 - brightness, 255 - brightness, 255)
    
# http://graphics.stanford.edu/~seander/bithacks.html#DetermineIfPowerOf2
def check_power_of_two(number):
    return (number != 0) and not (number & (number - 1))
    
# http://graphics.stanford.edu/~seander/bithacks.html#RoundUpPowerOf2
def next_power_of_two(number):
    number -= 1
    number |= number >> 1
    number |= number >> 2
    number |= number >> 4
    number |= number >> 8
    number |= number >> 16
    number += 1
    return number
    
def range_of_coeffs(coeffs):
    return (min(map(np.min, coeffs)), max(map(np.max, coeffs)))

    
if __name__ == '__main__':

    import sys
    app = QtGui.QApplication(['WaveletGui'])
    window = PlotWindow()
    window.show()
    sys.exit(app.exec_())