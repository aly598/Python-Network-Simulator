import tkinter
from tkinter import messagebox
import networkx
import math


NODE_RADIUS = 20
DEVICE_COLORS = { "PC": "skyblue", "Router": "salmon", "Switch": "lightgreen"}


# Main Class
class NetworkSimulator:

    def __init__(self, rootWindow):

        # ---------- Main Window ----------
        self.root = rootWindow
        self.root.title("Simple Network Simulator")

        # ---------- Network Data ----------
        self.networkGraph = networkx.Graph()   # نتورك فارغه في
        self.nodePositions = {}                # Stores position of each device
        self.deviceCounter = 1                 # Device naming counter
        self.firstSelectedNode = None          # Used when adding links


        # ================= Sidebar =================
        self.sidebar = tkinter.Frame( self.root, width=200, bg="#ed0d75", padx=10, pady=10  )
        self.sidebar.pack(side=tkinter.LEFT, fill=tkinter.Y)


        # ================= Canvas =================
        self.canvas = tkinter.Canvas( self.root,  bg="white",  cursor="cross")
        self.canvas.pack(  side=tkinter.RIGHT,  fill=tkinter.BOTH,expand=True)


        # ================= Tools =================
        tkinter.Label(self.sidebar, text="Tools", font=("Arial", 14, "bold") ).pack(pady=10)
        self.currentMode = tkinter.StringVar(value="Move")

        tkinter.Radiobutton( self.sidebar, text="Add PC", variable=self.currentMode, value="PC", indicatoron=0, width=15 ).pack(pady=5)

        tkinter.Radiobutton(self.sidebar,text="Add Router",variable=self.currentMode,value="Router", indicatoron=0, width=15 ).pack(pady=5)

        tkinter.Radiobutton( self.sidebar, text="Add Switch", variable=self.currentMode, value="Switch", indicatoron=0, width=15 ).pack(pady=5)

        tkinter.Radiobutton(self.sidebar, text="Add Link", variable=self.currentMode, value="Link", indicatoron=0, width=15).pack(pady=5)

        tkinter.Button( self.sidebar, text="Ping Test",command=self.openPingWindow, bg="orange", width=15 ).pack(pady=10)


        # ================= Event Log =================
        tkinter.Label(self.sidebar,text="Event Log",font=("Arial", 10, "bold")  ).pack(pady=5)

        self.logBox = tkinter.Text(self.sidebar,height=10,width=25,font=("Consolas", 8))
        self.logBox.pack()


        # ================= Mouse Events =================
        self.canvas.bind("<Button-1>", self.handleLeftClick)
        self.canvas.bind("<Button-3>", self.handleRightClick)


    # ================= Logging =================
    def logMessage(self, text):
        self.logBox.insert(tkinter.END, f"> {text}\n")
        self.logBox.see(tkinter.END)


    # ================= Left Click =================
    def handleLeftClick(self, event):

        x, y = event.x, event.y
        mode = self.currentMode.get()

        # ---- Add Device ----
        if mode in ["PC", "Router", "Switch"]:

            deviceName = f"{mode}{self.deviceCounter}"
            self.deviceCounter += 1

            self.networkGraph.add_node(deviceName,type=mode,ip="0.0.0.0" )

            self.nodePositions[deviceName] = (x, y)
            self.renderNetwork()
            self.logMessage(f"{deviceName} created")

        # ---- Add Link ----
        elif mode == "Link":

            clickedNode = self.getNodeAtPosition(x, y)

            if clickedNode:
                if self.firstSelectedNode is None:
                    self.firstSelectedNode = clickedNode
                    self.logMessage(f"{clickedNode} selected")
                else:
                    if clickedNode != self.firstSelectedNode:
                        self.networkGraph.add_edge(
                            self.firstSelectedNode,
                            clickedNode
                        )
                        self.logMessage(
                            f"{self.firstSelectedNode} connected to {clickedNode}"
                        )
                        self.firstSelectedNode = None
                        self.renderNetwork()


    # ================= Detect Clicked Device =================
    def getNodeAtPosition(self, x, y):

        for node, (nxPos, nyPos) in self.nodePositions.items():
            if math.hypot(nxPos - x, nyPos - y) <= NODE_RADIUS:
                return node

        return None


    # ================= Right Click =================
    def handleRightClick(self, event):

        node = self.getNodeAtPosition(event.x, event.y)

        if node:
            menu = tkinter.Menu(self.root, tearoff=0)

            menu.add_command(
                label="Properties",
                command=lambda: self.openProperties(node)
            )

            menu.add_command(
                label="Delete",
                command=lambda: self.deleteNode(node)
            )

            menu.post(event.x_root, event.y_root)


    # ================= Properties Window =================
    def openProperties(self, node):

        window = tkinter.Toplevel(self.root)
        window.title(f"{node} Properties")

        tkinter.Label(window, text="IP Address").pack(pady=5)

        ipEntry = tkinter.Entry(window)
        ipEntry.insert(0, self.networkGraph.nodes[node]["ip"])
        ipEntry.pack()

        def saveIP():
            self.networkGraph.nodes[node]["ip"] = ipEntry.get()
            self.logMessage(f"{node} IP updated")
            window.destroy()

        tkinter.Button(
            window,
            text="Save",
            command=saveIP
        ).pack(pady=10)


    # ================= Delete Device =================
    def deleteNode(self, node):
        self.networkGraph.remove_node(node)
        del self.nodePositions[node]
        self.renderNetwork()
        self.logMessage(f"{node} deleted")


    # ================= Draw Network =================
    def renderNetwork(self):

        self.canvas.delete("all")

        # Draw links
        for u, v in self.networkGraph.edges():
            x1, y1 = self.nodePositions[u]
            x2, y2 = self.nodePositions[v]
            self.canvas.create_line(x1, y1, x2, y2, width=2)

        # Draw devices
        for node, (x, y) in self.nodePositions.items():
            deviceType = self.networkGraph.nodes[node]["type"]
            color = DEVICE_COLORS.get(deviceType, "gray")

            self.canvas.create_oval(
                x - NODE_RADIUS, y - NODE_RADIUS,
                x + NODE_RADIUS, y + NODE_RADIUS,
                fill=color,
                outline="black",
                width=2
            )

            self.canvas.create_text(x, y + 30, text=node)


    # ================= Ping Window =================
    def openPingWindow(self):

        window = tkinter.Toplevel(self.root)
        window.title("Ping Test")

        tkinter.Label(window, text="Source").grid(row=0, column=0)
        src = tkinter.Entry(window)
        src.grid(row=0, column=1)

        tkinter.Label(window, text="Destination").grid(row=1, column=0)
        dst = tkinter.Entry(window)
        dst.grid(row=1, column=1)

        def ping():
            try:
                path = networkx.shortest_path(
                    self.networkGraph,
                    src.get(),
                    dst.get()
                )
                messagebox.showinfo(
                    "Ping Success",
                    f"Path: {path}"
                )
            except:
                messagebox.showerror(
                    "Ping Failed",
                    "Destination Unreachable"
                )

        tkinter.Button(
            window,
            text="Ping",
            command=ping
        ).grid(row=2, column=0, columnspan=2, pady=10)


# ================= Program Start =================
if __name__ == "__main__":
    root = tkinter.Tk()
    root.geometry("900x600")
    NetworkSimulator(root)
    root.mainloop()