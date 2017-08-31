from Tkinter import *
import tkFileDialog
import tkSimpleDialog
import matplotlib.pyplot as pl
import PIL
from PIL import Image
from PIL import ImageTk

def vp_start_econgui(host_gui=None):
    '''Starting point when module is the main routine.'''
    global top, root, gui
    gui = host_gui
    root = Tk()
    top = New_Toplevel_1 (root)
    root.resizable(width=False, height=False)
    root.mainloop()

def destroy_New_Toplevel_1():
    global w
    w.destroy()
    w = None

class New_Toplevel_1:

    def __init__(self, top=None):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9' # X11 color: 'gray85'
        _ana1color = '#d9d9d9' # X11 color: 'gray85'
        _ana2color = '#d9d9d9' # X11 color: 'gray85'
        font10 = "-family {DejaVu Sans Mono} -size 15 -weight normal "  \
            "-slant roman -underline 0 -overstrike 1"
        font11 = "-family {DejaVu Sans Mono} -size 15 -weight bold "  \
            "-slant roman -underline 0 -overstrike 0"
        font9 = "-family {DejaVu Sans Mono} -size 15 -weight normal "  \
            "-slant roman -underline 0 -overstrike 0"

        top.geometry("1031x593+89+80")
        top.title('Economic Disease Burden')
        top.configure(background="#135bd9")
        top.configure(highlightcolor="black")
        top.configure(cursor='pencil')

        self.Label1 = Label(top)
        self.Label1.place(relx=0.01, rely=0.03, height=18, width=126)
        self.Label1.configure(activebackground="#135bd9")
        self.Label1.configure(activeforeground="white")
        self.Label1.configure(background="#135bd9")
        self.Label1.configure(text='''Abs Labor Charge''')

        self.Label15 = Label(top)
        self.Label15.place(relx=0.01, rely=0.07, height=18, width=126)
        self.Label15.configure(activebackground="#f9f9f9")
        self.Label15.configure(background="#135bd9")
        self.Label15.configure(text='''Labor Hours''')

        self.Label14 = Label(top)
        self.Label14.place(relx=-.017, rely=0.11, height=18, width=126)
        self.Label14.configure(activebackground="#f9f9f9")
        self.Label14.configure(background="#135bd9")
        self.Label14.configure(text='''Wage/hr''')

        self.Label5 = Label(top)
        self.Label5.place(relx=0.02, rely=0.15, height=18, width=126)
        self.Label5.configure(activebackground="#f9f9f9")
        self.Label5.configure(background="#135bd9")
        self.Label5.configure(text='''Tuition Rate/day''')

        self.Label4 = Label(top)
        self.Label4.place(relx=0.0, rely=0.19, height=18, width=126)
        self.Label4.configure(activebackground="#f9f9f9")
        self.Label4.configure(background="#135bd9")
        self.Label4.configure(text='''Clinic Cost/day''')

        self.Label6 = Label(top)
        self.Label6.place(relx=-0.003, rely=0.23, height=18, width=126)
        self.Label6.configure(activebackground="#f9f9f9")
        self.Label6.configure(background="#135bd9")
        self.Label6.configure(text='''SES Bot''')

        self.Label7 = Label(top)
        self.Label7.place(relx=-0.017, rely=0.27, height=18, width=126)
        self.Label7.configure(activebackground="#f9f9f9")
        self.Label7.configure(background="#135bd9")
        self.Label7.configure(text='''SES Top''')

        self.Entry1 = Entry(top)
        self.Entry1.place(relx=0.17, rely=0.03, relheight=0.03, relwidth=0.14)
        self.Entry1.configure(background="white")
        self.Entry1.configure(font="TkFixedFont")
        self.Entry1.configure(selectbackground="#c4c4c4")

        self.Entry2 = Entry(top)
        self.Entry2.place(relx=0.19, rely=0.07, relheight=0.03, relwidth=0.14)
        self.Entry2.configure(background="white")
        self.Entry2.configure(font="TkFixedFont")
        self.Entry2.configure(selectbackground="#c4c4c4")

        self.Entry3 = Entry(top)
        self.Entry3.place(relx=0.17, rely=0.11, relheight=0.03, relwidth=0.14)
        self.Entry3.configure(background="white")
        self.Entry3.configure(font="TkFixedFont")
        self.Entry3.configure(selectbackground="#c4c4c4")

        self.Entry4 = Entry(top)
        self.Entry4.place(relx=0.19, rely=0.15, relheight=0.03, relwidth=0.14)
        self.Entry4.configure(background="white")
        self.Entry4.configure(font="TkFixedFont")
        self.Entry4.configure(selectbackground="#c4c4c4")

        self.Entry5 = Entry(top)
        self.Entry5.place(relx=0.17, rely=0.19, relheight=0.03, relwidth=0.14)
        self.Entry5.configure(background="white")
        self.Entry5.configure(font="TkFixedFont")
        self.Entry5.configure(selectbackground="#c4c4c4")

        self.Entry6 = Entry(top)
        self.Entry6.place(relx=0.19, rely=0.23, relheight=0.03, relwidth=0.14)
        self.Entry6.configure(background="white")
        self.Entry6.configure(font="TkFixedFont")
        self.Entry6.configure(selectbackground="#c4c4c4")

        self.Entry7 = Entry(top)
        self.Entry7.place(relx=0.17, rely=0.27, relheight=0.03, relwidth=0.14)
        self.Entry7.configure(background="white")
        self.Entry7.configure(font="TkFixedFont")
        self.Entry7.configure(selectbackground="#c4c4c4")

        self.Button1 = Button(top)
        self.Button1.place(relx=0.02, rely=0.35, height=26, width=157)
        self.Button1.configure(activebackground="#d9d9d9")
        self.Button1.configure(background="#d9d938")
        self.Button1.configure(font=font9)
        self.Button1.configure(text='''Materials''')
        self.Button1.configure(cursor='crosshair')
        self.Button1.configure(command=lambda: but1Press())

        self.Button2 = Button(top)
        self.Button2.place(relx=0.18, rely=0.35, height=26, width=157)
        self.Button2.configure(activebackground="#d9d9d9")
        self.Button2.configure(background="#d9d938")
        self.Button2.configure(font=font9)
        self.Button2.configure(text='''Interpolate''')
        self.Button2.configure(cursor='crosshair')
        self.Button2.configure(command=lambda: but2Press())

        self.Button3 = Button(top)
        self.Button3.place(relx=0.02, rely=0.41, height=26, width=157)
        self.Button3.configure(activebackground="#d9d9d9")
        self.Button3.configure(background="#d9d938")
        self.Button3.configure(font=font11)
        self.Button3.configure(text='''Generate''')
        self.Button3.configure(cursor='crosshair')
        self.Button3.configure(command=lambda: but3Press())

        self.Button4 = Button(top)
        self.Button4.place(relx=0.18, rely=0.41, height=26, width=157)
        self.Button4.configure(activebackground="#d9d9d9")
        self.Button4.configure(background="#d9d938")
        self.Button4.configure(font=font10)
        self.Button4.configure(text='''Clear''')
        self.Button4.configure(cursor='crosshair')
        self.Button4.configure(command=lambda: but4Press())

        self.Button5 = Button(top)
        self.Button5.place(relx=0.02, rely=0.50, height=26, width=322)
        self.Button5.configure(activebackground="#d9d9d9")
        self.Button5.configure(background="#d9d938")
        self.Button5.configure(font=font9)
        self.Button5.configure(text='''Create Item List''')
        self.Button5.configure(cursor='crosshair')
        self.Button5.configure(command=lambda: but5Press())

        self.Button5 = Button(top)
        self.Button5.place(relx=0.4, rely=0.12, height=486, width=587)
        self.Button5.configure(activebackground="#d9d9d9")
        self.Button5.configure(state=ACTIVE)
        self.Button5.configure(cursor='exchange')
        self.Button5.configure(command=lambda: but5Press())

    def take(self):
        self.entries = []
        self.entries.append(self.Entry1.get())
        self.entries.append(self.Entry2.get())
        self.entries.append(self.Entry3.get())
        self.entries.append(self.Entry4.get())
        self.entries.append(self.Entry5.get())
        self.entries.append(self.Entry6.get())
        self.entries.append(self.Entry7.get())
        print(self.entries)

def but1Press():
    global materials
    name = tkFileDialog.askopenfilename()
    out = open(name, 'r')
    out = out.read().split()
    #effectively useless, but makes list comprehension easy
    for i in range(0,len(out)):
        try:
            temp = float(out[i])
            out[i] = temp
        except:
            pass
    materials_list = [x for x in out if isinstance(x,str)]
    proportion_list = [x for x in out if isinstance(x,float)]
    price_list = []
    for i in materials_list:
        dialog = float(tkSimpleDialog.askstring('Cost per unit of:', str(i)))
        price_list.append(dialog)
    mat_metadata = list(zip(price_list, proportion_list))
    materials = dict(zip(materials_list, mat_metadata))
    print(materials)
    top.Button1.configure(command=None)
    top.Button1.configure(text='Loaded')
    top.Button1.configure(background='#135bd9')

def but2Press():
    pass

def but3Press():
    #model
    from economic_disease_burden import Forecast
    pl.clf()
    top.take()
    f = Forecast(gui._agents, materials, float(top.entries[0]), float(top.entries[1]), float(top.entries[2]), float(top.entries[3]), .08, float(top.entries[4]), float(top.entries[5]), float(top.entries[6]))
    f.run(len(gui._total))
    pl.plot(f.running)
    pl.savefig('fig3')
    img = Image.open('fig3.png')
    img = img.resize((587,486), PIL.Image.ANTIALIAS)
    img.save('fig3.png')
    image3 = ImageTk.PhotoImage(file='fig3.png')
    pl.clf()
    top.Button5.configure(image=image3)


def but4Press():
    top.Entry1.delete(0,END)
    top.Entry2.delete(0,END)
    top.Entry3.delete(0,END)
    top.Entry4.delete(0,END)
    top.Entry5.delete(0,END)
    top.Entry6.delete(0,END)
    top.Entry7.delete(0,END)

def but5Press():
    dialog = tkSimpleDialog.askstring('SIWR Input', 'Input a file name:')
    dialog += '.siwr_fin'
    count = int(tkSimpleDialog.askstring('Generate Materials File', 'Input the number of unique materials:'))
    out = open(dialog, 'w')
    for i in range(0,count):
        name = tkSimpleDialog.askstring('Generate Materials File', 'Material name:')
        prop = tkSimpleDialog.askstring('Generate Materials File', 'Decimal proportion of ' + str(name) + ' used per clean:')
        out.write(name)
        out.write(' ')
        out.write(prop)
        out.write(' ')

if __name__ == '__main__':
    vp_start_econgui()
