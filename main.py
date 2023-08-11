import socket
import select
import threading
import time
from tkinter import *
from tkinter import ttk
from datetime import datetime
# from datadownload import DataDownload

IP_LOCAL = "0.0.0.0"
IP_OFIL  = "192.168.0.100"

SEND_PORT = 4526    
RECV_PORT = 4527

recv_addr = (IP_LOCAL, RECV_PORT)
send_addr = (IP_OFIL, SEND_PORT)

send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
send_socket.setblocking(False)

recv_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
recv_socket.setblocking(False)
recv_socket.bind(recv_addr)

send_poller = select.poll()
send_poller.register(send_socket, select.POLLOUT)

recv_poller = select.poll()
recv_poller.register(recv_socket, select.POLLIN)

msg_tx = ""
msg_rx = ""
msg_tx_update = ""
msg_rx_update = ""
last_heartbeat_hera_recv = time.time()
buffer_time_record = ""
connected = 0
byte_recv = b''
DisplayArr = ["Visible Only", "UV Only", "Combined"]
UVColorArr = ["red", "orange", "yellow", "green", "light blue", "blue", "purple", "pink",
        "transparent red", "transparent orange", "transparent yellow", "transparent green", "transparent light blue", "transparent blue", "transparent purple", "transparent pink"]
List_Command_Querry = ["GA", "MZ", "AE", "DMODE", "MF", "AF", "CNW", "UVC"]
List_Respond_Data = [0,0,0,0,0,0,0,0]
List_Suffixes = ["S", "Q", "R"]
callbackArr = [0,0,0,0] #[zoom, focus, gain, exposure]
timeCallbackArr = [0,0,0,0] #[zoom, focus, gain, exposure]
callback_flag = 0
dump_flag = 0

# data = 

def check_respond_data(buffer1, buffer2):
    if len(buffer1) < 1:
        return 0
    for i in range(len(buffer2)):
        if buffer1[i] !=  buffer2[i]:
            return 0
    return 1
        
def handle_respond_data(buffer):
    if len(buffer) > 1:
        array = buffer.split('R')
        array2 = array[0].split('CI_')
        return (array[1],array2[1])
    else:
        return (buffer, buffer)
            
def network_write(fd_socket, poll, msg):
    events = poll.poll(1000) ## need to fix
    for fd, event in events:
        if fd == fd_socket.fileno() and event == select.POLLOUT:
            try:
                fd_socket.sendto(msg.encode('utf-8'), send_addr)
            except socket.error:
                pass

def network_read(fd_socket, poll):
    events = poll.poll(2000)
    global byte_recv
    for fd, event in events:
        if fd == fd_socket.fileno() and event == select.POLLIN:
            try:
                byte_recv, addr = fd_socket.recvfrom(1024)
                return byte_recv
            except socket.error:
                pass
    return b''

def callback_takephoto():
    global connected
    if connected == 1:
        now = datetime.now()
        dt_string = "IC_PLSTS" + now.strftime("%d-%m-%Y-%H-%M-%S")
        print(dt_string)
        network_write(send_socket, send_poller, dt_string)

def callback_recordvideo():
    global buffer_time_record, connected
    if connected == 1:
        if (CaptureBT['text'] == 'Record'):
            now = datetime.now()
            buffer_time_record = now.strftime("%d-%m-%Y-%H-%M-%S")
            dt_string = "IC_VLSTS" + buffer_time_record
            network_write(send_socket, send_poller, dt_string)
            CaptureBT['text'] = 'Stop Record'
        else:
            dt_string = "IC_VLSPS" + buffer_time_record
            network_write(send_socket, send_poller, dt_string)
            CaptureBT['text'] = 'Record'

def callback_UVcolor(event):
    global connected
    if connected == 1:
        for i in range(len(UVColorArr)):
            if UVcolorcombo.get() == UVColorArr[i]:
                dt_string = "IC_UVCS" + str(i)
                print(dt_string)
                network_write(send_socket, send_poller, dt_string)
                
def callback_ZoomSlider(event):
    global connected
    if connected == 1:
        callbackArr[0] = 1
        timeCallbackArr[0] = time.time()
        # dt_string = "IC_MZS" + str(int(ZoomCurrentValue.get()))
        # print(dt_string)
        # network_write(send_socket, send_poller, dt_string)
        
def callback_FocusSlider(event):
    global connected
    if connected == 1:
        timeCallbackArr[1] = time.time()
        callbackArr[1] = 1
        # dt_string = "IC_MFS" + str(int(FocusCurrentValue.get()))
        # print(dt_string)
        # network_write(send_socket, send_poller, dt_string)
        
def callback_GainSlider(event):
    global connected
    if connected == 1:
        timeCallbackArr[2] = time.time()
        callbackArr[2] = 1
        # dt_string = "IC_GAS" + str(GainCurrentValue.get())
        # print(dt_string)
        # network_write(send_socket, send_poller, dt_string)
    
def callback_Exposure(event):
    global connected
    if connected == 1:
        timeCallbackArr[3] = time.time()
        callbackArr[3] = 1
        # dt_string = "IC_AES" + str(int(ExposureCurrentValue.get()))
        # print(dt_string)
        # network_write(send_socket, send_poller, dt_string)
        
def callback_Display(event):
    global connected
    if connected == 1:
        for i in range(len(DisplayArr)):
            if Displaycombo.get() == DisplayArr[i]:
                dt_string = "IC_DMODES" + str(i+1)
                print(dt_string)
                network_write(send_socket, send_poller, dt_string)

def callback_Focus():
    global connected
    if connected == 1:
        if Focus.get() == 1:
            FocusSlider['state'] = DISABLED
        else:
            FocusSlider['state'] = NORMAL

        dt_string = "IC_AFS" + str(int(Focus.get()))
        network_write(send_socket, send_poller, dt_string)

# GUI
root = Tk()
root.title("OFIL CONTROLLER")
root.geometry("380x510")
root.resizable(False, False)
# style = Style(root)
# style.configure(".",font=("Arial",20))  # change size of text tab
tabControl = ttk.Notebook(root)
advancedTab = Frame(tabControl)
mainTab = Frame(tabControl)
tabControl.add(mainTab, text ='Main')
tabControl.add(advancedTab, text ='Advance')
tabControl.pack()

# Status Label
State = Label(root, text="Disconnected", width=380, height=10, bg='red')
State.pack()
       
def thread_check_connection():
    """
    Check connection between GCS and OFIL
    """
    def check_connection():
        global last_heartbeat_hera_recv, connected
        while True:
            try:
                if (time.time() - last_heartbeat_hera_recv) > 5:
                    connected = 0
                if connected == 0:
                    State.config(text="Disconnected", bg="red")
                else:
                    State.config(text="Connected", bg="green")
                    # network_write(send_socket, send_poller, "IC_QMMFQ")   
            except:
                pass
            time.sleep(0.5)
    _thread_check_connection = threading.Thread(target=check_connection, daemon=True)
    _thread_check_connection.start()
    
def thread_heartbeat():
    """
    Init connection with the camera OFIL
    """ 
    def init_communication():
        global last_heartbeat_hera_recv, connected, msg_rx
        while True:
            # print(connected)
            if dump_flag == 0:
                if connected == 0:
                    network_write(send_socket, send_poller, "IC_ALVS")
                msg_rx = network_read(recv_socket, recv_poller).decode('utf-8').strip()
                print(msg_rx)
                if msg_rx == "CI_ALVQ" or check_respond_data(msg_rx, "CI_") == 1:
                    connected = 1
                    network_write(send_socket, send_poller, "IC_ALVR")
                    last_heartbeat_hera_recv = time.time()
                    # print(last_heartbeat_hera_recv)
                
            time.sleep(1)
    _thread_heartbeat = threading.Thread(target=init_communication, daemon=True)
    _thread_heartbeat.start()
    
def thread_querry_data():
    """
    Querry data from OFIL to update GUI
    """
    def update_data():
        global msg_tx_update, msg_rx_update, byte, dump_flag
        only_update_once = 0
        while True:
            time.sleep(2)
            if connected == 1:
                dump_flag = 1
                for i in range(len(List_Command_Querry)):
                    msg_tx_update = "IC_" + List_Command_Querry[i] + "Q"
                    msg_rx_fuck = "CI_" + List_Command_Querry[i] + "R"
                    print(msg_tx_update)
                    network_write(send_socket, send_poller, msg_tx_update)
                    msg_rx_update = network_read(recv_socket, recv_poller).decode('utf-8').strip()
                    while (check_respond_data(msg_rx_update, msg_rx_fuck) != 1):
                        msg_rx_update = network_read(recv_socket, recv_poller).decode('utf-8').strip()
                        network_write(send_socket, send_poller, "IC_ALVR")
                    print(msg_rx_update)
                    data, command = handle_respond_data(msg_rx_update)
                    if List_Command_Querry[i] == command:
                        List_Respond_Data[i] = int(data)
                # Update Data for GUI
                print(List_Respond_Data)
                GainCurrentValue.set(List_Respond_Data[0])
                ZoomCurrentValue.set(List_Respond_Data[1])
                ExposureCurrentValue.set(List_Respond_Data[2])
                Displaycombo.current(List_Respond_Data[3]-1)
                FocusCurrentValue.set(List_Respond_Data[4])
                Focus.set(List_Respond_Data[5])
                if (List_Respond_Data[5] == 1):
                    FocusSlider['state'] = DISABLED
                else:
                    FocusSlider['state'] = NORMAL
                UVcolorcombo.current(List_Respond_Data[7])
                now = datetime.now()
                buffer_set_time ="IC_DATS" + now.strftime("%Y %m %d %H %M %S")
                network_write(send_socket, send_poller, buffer_set_time)
                only_update_once = 1
                dump_flag = 0
            if only_update_once == 1:
                print("thread_querry_data exit")
                return
    _thread_querry_data = threading.Thread(target=update_data, daemon=True)
    _thread_querry_data.start()
    
def thread_callback_senddata():
    def callback():
        while True:
            if connected == 1:
                for i in range(len(callbackArr)):
                    if callbackArr[i] == 1:
                        if i == 0:
                            if (time.time() - timeCallbackArr[0]) > 0.5:
                                dt_string = "IC_MZS" + str(int(ZoomCurrentValue.get()))
                                print(dt_string)
                                network_write(send_socket, send_poller, dt_string)
                        elif i ==  1:
                            if (time.time() - timeCallbackArr[1]) > 0.5:
                                dt_string = "IC_MFS" + str(int(FocusCurrentValue.get()))
                                print(dt_string)
                                network_write(send_socket, send_poller, dt_string)
                        elif i == 2:
                            if (time.time() - timeCallbackArr[2]) > 0.5:
                                dt_string = "IC_GAS" + str(int(GainCurrentValue.get()))
                                print(dt_string)
                                network_write(send_socket, send_poller, dt_string)
                        elif i == 3:
                            if (time.time() - timeCallbackArr[3]) > 0.5:
                                dt_string = "IC_AES" + str(int(ExposureCurrentValue.get()))
                                print(dt_string)
                                network_write(send_socket, send_poller, dt_string)
                        callbackArr[i] = 0
            time.sleep(2)
    _thread_callback_senddata = threading.Thread(target=callback, daemon=True)
    _thread_callback_senddata.start()
                                    
# Start thread                     
thread_check_connection()
thread_heartbeat()
thread_querry_data()
thread_callback_senddata()


# Take Picture
PictureBT = Button(mainTab, text="Take Picture", state= NORMAL, command=callback_takephoto, height=6, width=20, bg="#F6AC0D", activebackground="orange")
PictureBT.grid(row=3, column=0, pady=20) 

# Capture Video
CaptureBT = Button(mainTab, text="Record",state= NORMAL, command=callback_recordvideo, height=6, width=20, bg="#F6AC0D", activebackground="orange")
CaptureBT.grid(row=3, column=1, pady=20)

# Zoom
ZoomLabel = LabelFrame(mainTab,text="Zoom Camera")
ZoomLabel.grid(row=4, column=0, columnspan=2)
ZoomCurrentValue = DoubleVar()
ZoomSlider = Scale(ZoomLabel, from_= 0, to= 40,length= 350, orient='horizontal', variable=ZoomCurrentValue, command=callback_ZoomSlider)
ZoomSlider.grid(row=0, column=0,columnspan=2,pady=10)

# Focus Manual or Auto
Focus = IntVar()
# Focus.set(1)
FocusLabel = LabelFrame(mainTab,text="Auto Focus")
FocusLabel.grid(row=6, column=0, columnspan=2)
F1 = Radiobutton(FocusLabel, text="Auto Focus", variable= Focus, value=1, command=callback_Focus)
F1.grid(row=0, column=0, columnspan=1, sticky="w")
F2 = Radiobutton(FocusLabel, text="Manual Focus", variable= Focus, value=0, command=callback_Focus)
F2.grid(row=1, column=0, columnspan=1, sticky="w")

FocusCurrentValue = DoubleVar()
FocusSlider = Scale(FocusLabel, from_= 0, to= 75,length= 350,state=DISABLED, orient='horizontal', variable=FocusCurrentValue, command=callback_FocusSlider)
FocusSlider.grid(row=2, column=0,columnspan=2)

# Gain
GainLabel = LabelFrame(advancedTab,text="Gain")
GainLabel.grid(row=0, column=0, columnspan=2)
GainCurrentValue = DoubleVar()
GainSlider = Scale(GainLabel, from_= 0, to= 250,length= 370, orient='horizontal', variable=GainCurrentValue, command=callback_GainSlider)
GainSlider.grid(row=0, column=0,columnspan=2)

# Change UV Color
UVcolorLabel = LabelFrame(advancedTab,text="UV Color")
UVcolorLabel.grid(row=2, column=0, columnspan=1, pady= 10)
UVcolorcombo = ttk.Combobox(UVcolorLabel, state= "readonly", values=UVColorArr)
UVcolorcombo.bind('<<ComboboxSelected>>', callback_UVcolor)
# UVcolorcombo.current(1)
UVcolorcombo.grid(row=0, column=0, columnspan=1 , pady= 10)

# Display Mode
DisplayLabel = LabelFrame(advancedTab,text="Display Mode")
DisplayLabel.grid(row=2, column=1, columnspan=2,  padx= 15)
Displaycombo = ttk.Combobox(DisplayLabel, state= "readonly", values=DisplayArr)
Displaycombo.bind('<<ComboboxSelected>>', callback_Display)
# Displaycombo.current(0)
Displaycombo.grid(row=0, column=0, columnspan=2,pady= 10)

# Auto Exposure
ExposureLabel = LabelFrame(advancedTab, text="Exposure")
ExposureLabel.grid(row=7, column=0, columnspan=2)
ExposureCurrentValue = DoubleVar()
ExposureSlider = Scale(ExposureLabel, from_= 0, to= 22,length= 370, orient='horizontal', variable=ExposureCurrentValue, command=callback_Exposure)
ExposureSlider.grid(row=0, column=0,columnspan=2)
Label(ExposureLabel, text="0: Auto Exposure").grid(row=1, column=0, sticky='w')
Label(ExposureLabel, text="1: 1/1").grid(row=2, column=0, sticky='w')
Label(ExposureLabel, text="2: 1/2").grid(row=3, column=0, sticky='w')
Label(ExposureLabel, text="3: 1/3").grid(row=4, column=0, sticky='w')
Label(ExposureLabel, text="4: 1/6").grid(row=5, column=0, sticky='w')
Label(ExposureLabel, text="5: 1/12").grid(row=6, column=0, sticky='w')
Label(ExposureLabel, text="6: 1/25").grid(row=7, column=0, sticky='w')
Label(ExposureLabel, text="7: 1/50").grid(row=8, column=0, sticky='w')
Label(ExposureLabel, text="8: 1/75").grid(row=9, column=0, sticky='w')
Label(ExposureLabel, text="9: 1/100").grid(row=10, column=0, sticky='w')
Label(ExposureLabel, text="10: 1/120").grid(row=11, column=0, sticky='w')
Label(ExposureLabel, text="11: 1/150").grid(row=1, column=1, sticky='w')
Label(ExposureLabel, text="12: 1/215").grid(row=2, column=1, sticky='w')
Label(ExposureLabel, text="13: 1/300").grid(row=3, column=1, sticky='w')
Label(ExposureLabel, text="14: 1/425").grid(row=4, column=1, sticky='w')
Label(ExposureLabel, text="15: 1/600").grid(row=5, column=1, sticky='w')
Label(ExposureLabel, text="16: 1/1000").grid(row=6, column=1, sticky='w')
Label(ExposureLabel, text="17: 1/1250").grid(row=7, column=1, sticky='w')
Label(ExposureLabel, text="18: 1/1750").grid(row=8, column=1, sticky='w')
Label(ExposureLabel, text="19: 1/2500").grid(row=9, column=1, sticky='w')
Label(ExposureLabel, text="20: 1/3500").grid(row=10, column=1, sticky='w')
Label(ExposureLabel, text="21: 1/6000").grid(row=11, column=1, sticky='w')
Label(ExposureLabel, text="22: 1/10000").grid(row=12, column=1, sticky='w')

root.mainloop() 