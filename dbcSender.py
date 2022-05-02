import argparse
import cantools
import can
import random
import datetime
import signal

class DBCSender():
    def __init__(self, dbc: str, device: str):
        try:
            self.__db = cantools.database.load_file(dbc)
            self.__can_bus = can.interface.Bus(device, bustype='socketcan')
        except (FileNotFoundError, ValueError, OSError) as err:
            print(f"{err}")
            exit(1)
        # install signal handler
        signal.signal(signal.SIGINT, self._handler)

    @staticmethod
    def _handler(signum, frame):
        res = input("Ctrl-c was pressed. Do you really want to exit? y/n ")
        if res == 'y':
            exit(1)

    def _get_new_value(self, old_value: int, value_minimum: int, value_maximum: int, max_diff: int):
        new_value = old_value + random.randint(max_diff/2*(-1), max_diff/2)
        while new_value < value_minimum or new_value > value_maximum:
            new_value = old_value + random.randint(max_diff/2*(-1), max_diff/2)
        return new_value

    def show_messages(self):
        self._print_all_messages(messages=self.__db.messages)

    def run(self, cycle_time_ms: int=100):
        previous_data = {}
        while True:
            start_time = datetime.datetime.utcnow()
            for message in self.__db.messages:
                data = {}
                if message.name not in previous_data:
                    for signal in message.signals:
                        data.update({signal.name: random.randint(signal.minimum, signal.maximum)})
                else:
                    for signal in message.signals:
                        data.update({signal.name: self._get_new_value(old_value=previous_data[message.name][signal.name], 
                                                                        value_minimum=signal.minimum, 
                                                                        value_maximum=signal.maximum, 
                                                                        max_diff=10)})

                previous_data.update({message.name: data})
                msg = can.Message(arbitration_id=message.frame_id, data=message.encode(data))
                print(f'actual data: {data} - message: {hex(msg.arbitration_id)} {msg.data.hex().upper()}')
                self.__can_bus.send(msg)
            
            # wait until cycle time is over before sending next message
            while datetime.datetime.utcnow() - start_time < datetime.timedelta(milliseconds=cycle_time_ms): pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Decode CAN messages using a DBC file')
    parser.add_argument('dbc', help='path to dbc file', type=str)
    parser.add_argument('device', help='CAN interface to be used', type=str)
    parser.add_argument('cycle_time', help='time in milliseconds between each sending cycle', type=int)
    args = parser.parse_args()

    encoder = DBCSender(dbc=args.dbc, device=args.device)
    encoder.run(cycle_time_ms=args.cycle_time)