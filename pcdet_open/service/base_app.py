import json
from argparse import ArgumentParser

from .logger import start_logger, logging

import tornado.ioloop
from tornado.escape import json_decode
from tornado.web import RequestHandler, Application


class BaseApiHandler(RequestHandler):
    def write_error(self, status_code: int, **kwargs) -> None:
        if "exc_info" in kwargs:
            message = str(kwargs["exc_info"][1])
        else:
            message = self._reason
        self.return_error(message, status_code=status_code)

    def return_error(self, message, status_code=400):
        logging.warning(message)
        self.set_status(status_code)
        self._return_json({
            'message': message
        })

    def return_ok(self, data):
        self._return_json({
            "code": "OK",
            "message": "",
            "data": data
        })

    def _return_json(self, obj):
        self.write(json.dumps(obj,ensure_ascii=False, separators=(',', ':')))

    # override: Called at the beginning of a request before get/post/etc.
    def prepare(self):
        self.args = json_decode(self.request.body) if self.request.body else {}
        self.set_header("Content-Type", 'application/json')

    def get_field(self, obj, key, type_, check_empty=False):
        value = obj.get(key, None)
        if value is None:
            raise ValueError(f'no "{key}" field')

        if not isinstance(value, type_):
            raise ValueError(f'the value of "{key}" must be a {type_.__name__}')

        if check_empty and len(value) == 0:
            raise ValueError(f'the value of "{key}" is empty')

        return value

class HelpHandler(RequestHandler):
    def initialize(self, url: str):
        self.url = url

    def get(self):
        self.write(f"<p>please refer {self.url}</p>")


def _make_app(handlers, help_url=None) -> Application:
    all_handlers = handlers.copy() # extended in future
    if help_url is not None:
        all_handlers.append((r'/help', HelpHandler, dict(url=help_url)))

    return Application(all_handlers)
    

def start_service(handlers, args, help_url=None):
    """
    :param handlers: a list of hander. a handler is a tupe: (url, BaseApiHandler)
    """

    logging.info("----- SERVER STARTED -----")
    app = _make_app(handlers, help_url)

    server = tornado.httpserver.HTTPServer(app, 
                                           max_buffer_size=10485760, 
                                           body_timeout=1000.)#body_timeout仅用于限制数据传输时间
    server.bind(args.port)
    server.start(args.num_processes)
    print('Tornado server starting on port {}'.format(args.port), flush=True)
    tornado.ioloop.IOLoop.current().start()

def parse_args(parser: ArgumentParser):
    parser.add_argument('--port', type=int, default=5000)
    parser.add_argument('--num_processes', type=int, default=1)
    parser.add_argument('--log_dir', type=str, default=None)
    parser.add_argument('--log_level', type=str, default="INFO", nargs='?', help="logging level")
    parser.add_argument('-d', '--debug', action='store_true')
    args = parser.parse_args()

    if args.debug:
        import pdb
        pdb.set_trace()

    start_logger(level=args.log_level, output_dir=args.log_dir)
    return args
