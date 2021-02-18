import argparse
import logging

import pypicache.server


def main():
  parser = argparse.ArgumentParser(
      description="univasal repo cache",
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("prefix",
                      default="/tmp/packages",
                      help="Package prefix, e.g. /tmp/packages")
  parser.add_argument("--address",
                      default="0.0.0.0:5000",
                      help="Address to bind to.")
  parser.add_argument("--debug",
                      default=False,
                      action="store_true",
                      help="Turn on debugging logging and output.")
  parser.add_argument("--reload",
                      default=False,
                      action="store_true",
                      help="Turn on automatic reloading on code changes.")
  parser.add_argument("--processes",
                      default=1,
                      type=int,
                      help="Number of processes to run")
  parser.add_argument("--upstream",
                      default="https://pypi.org/",
                      help="Upstream package server to use")
  args = parser.parse_args()

  loglevel = logging.DEBUG if args.debug else logging.INFO

  logging.basicConfig(
      level=loglevel,
      # format=
      # "%(asctime)s [%(levelname)s] [%(processName)s-%(threadName)s] [%(name)s] [%(filename)s:%(lineno)d] %(message)s",
      # datefmt="%Y-%m-%d %H:%M:%S%z"
  )
  logging.info("Debugging: {0!r} Reloading: {0!r}", args.debug, args.reload)

  app = pypicache.server.configure_app(debug=args.debug)

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
