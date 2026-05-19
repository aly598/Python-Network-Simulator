# Simple Network Simulator 🌐

A Python-based graphical network simulator built using `tkinter` and `networkx`. This project allows users to visually build network topologies, configure IP addresses, and simulate basic network connectivity using shortest-path algorithms.

## Features ✨
- **Visual Topology Builder:** Add PCs, Switches, and Routers to the canvas.
- **Device Linking:** Connect devices seamlessly with point-to-point links.
- **Properties Configuration:** Assign and manage IP addresses for individual nodes.
- **Ping Simulation:** Test reachability between source and destination nodes to ensure connectivity.
- **Event Logging:** Real-time tracking of network modifications, connections, and ping test results.

## Screenshots 📸

### Main Interface
![Main Interface](Images/main_interface.png)

### Network Topology Example
![Network Topology](Images/topology_view.png)

### Successful Ping Test
![Ping Test](Images/ping_success.png)

## Prerequisites 🛠️
Make sure you have Python installed along with the required libraries. You will need `networkx`:
```bash
pip install networkx