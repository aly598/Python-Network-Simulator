import tkinter as tk
from tkinter import simpledialog, messagebox
import networkx as nx
import math

NODE_RADIUS = 20
COLORS = {
    "PC": "skyblue",
    "Router": "salmon",
    "Switch": "lightgreen"
}

class NetworkSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Network Simulator (Python)")

        self.G = nx.Graph()
        self.nodes_pos = {}
        self.node_counter = 1
        self.selected_node = None

        self.sidebar = tk.Frame(root, height=30, bg="#639cf2", padx=5, pady=10)
        self.sidebar.pack(side=tk.TOP, fill=tk.X)

        self.canvas = tk.Canvas(root, bg="white", cursor="cross")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(self.sidebar, text="Tools", font=("Arial", 14, "bold")).pack(pady=10)

        self.mode = tk.StringVar(value="Move")

        tk.Radiobutton(self.sidebar, text="Add PC", variable=self.mode, value="PC",indicatoron=0, width=15).pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        tk.Radiobutton(self.sidebar, text="Add Router", variable=self.mode, value="Router",indicatoron=0, width=15).pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        tk.Radiobutton(self.sidebar, text="Add Switch", variable=self.mode, value="Switch",indicatoron=0, width=15).pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        tk.Radiobutton(self.sidebar, text="Link Devices", variable=self.mode, value="Link",indicatoron=0, width=15).pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)

        
        tk.Button(self.sidebar, text="Ping Test", command=self.ping_window, bg="yellow", width=15) .pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)


        tk.Label(self.sidebar, text="Event Log:", font=("Arial", 10, "bold")).pack(pady=(20, 5))
        self.log_text = tk.Text(self.sidebar, height=5, width=10, font=("Consolas", 8))
        self.log_text.pack()

        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Button-3>", self.on_right_click)

    def log_event(self, message):
        self.log_text.insert(tk.END, f"> {message}\n")
        self.log_text.see(tk.END)

    def on_canvas_click(self, event):
        x, y = event.x, event.y
        mode = self.mode.get()

        if mode in ["PC", "Router", "Switch"]:
            node_name = f"{mode}{self.node_counter}"
            self.node_counter += 1
            self.G.add_node(node_name, type=mode, ip="0.0.0.0", pos=(x, y))
            self.nodes_pos[node_name] = (x, y)
            self.draw_network()
            self.log_event(f"Created {node_name}")

        elif mode == "Link":
            clicked_node = self.get_node_at_pos(x, y)
            if clicked_node:
                if self.selected_node is None:
                    self.selected_node = clicked_node
                    self.log_event(f"Selected {clicked_node}, click another to link.")
                else:
                    if clicked_node != self.selected_node:
                        if not self.G.has_edge(self.selected_node, clicked_node):
                            self.G.add_edge(self.selected_node, clicked_node)
                            self.log_event(f"Connected {self.selected_node} <--> {clicked_node}")
                        self.selected_node = None
                        self.draw_network()
                    else:
                        self.selected_node = None

    def get_node_at_pos(self, x, y):
        for node, pos in self.nodes_pos.items():
            nx_, ny_ = pos
            if math.hypot(nx_ - x, ny_ - y) <= NODE_RADIUS:
                return node
        return None

    def on_right_click(self, event):
        node = self.get_node_at_pos(event.x, event.y)
        if node:
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label=f"Properties ({node})", command=lambda: self.open_properties(node))
            menu.add_command(label="Delete", command=lambda: self.delete_node(node))
            menu.add_separator()
            menu.add_command(label="Ping from this", command=lambda: self.ping_from_node(node))
            menu.post(event.x_root, event.y_root)

    def open_properties(self, node):
        data = self.G.nodes[node]
        win = tk.Toplevel(self.root)
        win.title(f"Properties: {node}")
        win.geometry("300x220")

        tk.Label(win, text="Device Name:").pack(pady=5)
        name_entry = tk.Entry(win)
        name_entry.insert(0, node)
        name_entry.pack()

        tk.Label(win, text="IP Address:").pack(pady=5)
        ip_entry = tk.Entry(win)
        ip_entry.insert(0, data.get("ip", "0.0.0.0"))
        ip_entry.pack()

        tk.Label(win, text="Type:").pack(pady=5)
        type_label = tk.Label(win, text=data.get("type", "Unknown"))
        type_label.pack()

        def save():
            new_name = name_entry.get().strip()
            new_ip = ip_entry.get().strip()
            if not new_name:
                messagebox.showerror("Error", "Name cannot be empty")
                return
            if new_name != node:
                if new_name in self.G.nodes:
                    messagebox.showerror("Error", "Name already exists")
                    return
                self.G = nx.relabel_nodes(self.G, {node: new_name})
                self.nodes_pos[new_name] = self.nodes_pos.pop(node)
                node_ref = new_name
            else:
                node_ref = node

            self.G.nodes[node_ref]["ip"] = new_ip
            self.log_event(f"Updated {node_ref} IP to {new_ip}")
            self.draw_network()
            win.destroy()

        tk.Button(win, text="Save", command=save, bg="#4CAF50", fg="white").pack(pady=20)

    def delete_node(self, node):
        if node in self.G.nodes:
            self.G.remove_node(node)
        if node in self.nodes_pos:
            del self.nodes_pos[node]
        self.draw_network()
        self.log_event(f"Deleted {node}")

    def draw_network(self):
        self.canvas.delete("all")

        for u, v in self.G.edges():
            x1, y1 = self.nodes_pos[u]
            x2, y2 = self.nodes_pos[v]
            self.canvas.create_line(x1, y1, x2, y2, width=2, fill="gray")

        for node, pos in self.nodes_pos.items():
            x, y = pos
            color = COLORS.get(self.G.nodes[node].get("type", ""), "gray")
            self.canvas.create_oval(
                x - NODE_RADIUS,
                y - NODE_RADIUS,
                x + NODE_RADIUS,
                y + NODE_RADIUS,
                fill=color,
                outline="black",
                width=2
            )
            self.canvas.create_text(x, y + NODE_RADIUS + 15, text=node, font=("Arial", 10))
            ip = self.G.nodes[node].get("ip", "")
            if ip and ip != "0.0.0.0":
                self.canvas.create_text(x, y + NODE_RADIUS + 28, text=ip, font=("Arial", 8, "italic"), fill="blue")

    def ping_window(self):
        win = tk.Toplevel(self.root)
        win.title("Ping Test")

        tk.Label(win, text="Source Node:").grid(row=0, column=0, padx=5, pady=5)
        src_entry = tk.Entry(win)
        src_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(win, text="Destination Node:").grid(row=1, column=0, padx=5, pady=5)
        dst_entry = tk.Entry(win)
        dst_entry.grid(row=1, column=1, padx=5, pady=5)

        def run_ping():
            u = src_entry.get().strip()
            v = dst_entry.get().strip()
            if u in self.G.nodes and v in self.G.nodes:
                try:
                    path = nx.shortest_path(self.G, source=u, target=v)
                    self.log_event(f"Ping {u}->{v}: SUCCESS")
                    self.log_event(f"Path: {' -> '.join(path)}")
                    messagebox.showinfo("Ping Result", f"Reply from {v}\nPath: {' -> '.join(path)}")
                except nx.NetworkXNoPath:
                    self.log_event(f"Ping {u}->{v}: FAILED (Unreachable)")
                    messagebox.showerror("Ping Result", "Destination Unreachable")
            else:
                messagebox.showerror("Error", "Invalid Node Names")

        tk.Button(win, text="Ping", command=run_ping).grid(row=2, column=0, columnspan=2, pady=10)

    def ping_from_node(self, src_node):
        dst = simpledialog.askstring("Ping", f"Ping from {src_node} to:")
        if not dst:
            return
        if dst not in self.G.nodes:
            messagebox.showerror("Error", "Destination node does not exist")
            return
        try:
            path = nx.shortest_path(self.G, source=src_node, target=dst)
            self.log_event(f"Ping {src_node}->{dst}: SUCCESS")
            self.log_event(f"Path: {' -> '.join(path)}")
            messagebox.showinfo("Ping Result", f"Reply from {dst}\nPath: {' -> '.join(path)}")
        except nx.NetworkXNoPath:
            self.log_event(f"Ping {src_node}->{dst}: FAILED (Unreachable)")
            messagebox.showerror("Ping Result", "Destination Unreachable")


# Start the app in a simple way
root = tk.Tk()
root.title("Simple Network Simulator (Python)")
root.geometry("900x600")
NetworkSimulator(root)
root.mainloop()