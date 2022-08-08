from argparse import ArgumentParser, Namespace


class CLI:

    def __init__(self, parser: ArgumentParser):
        self.namespace: Namespace = parser.parse_args()

    def __call__(self):
        if self.namespace.command:
            available_commands = [
                command_name
                for command_name
                in self.__dir__()
                if not command_name.startswith("__")
            ]
            if self.namespace.command not in available_commands:
                print("Wrong command!")
                exit(1)

            command = getattr(self, self.namespace.command)
            if not command:
                print("Can't find this command in CLI.")
                exit(1)

            command()

    def apply(self):
        print("We are in apply")
        pass

    def rollback(self):
        print("We are in rollback")
        pass

    def initdb(self):
        print("We are in initdb")
        pass


def get_cli(parser: ArgumentParser):
    return CLI(parser)
