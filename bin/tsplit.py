#!/usr/bin/env python

from argparse import ArgumentParser

from six import print_

from tablesplitter.command import registry

def list_commands():
    print_("Available commands: \n")
    for name, cls in registry.items():
        print_("* {} - {}".format(name, cls.help))

if __name__ == "__main__":
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest='subparser_name')

    subparsers.add_parser('list', help="List available commands")
    
    for name, cls in registry.items():
        subparser = subparsers.add_parser(name, help=cls.help)
        cls.add_arguments(subparser)

    args = parser.parse_args()

    if args.subparser_name == "list":
        list_commands()
    else:
        cmd = registry.get(args.subparser_name)()
        cmd.run(args)
