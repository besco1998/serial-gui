from tkinter import *
from tkinter import ttk
import serial
import serial.tools.list_ports
import datetime
import threading
import multiprocessing
import os
import struct
import gps_time
import numpy as np

#for printing debugging messages in console
dbg = 1

gRoot = Tk()
#gRoot.geometry("480x280")
gRoot.title("Serial Console")
sty = ttk.Style()
sty.theme_use("alt")
gRoot.columnconfigure(0,weight=1)
gRoot.rowconfigure(0,weight=1)
#sty.configure("gframe.TFrame",background="white")
gFrame = ttk.LabelFrame(gRoot,text="Connection Setting",padding=10)
gFrame.grid(column=1,row=1, sticky=(W,E))

gFrame2 = ttk.LabelFrame(gRoot,text="Representation",padding=10)
gFrame2.grid(column=1,row=2, sticky=(W,E))
#Frame for COM messages

gFrame21 = ttk.Frame(gRoot,padding=10)
gFrame21.grid(column=2,row=1, sticky=(W))
#gRoot.resizable(0,0)

for x in range(10):
    gFrame.columnconfigure(x,weight = x)
    gFrame.rowconfigure(x,weight = x)
    gFrame2.columnconfigure(x,weight = x)
    gFrame2.rowconfigure(x,weight = x)
    
label1=ttk.Label(gFrame, text = "Serial Console")
label1.grid(column=2,row=0)

Xlabel=ttk.Label(gFrame2, text = "X:")
Xlabel.grid(column=1,row=0)
Ylabel=ttk.Label(gFrame2, text = "Y:")
Ylabel.grid(column=1,row=1)
Zlabel=ttk.Label(gFrame2, text = "Z:")
Zlabel.grid(column=1,row=2)

Xtext = Text(gFrame2,height=1,width=20)
Xtext.grid(column=2,row=0)
Ytext = Text(gFrame2,height=1,width=20)
Ytext.grid(column=2,row=1)
Ztext = Text(gFrame2,height=1,width=20)
Ztext.grid(column=2,row=2)

Latlabel=ttk.Label(gFrame2, text = "Lat:")
Latlabel.grid(column=3,row=0)
Lonlabel=ttk.Label(gFrame2, text = "Lon:")
Lonlabel.grid(column=3,row=1)
Altlabel=ttk.Label(gFrame2, text = "Alt:")
Altlabel.grid(column=3,row=2)

Lattext = Text(gFrame2,height=1,width=20)
Lattext.grid(column=4,row=0)
Lontext = Text(gFrame2,height=1,width=20)
Lontext.grid(column=4,row=1)
Alttext = Text(gFrame2,height=1,width=20)
Alttext.grid(column=4,row=2)

Vxlabel=ttk.Label(gFrame2, text = "Vx:")
Vxlabel.grid(column=1,row=4)
Vylabel=ttk.Label(gFrame2, text = "Vy:")
Vylabel.grid(column=1,row=5)
Vzlabel=ttk.Label(gFrame2, text = "Vz:")
Vzlabel.grid(column=1,row=6)

Vxtext = Text(gFrame2,height=1,width=20)
Vxtext.grid(column=2,row=4)
Vytext = Text(gFrame2,height=1,width=20)
Vytext.grid(column=2,row=5)
Vztext = Text(gFrame2,height=1,width=20)
Vztext.grid(column=2,row=6)

Timelabel=ttk.Label(gFrame2, text = "Time:")
Timelabel.grid(column=3,row=5)
Doplabel=ttk.Label(gFrame2, text = "DOP:")
Doplabel.grid(column=3,row=6)

Timetext = Text(gFrame2,height=1,width=20)
Timetext.grid(column=4,row=5)
Doptext = Text(gFrame2,height=1,width=20)
Doptext.grid(column=4,row=6)



gFrame.rowconfigure(0,weight=2)
gFrame2.rowconfigure(0,weight=2)


sty.configure("label2.TLabel",borderwidth=4,relief="ridge",foreground="red",ipadx=10)
label2=ttk.Label(gFrame,sty="label2.TLabel", text = "Select Com Port")
label2.grid(column=1,row=1, sticky = (N,E,W,S))

"""
Com Port List
"""
#Start
ports = serial.tools.list_ports.comports()
com_port_list = [com[0] for com in ports]
com_port_list.insert(0,"Select an Option")
if dbg == 1:
    print(com_port_list)
#END
com_value_inside = StringVar()
baud_value_inside = StringVar()
baud_menu = ttk.OptionMenu(gFrame,baud_value_inside,"select baud rate","9600",
                           '19200','28800','38400','57600','76800',
                           '115200','128000','153600','230400','256000','460800','921600')
baud_menu.grid(column=3, row=1, sticky = (E))
def com_port_list_update():
    global ports
    global com_port_list
    ports = serial.tools.list_ports.comports()
    com_port_list = [com[0] for com in ports]
    com_port_list.insert(0,"Select an Option")
    if dbg == 1:
        print(com_port_list)
    com_menu = ttk.OptionMenu(gFrame,com_value_inside,*com_port_list)
    com_menu.grid(column=2, row=1, sticky = (E))
    #Frame for the COM LIST
    gRoot_com_list = Toplevel(gRoot)
    x = gRoot.winfo_x()
    y = gRoot.winfo_y()
    gRoot_com_list.geometry("+%d+%d" %(x+200,y+200))
    gFrame01 = ttk.Frame(gRoot_com_list,padding=10)
    gFrame01.grid(column=0,row=1, sticky=(W))
    #Create a horizontal scrollbar
    scrollbar = ttk.Scrollbar(gFrame01, orient= 'horizontal')
    scrollbar.grid(column=1,row=2, sticky=W+E)

    Lb1 = Listbox(gFrame01, xscrollcommand = 1, width = 50, font= ('Helvetica 8 bold'))
    counter = 0
    for x in ports:
        Lb1.insert(counter, str(x))
    #print (counter)
    counter += 1
    Lb1.grid(column=1,row=1, sticky=W+E)
    Lb1.config(xscrollcommand= scrollbar.set)

    #Configure the scrollbar
    scrollbar.config(command= Lb1.xview)

def ecef2lla_hugues(x, y, z):
	# x, y and z are scalars in meters (CANNOT use vectors for this method)
	# Following "An analytical method to transform geocentric into geodetic coordinates"
	# By Hugues Vermeille (2011)

	x = np.array([x]).reshape(np.array([x]).shape[-1], 1)
	y = np.array([y]).reshape(np.array([y]).shape[-1], 1)
	z = np.array([z]).reshape(np.array([z]).shape[-1], 1)

	a=6378137
	a_sq=a**2
	e = 8.181919084261345e-2
	e_sq = 6.69437999014e-3

	p = (x**2 + y**2)/a_sq
	q = ((1 - e_sq)*(z**2))/a_sq
	r = (p + q - e_sq**2)/6.

	evolute = 8*r**3 + p*q*(e_sq**2)

	if(evolute > 0):
		u = r + 0.5*(np.sqrt(8*r**3 + p*q*e_sq**2) + np.sqrt(p*q*e_sq**2))**(2/3.) + \
				0.5*(np.sqrt(8*r**3 + p*q*e_sq**2) - np.sqrt(p*q*e_sq**2))**(2/3.)
	else:
		u_term1 = np.sqrt(p*q*e_sq**2)/(np.sqrt(-8*r**3 - p*q*e_sq**2) + np.sqrt(-8*r**3))
		u_term2 = (-4.*r)*np.sin((2./3.)*np.arctan(u_term1))
		u_term3 = np.cos(np.pi/6. + (2./3.)*np.arctan(u_term1))
		u       = u_term2*u_term3

	v = np.sqrt(u**2 + q*e_sq**2)
	w = e_sq*(u + v - q)/(2.*v)
	k = (u + v)/(np.sqrt(w**2 + u + v) + w)
	d = k*np.sqrt(x**2 + y**2)/(k + e_sq)
	h = np.sqrt(d**2 + z**2)*(k + e_sq - 1)/k
	phi = 2.*np.arctan(z/((np.sqrt(d**2 + z**2) + d)))

	if((q == 0) and (p <= e_sq**2)):
		h = -(a*np.sqrt(1 - e_sq)*np.sqrt(e_sq - p))/(e)
		phi1 = 2*np.arctan(np.sqrt(e_sq**2 - p)/(e*(np.sqrt(e_sq - p)) + np.sqrt(1 - e_sq)*np.sqrt(p)))
		phi2 = -phi1
		phi = (phi1, phi2)


	case1 = (np.sqrt(2) - 1)*np.sqrt(y**2) < np.sqrt(x**2 + y**2) + x
	case2 = np.sqrt(x**2 + y**2) + y < (np.sqrt(2) + 1)*np.sqrt(x**2)
	case3 = np.sqrt(x**2 + y**2) - y < (np.sqrt(2) + 1)*np.sqrt(x**2)

	if(case1):
		print("case1")
		lambd = 2.*np.arctan(y/(np.sqrt(x**2 + y**2) + x))
		return phi*180/np.pi, lambd*180/np.pi, h
	if(case2):
		print("case2")
		lambd = (-np.pi/2) - 2.*np.arctan(x/(np.sqrt(x**2 + y**2) - y))
		return phi*180/np.pi, lambd*180/np.pi, h
	if(case3):
		print("case3")
		lambd = (np.pi/2) - 2.*np.arctan(x/(np.sqrt(x**2 + y**2) + y))
		return phi*180/np.pi, lambd*180/np.pi, h


def serial_print():
    global serFlag
    global ser
    global counter1
    x =""
    #print("Task 1 assigned to thread: {}".format(threading.current_thread().name))
    #print("ID of process running task 1: {}".format(os.getpid()))
    if(serFlag):
        if(ser.in_waiting>0):
            #
            try:
                #x = ser.read(ser.in_waiting)
                #x = ser.readline(ser.in_waiting)
                #x = ser.read_until(expected='\n', size=ser.in_waiting)
                #print(x)
                #y = str(counter1)+": "+str(datetime.datetime.now())+" -> "+str(ser.read().hex())
                txt="new packet:"
                payload=""
                y =ser.read(1).hex()
                #counter+=1
                if y== "4c":
                    y =ser.read(1).hex()
                    #counter+=1
                    if y== "4d":
                        y =ser.read(1).hex()
                        #counter+=1
                        if y== "48":
                            y =ser.read(1).hex()
                            #counter+=1
                            if y== "48":
                                y =ser.read(1).hex()
                                #counter+=1
                                if y=="42":
                                    y =ser.read(1).hex()
                                    #counter+=1
                                    if y=="47":
                                        print("new packet")
                                        #y =ser.read().hex()
                                        versionMarker=ser.read(2).hex()
                                        #counter+=2
                                        type=ser.read(1).hex()
                                        #counter+=1
                                        if type=="f2":
                                            PositionPayload=ser.read(37)
                                            #counter+=37
                                            if PositionPayload[0]==1:
                                                payload="valid: "
                                            else:
                                                payload="Not vaild: "

                                            x=struct.unpack("f",PositionPayload[1:5])
                                            y=struct.unpack("f",PositionPayload[5:9])
                                            z=struct.unpack("f",PositionPayload[9:13])
                                            vx=struct.unpack("f",PositionPayload[13:17])
                                            vy=struct.unpack("f",PositionPayload[17:21])
                                            vz=struct.unpack("f",PositionPayload[21:25])
                                            time=struct.unpack("d",PositionPayload[25:33])
                                            dop=struct.unpack("f",PositionPayload[33:37])
                                            print(str(time))
                                            print( gps_time.GPSTime( 0,time_of_week=float(str(time[0]))).to_datetime())
                                            lat,lon,alt=ecef2lla_hugues(x, y, z)
                                            Lattext.delete(1.0,END)
                                            Lontext.delete(1.0,END)
                                            Alttext.delete(1.0,END)
                                            Xtext.delete(1.0,END)
                                            Ytext.delete(1.0,END)
                                            Ztext.delete(1.0,END)
                                            Vxtext.delete(1.0,END)
                                            Vytext.delete(1.0,END)
                                            Vztext.delete(1.0,END)
                                            Timetext.delete(1.0,END)
                                            Doptext.delete(1.0,END)
                                            Lattext.insert(END,str(lat[0]))
                                            Lontext.insert(END,str(lon[0]))
                                            Alttext.insert(END,str(alt[0]))
                                            Xtext.insert(END,str(x[0]))
                                            Ytext.insert(END,str(y[0]))
                                            Ztext.insert(END,str(z[0]))                                            
                                            Vxtext.insert(END,str(vx[0]))
                                            Vytext.insert(END,str(vy[0]))
                                            Vztext.insert(END,str(vz[0]))                                             
                                            Doptext.insert(END,str(dop[0]))
                                            Timetext.insert(END,str(gps_time.GPSTime( 0,time_of_week=float(str(time[0]))).to_datetime()))                                            
                                            payload=payload+"\nECEF[X:"+str(x[0])+" ,Y:"+str(y[0])+" ,Z:"+str(z[0])+"]"+ "\nLLA[Lat:"+str(lat[0])+" ,Lon:"+str(lon[0])+" ,Alt:"+str(alt[0])+"]" +" ,vx:"+str(vx[0])+" ,vy:"+str(vy[0])+" ,vz:"+str(vz[0])+" ,t:"+str(gps_time.GPSTime( 0,time_of_week=float(str(time[0]))).to_datetime())+" ,DOP:"+str(dop[0])
                                        elif type=="f4":
                                            statePayload=ser.read(64).hex()
                                            #counter+=64
                                            snr=statePayload[0:63]
                                            payload1=""
                                            print(snr)
                                            for x in range(0,31):
                                                payload1=payload1+"Sat #"+str(x+1)+"  SNR: "+str(snr[x*2])+str(snr[(x*2)+1])+"\n"
                                            #payload=str(snr)
                                            print (payload1)
                                        print (payload)
                                        Lb2.insert(counter1+1, str(payload))
                Lb2.see("end")
                #print (counter1)
                counter1 += 1
                #gFrame.after(100,serial_print)
            except:
                pass
        ser.flush()
        gFrame.after(100,serial_print)


ser = serial.Serial()
serFlag = 0
def serial_connect(com_port,baud_rate):
    global ser
    ser.baudrate = baud_rate
    ser.port = com_port
    ser.timeout = 1
    ser._xonxoff=1
    ser.bytesize=serial.EIGHTBITS
    ser.parity=serial.PARITY_NONE
    ser.stopbits=serial.STOPBITS_ONE
    ser.open()
    global serFlag
    serFlag = 1
    
    t1 = threading.Thread(target = serial_print, args = (), daemon=1)
    t1.start()
    #t1.join()
    """
    P1 = multiprocessing.Process(target = serial_print, args=())
    P1.start()
    P1.join()
    """
    #serial_print()
counter1 = 0;


    
def serial_close():
    global ser
    global serFlag
    serFlag = 0
    ser.close()
    
def submit_value():
    if dbg == 1:
        print("selected option: {}".format(com_value_inside.get()))
        print(" Baud Rate {}".format(baud_value_inside.get()))
    serial_connect(com_value_inside.get(),baud_value_inside.get())


Lb2 = Listbox(gFrame21, width = 100, xscrollcommand = 1)
Lb2.grid(column=1, row = 1, sticky = W+E)
Sb2 = ttk.Scrollbar(gFrame21,orient = 'vertical')
Sb2.config(command=Lb2.yview)
Sb2.grid(column = 2,row =1, sticky=N+S)
Sb2v = ttk.Scrollbar(gFrame21,orient = 'horizontal')
Sb2v.grid(column = 1,row =2, sticky=W+E)
Sb2v.config(command = Lb2.xview)
Lb2.configure(xscrollcommand = Sb2v.set, yscrollcommand = Sb2.set)

def clear_listbox():
    Lb2.delete(0,END)
    
subBtn = ttk.Button(gFrame,text="submit",command = submit_value)
subBtn.grid(column=4,row=1, sticky = (E))

RefreshBtn = ttk.Button(gFrame,text="Get List",command = com_port_list_update)
RefreshBtn.grid(column=2,row=2, sticky = (E))



closeBtn = ttk.Button(gFrame,text="Disconnect",command = serial_close)
closeBtn.grid(column=4,row=2, sticky = (E))

clearBtn = ttk.Button(gFrame,text="Clear Messages",command = clear_listbox)
clearBtn.grid(column=3,row=2, sticky = (E))



"""
#Add a Listbox Widget
listbox = Listbox(win, width= 350, font= ('Helvetica 15 bold'))
listbox.pack(side= LEFT, fill= BOTH)

#Add values to the Listbox
for values in range(1,101):
   listbox.insert(END, values)
"""
def donothing():
   filewin = Toplevel(gRoot)
   button = Button(filewin, text="Do nothing button")
   button.pack()

def About_me():
   filewin = Toplevel(gRoot)
   Label1 = Label(filewin, text = "EXASUB.COM").pack()
   button = Button(filewin, text="Quit", command = filewin.destroy)
   button.pack()

menubar = Menu(gRoot)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="New", command=donothing)
filemenu.add_command(label="Open", command=donothing)
filemenu.add_command(label="Save", command=donothing)
filemenu.add_command(label="Save as...", command=donothing)
filemenu.add_command(label="Close", command=donothing)

filemenu.add_separator()

filemenu.add_command(label="Exit", command=gRoot.quit)
menubar.add_cascade(label="File", menu=filemenu)
editmenu = Menu(menubar, tearoff=0)
editmenu.add_command(label="Undo", command=donothing)

editmenu.add_separator()

editmenu.add_command(label="Cut", command=donothing)
editmenu.add_command(label="Copy", command=donothing)
editmenu.add_command(label="Paste", command=donothing)
editmenu.add_command(label="Delete", command=donothing)
editmenu.add_command(label="Select All", command=donothing)

menubar.add_cascade(label="Edit", menu=editmenu)
helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="Help Index", command=donothing)
helpmenu.add_command(label="About...", command=donothing)
menubar.add_cascade(label="Help", menu=helpmenu)
menubar.add_command(label = "EXASUB.com", command = About_me)
menubar.add_separator()
menubar.add_command(label = "Quit", command = gRoot.destroy)

gRoot.config(menu=menubar)
gRoot.mainloop()