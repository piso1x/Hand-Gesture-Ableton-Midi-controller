import mido 
class MidiController: 
    def __init__(self, port_name="Python Hand Gestures"): 
        self.outport = mido.open_output(port_name, virtual=True) 
    def send_cc(self, value):
        msg = mido.Message('control_change', control=1, value=value)
        self.outport.send(msg)
    def close(self):
        self.outport.close()