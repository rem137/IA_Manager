import sys
from .cli.commands import build_parser
from .cli.shell import interactive_loop


def main():
    parser = build_parser()
    if len(sys.argv) > 1:
        args = parser.parse_args()
        if hasattr(args, 'func'):
            args.func(args)
        else:
            parser.print_help()
    else:
        interactive_loop()


if __name__ == "__main__":
    main()
