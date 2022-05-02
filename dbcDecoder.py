import argparse
import cantools
import can
import datetime
import signal


class DBCDecoder():
    def __init__(self, dbc: str, device: str):  
        try:
            self.__db = cantools.database.load_file(dbc)
            self.__can_bus = can.interface.Bus(device, bustype='socketcan')
        except (FileNotFoundError, ValueError, OSError) as err:
            print(f"{err}")
            exit(1)
        # install signal handler
        signal.signal(signal.SIGINT, self._handler)
        self._print_all_messages(messages=self.__db.messages)

    @staticmethod
    def _handler(signum, frame):
        res = input("Ctrl-c was pressed. Do you really want to exit? y/n ")
        if res == 'y':
            exit(1)

    def _print_all_messages(self, messages: list):
        for message in self.__db.messages:
            print(f'{hex(message.frame_id)} - {message.name} ({message.length} Bytes - timing: {message.cycle_time} ms):')
            for signal in message.signals:
                self._print_signal(signal=signal)

    def _print_signal(self, signal: cantools.database.can.signal.Signal):
        print(f'\t{signal.name} ({signal.comment})')
        print(f'\t\tSTART: {signal.start}')
        print(f'\t\tLENGTH [bit]: {signal.length}')
        print(f'\t\tBO: {signal.byte_order}')
        print(f'\t\tIS SIGNED: {signal.is_signed}')
        print(f'\t\tIS FLOAT: {signal.is_float}')
        print(f'\t\tSCALE: {signal.scale}')
        print(f'\t\tOFFSET: {signal.offset}')
        print(f'\t\tMINIMUM: {signal.minimum}')
        print(f'\t\tMAXIMUM: {signal.maximum}')
        print(f'\t\tUNIT: {signal.unit}')
        print(f'\t\tCHOICES: {signal.choices}')

    def run(self):
        while True:
            message = self.__can_bus.recv()
            print(f'{datetime.datetime.utcnow()} - {hex(message.arbitration_id)} {self.__db.decode_message(message.arbitration_id, message.data)}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Decode CAN messages using a DBC file')
    parser.add_argument('dbc', help='path to dbc file', type=str)
    parser.add_argument('device', help='CAN interface to be used', type=str)
    args = parser.parse_args()

    decoder = DBCDecoder(dbc=args.dbc, device=args.device)
    decoder.run()