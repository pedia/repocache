import argparse
import logging

import repocache.server


def main():
  parser = argparse.ArgumentParser(
      description="univasal repo cache",
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("--cache-folder",
                      default="/tmp/packages",
                      help="Where to store cache files")
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
  parser.add_argument("--pypi-upstream",
                      default="https://pypi.org/",
                      help="Upstream server for pypi")
  args = parser.parse_args()

  loglevel = logging.DEBUG if args.debug else logging.INFO

  logging.basicConfig(level=loglevel)
  logging.info("Debugging: %s Reloading: %s", args.debug, args.reload)

  logging.getLogger('urllib3.connectionpool').setLevel(logging.ERROR)
  logging.getLogger('filelock').setLevel(logging.ERROR)

  app = repocache.server.configure_app(debug=args.debug)

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
