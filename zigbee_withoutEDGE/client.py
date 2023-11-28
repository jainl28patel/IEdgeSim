from zigbee import Coordinator, Router, EndDevice, Network

if __name__ == "__main__":
   coordinator = Coordinator("C", None)
   network = Network(coordinator)
   coordinator.network = network
   coordinator.start_network()

   router1 = Router("R1")
   router2 = Router("R2")
   end_device = EndDevice("D1")

   coordinator.add_node_to_network(router1)
   coordinator.add_node_to_network(router2)
   coordinator.add_node_to_network(end_device)

   try:
       end_device.send_message(router1.address, "Hello from End Device")
   except AttributeError:
       print("Error: Unable to send message. Check if the recipient node is in the network.")

   try:
       router1.send_message(end_device.address, "Hello back to you, End Device")
   except AttributeError:
       print("Error: Unable to send message. Check if the recipient node is in the network.")

   try:
       network.coordinator.send_message(router2.address, "Broadcast message from Coordinator")
   except AttributeError:
       print("Error: Unable to send message. Check if the recipient node is in the network.")
