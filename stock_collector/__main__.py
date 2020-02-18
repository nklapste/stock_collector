#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""main entry point for stock-collector"""

import argparse
import logging
import os
import sys
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler

from stock_collector.collector import scrape_stock_data

LOG_LEVEL_STRINGS = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]


def log_level(log_level_string: str):
    """argparse type function for determining the specified logging level"""
    if log_level_string not in LOG_LEVEL_STRINGS:
        raise argparse.ArgumentTypeError(
            "invalid choice: {} (choose from {})".format(
                log_level_string, LOG_LEVEL_STRINGS
            )
        )
    return getattr(logging, log_level_string, logging.INFO)


def add_log_parser(parser):
    """Add logging options to the argument parser"""
    group = parser.add_argument_group(title="Logging")
    group.add_argument(
        "--log-level",
        dest="log_level",
        default="INFO",
        type=log_level,
        help="Set the logging output level",
    )
    group.add_argument(
        "--log-dir",
        dest="log_dir",
        help="Enable TimeRotatingLogging at the directory " "specified",
    )
    group.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )


def init_logging(args, log_file_path):
    """Intake a argparse.parse_args() object and setup python logging"""
    handlers_ = []
    log_format = logging.Formatter(fmt="%(asctime)s %(levelname)s %(message)s")
    if args.log_dir:
        os.makedirs(args.log_dir, exist_ok=True)
        file_handler = TimedRotatingFileHandler(
            os.path.join(args.log_dir, log_file_path),
            when="d",
            interval=1,
            backupCount=7,
            encoding="UTF-8",
        )
        file_handler.setFormatter(log_format)
        file_handler.setLevel(args.log_level)
        handlers_.append(file_handler)
    if args.verbose:
        stream_handler = logging.StreamHandler(stream=sys.stderr)
        stream_handler.setFormatter(log_format)
        stream_handler.setLevel(args.log_level)
        handlers_.append(stream_handler)

    logging.basicConfig(handlers=handlers_, level=args.log_level)


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-db", "--database", required=True, help="Path to the database file to populte"
    )
    parser.add_argument(
        "--stocks", nargs="+", required=True, help="List of stocks to scrape"
    )
    parser.add_argument(
        "--lookback",
        type=int,
        default=2,
        help="Number of days to lookback for historic stock data",
    )
    add_log_parser(parser)

    return parser


def main():
    args = get_parser().parse_args()
    init_logging(args, "stock_collector.log")

    present = datetime.utcnow()
    start_date = (present - timedelta(days=args.lookback)).date()
    end_date = present.date()
    for stock_code in args.stocks:
        scrape_stock_data(
            database_path=args.database,
            stock_code=stock_code,
            start_date=start_date,
            end_date_range=end_date,
        )


if __name__ == "__main__":
    main()
