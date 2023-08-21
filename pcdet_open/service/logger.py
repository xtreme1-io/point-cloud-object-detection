# encoding=utf-8
import logging
from logging.handlers import TimedRotatingFileHandler
import os
from os.path import join, exists
import sys


def __logging_level_from_str(level):
    level = level.upper()
    return logging.getLevelName(level)


def start_logger(level="INFO", backup_count=365, output_dir=None):
    """start the logger. write file and backup.

    :param level:  a level string: "DEBUG", "INFO", "WARN", "ERROR"
    :param backup_count: backup count, unit: day
    :param output_dir:
    :return:
    """
    level = __logging_level_from_str(level)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # file handler
    filename_directory = join(output_dir or os.getcwd(), 'server_logs', 'pid' + str(os.getpid()))
    if not exists(filename_directory):
        os.makedirs(filename_directory)

    file_handler = TimedRotatingFileHandler(join(filename_directory, "log.txt"),
                                            when="midnight",
                                            backupCount=backup_count)
    file_handler.setLevel(level)
    file_handler.suffix = "%Y%m%d"
    formatter = logging.Formatter(fmt="%(asctime)s %(levelname)s %(funcName)s: %(message)s",
                                  datefmt="%Y-%m-%d %H:%M:%S")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # print to stdout
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(level)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # info
    length = 20
    logging.log(level, "-" * length + " logging start " + "-" * length)
    logging.log(level, "LEVEL: {}".format(logging.getLevelName(level)))
    logging.log(level, "PATH:  {}".format(filename_directory))
    logging.log(level, "-" * (length * 2 + 15))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('level', type=str, default="INFO", nargs='?', help="logging level")
    args = parser.parse_args()

    start_logger(args.level)
