import Tkinter as tk
import imageProcessor

BAND_WIDTH = 16

class collapsingFrame(tk.Frame):
    def __init__(self, master, orientation = tk.HORIZONTAL, inisplit = 0.8, buttConf = 'RMm'):
        tk.Frame.__init__(self, master)
        self.buttIcon = {}
        self.buttIcon['M'] = imageProcessor.getIconImageTk(imageProcessor.WINDOW_MAX)
        self.buttIcon['m'] = imageProcessor.getIconImageTk(imageProcessor.WINDOW_MIN)
        self.buttIcon['R'] = imageProcessor.getIconImageTk(imageProcessor.WINDOW_RESTORE)
        if orientation in [tk.VERTICAL, tk.HORIZONTAL]:
            self.orientation = orientation
        else:
            raise AttributeError, orientation
        self.buttConf = buttConf
        self.cursor = 'sb_v_double_arrow' if orientation == tk.HORIZONTAL else 'sb_h_double_arrow'
        self.dim = 'height' if orientation == tk.HORIZONTAL else 'width'
        self.bind('<Configure>', self.configure, add = '+')
        self.split = inisplit
        self.bandRelDim = 0
        self.frstWidget = tk.Frame(self)
        self.scndWidget = tk.Frame(self)
        self.setGUI()
        self.setWidgetLayout(buttConf[0])
        
    def clickButton(self, nButt):
        boton = self.b1 if nButt else self.b2
        btTxt = boton['text']
        self.comButton(btTxt)
        
    def setWidgetLayout(self, btnTxt):
        if btnTxt == 'M': return self.wmax()
        if btnTxt == 'm': return self.wmin()
        self.wdef()
        
    def configure(self, event):
        totDim = event.height if self.orientation == tk.HORIZONTAL else event.width
        self.bandRelDim = float((1.0*BAND_WIDTH)/totDim)
        btnTxt = self.nxtButton()
        self.setWidgetLayout(btnTxt)

    def nxtButton(self):
        buttons = [getattr(self, 'b' + str(k+1)) for k in range(len(self.buttConf)-1)]
        return set(self.buttConf).difference(map(lambda x: x['text'][1], buttons)).pop()
        
    def setGUI(self):
        master = self
        self.band = tk.Frame(master, bg = 'red', cursor = self.cursor)
        self.band[self.dim] = BAND_WIDTH
        self.band.bind('<ButtonPress-1>', self.b1pressh)
        self.band.bind('<Button1-Motion>', self.b1motion)
        self.band.bind('<ButtonRelease-1>', self.b1releaseh)
        for k, btnTxt in enumerate(self.buttConf[1:]):
            buttLabel = str(k+1) + btnTxt
            setattr(self, 'b' + str(k+1), tk.Button(master, bg = 'red', text = buttLabel, image = self.buttIcon[btnTxt], command = lambda x = buttLabel:self.comButton(x)))
        
    def comButton(self, btTxt):
        nBtn, btId = btTxt
        self.setWidgetLayout(btId)
        btnTxt = self.nxtButton()        
        boton = getattr(self, 'b' + nBtn)
        boton['text'] = nBtn + btnTxt
        boton['image'] = self.buttIcon[btnTxt]
        boton['command'] = lambda:self.comButton(boton['text'])

    def trn(self,**kwargs):
        if self.orientation == tk.HORIZONTAL: return kwargs
        answer = {}
        for k in kwargs:
            if k.endswith('x'): newK = k[:-1] + 'y'
            elif k.endswith('y'): newK = k[:-1] + 'x'
            elif k.endswith('width'): newK = k.replace('width', 'height')
            elif k.endswith('height'): newK = k.replace('height', 'width')
            else: newK = k
            answer[newK] = kwargs[k]
        return answer
        
    def wdef(self):
        splitComp = 1 - self.split - self.bandRelDim
        trn = self.trn
        self.frstWidget.place(**trn(relheight = self.split, relwidth = 1.0))
        self.placeSepBand()
        self.scndWidget.place(**trn(rely = self.split, y = BAND_WIDTH, relheight =  splitComp, relwidth = 1.0))
        self.band['cursor'] = self.cursor
        
    def placeSepBand(self, kwargs = None):
        kwargs = kwargs or {}
        trn = self.trn
        placeInfo = trn(rely = self.split, y = 0, relwidth = 1.0)
        placeInfo.update(kwargs)
        self.band.place(**placeInfo)
        for k in range(len(self.buttConf)-1):
            widget = getattr(self,'b' + str(k+1))
            placeInfo = trn(rely = self.split, relx = 1.0, y = 0, x = -(k+1)*BAND_WIDTH, height = BAND_WIDTH, width = BAND_WIDTH)
            if self.orientation == tk.VERTICAL: 
                placeInfo['rely'] = 0
                placeInfo['y'] = -(placeInfo['y'] + BAND_WIDTH)
            if kwargs: placeInfo.update(kwargs)
            widget.place(**placeInfo)
            
    def wmax(self):
        self.frstWidget.place_forget()
        self.scndWidget.place(**self.trn(rely = 0, y = BAND_WIDTH, relheight = 1.0 - self.bandRelDim, relwidth = 1.0))
        kwargs = self.trn(rely = 0, y = 0)
        self.placeSepBand(kwargs)
        self.band['cursor'] = 'arrow'
        
    def wmin(self):
        self.scndWidget.place_forget()
        self.frstWidget.place(**self.trn(rely = 0, relheight = 1 - self.bandRelDim, relwidth = 1.0))
        kwargs = self.trn(rely = 1.0, y = -BAND_WIDTH)
        self.placeSepBand(kwargs)
        self.band['cursor'] = 'arrow'

    def b1pressh(self, event):
        if 'R' != self.nxtButton(): return
        self.mband = tk.Frame(self, bg = 'grey', cursor = self.cursor)
        self.mband[self.dim] = BAND_WIDTH
        kwargs = self.trn(rely = self.split, relwidth = 1.0)  
        self.mband.place(**kwargs)

    def b1motion(self, event):
        if 'R' != self.nxtButton(): return
        mwidth = self.master.winfo_height() if self.orientation == tk.HORIZONTAL else self.master.winfo_width()
        mmin = 0
        mmax = 1 - self.bandRelDim
        pos = event.y if self.orientation == tk.HORIZONTAL else event.x
        puPos = float((self.split*mwidth + pos)/mwidth)
        pixels = min(mmax,max(mmin,puPos))
        self.mband.place(**self.trn(rely = pixels))

    def b1releaseh(self, event):
        if 'R' != self.nxtButton(): return
        if self.orientation == tk.HORIZONTAL:
            mwidth = self.master.winfo_height()
            pos = event.y
        else:
            mwidth = self.master.winfo_width()
            pos = event.x
        split = (float(self.split * mwidth) + pos)/float(mwidth)
        self.split = max(0.0,min(1.0 - float(BAND_WIDTH)/float(mwidth), split))
        self.mband.place_forget()
        self.wdef()
        pass

if __name__ == '__main__':
    root = tk.Tk()
    motherFrame = collapsingFrame(root, tk.VERTICAL, inisplit = 0.3,buttConf = 'RM')
    motherFrame.config(height = 200, width = 200)
    motherFrame.pack(side = tk.TOP, fill = tk.BOTH, expand = tk.YES)
    tk.Label(motherFrame.frstWidget, text = 'Panel IZQUIERDO\nEl boton solo presenta o oculta el panel').pack(side = tk.TOP, fill = tk.BOTH, expand = tk.YES)
    test = collapsingFrame(motherFrame.scndWidget, tk.HORIZONTAL)
    test.pack(side = tk.TOP, fill = tk.BOTH, expand = tk.YES)
    tk.Button(test.frstWidget, text = 'Panel de ARRIBA').pack(side = tk.TOP, fill = tk.BOTH, expand = tk.YES)
    for k in range(5):
        tk.Button(test.scndWidget, text = 'Frame No. ' + str(k)).pack(side = tk.TOP, fill = tk.BOTH, expand = tk.YES)
    pass
    root.mainloop()