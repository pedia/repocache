import argparse
import configparser
import logging

from .server import Server


def main():
  parser = argparse.ArgumentParser(
      description='univasal repo cache',
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument('-f,--config-file',
                      default='default.cfg',
                      dest='config_file',
                      help='config file')
  parser.add_argument('--address',
                      default='0.0.0.0:5000',
                      help='Address to bind to.')
  parser.add_argument('-v,--verbose',
                      default=False,
                      dest='verbose',
                      action='store_true',
                      help='Show additional command output.')
  parser.add_argument('--debug',
                      default=False,
                      action='store_true',
                      help='Turn on debugging logging and output.')
  parser.add_argument('--reload',
                      default=False,
                      action='store_true',
                      help='Turn on automatic reloading on code changes.')
  parser.add_argument('--processes',
                      default=1,
                      type=int,
                      help='Number of processes to run')
  args = parser.parse_args()
  if args.verbose:
    print('args:', args)

  #
  config = configparser.ConfigParser()
  config.read(args.config_file)

  if False:  # args.verbose:
    for section_name in config.sections():
      print(f'[{section_name}]')
      sec = config[section_name]
      for key in sec:
        print(' ', key, sec[key])

  loglevel = logging.DEBUG if args.debug else logging.INFO
  logging.basicConfig(level=loglevel)

  # avoid trivial log of other libraries
  logging.getLogger('urllib3.connectionpool').setLevel(logging.ERROR)
  logging.getLogger('filelock').setLevel(logging.ERROR)

  app = Server(config)

  if args.verbose:
    app.dump_urls()

  host, port = args.address.split(':')
  app.run(
      host=host,
      port=port,
      debug=args.debug,
      use_reloader=args.reload,
      processes=args.processes,
  )


if __name__ == '__main__':
  main()
