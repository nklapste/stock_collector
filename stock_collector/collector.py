#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Collect stock data using yfinance"""

import sqlite3
from time import sleep
from datetime import timedelta, date, datetime
from math import ceil
from logging import getLogger

from pandas import DataFrame
import yfinance as yf

__log__ = getLogger(__name__)


def daterange(
    start_date: date, end_date: date, inc_days: int = 1, cap_to_present: bool = True
):
    """Create a iterator yielding :class:datetime.datetime`s between ``start_date`` and
    ``end_date`` that increment by the day value ``inc_days``"""
    if start_date >= end_date:
        raise ValueError("start_date must be smaller than end_date")
    for n in range(0, ceil(int((end_date - start_date).days) / inc_days)):
        range_start_date = start_date + timedelta(n * inc_days)
        range_end_date = start_date + timedelta((n + 1) * inc_days - 1)
        if cap_to_present and range_end_date >= datetime.utcnow().date():
            yield range_start_date, datetime.utcnow().date()
            return
        yield range_start_date, range_end_date


def scrape_stock_data(
    database_path: str,
    stock_code: str,
    start_date: date,
    end_date_range: date,
    interval: str = "1m",
):
    for start_date_range, end_date_range in daterange(start_date, end_date_range, 7):
        if start_date_range < datetime.utcnow().date() - timedelta(30):
            __log__.warning(
                "Scrape end range 30 days in past can only get day interval. setting fallback_interval to 1d"
            )
            fallback_interval = "1d"
        else:
            __log__.debug(f"using provided interval {interval}")
            fallback_interval = None
        start_date_range = start_date_range.strftime("%Y-%m-%d")

        end_date_range = end_date_range.strftime("%Y-%m-%d")
        __log__.info(
            f"Scraping stock {stock_code} from {start_date_range} to {end_date_range}"
        )

        while True:
            sleep(2)
            data: DataFrame = yf.download(
                stock_code,
                start=start_date_range,
                end=end_date_range,
                interval=fallback_interval or interval,
                prepost=True,
            )
            if data.empty:
                if fallback_interval != "1d":
                    raise RuntimeError(
                        "Obtained emtpy stock data and fallback_interval is already 1d something is wrong"
                    )
                __log__.warning("Obtained empty stock data switching to 1d interval")
                fallback_interval = "1d"
            else:
                __log__.debug(f"Obtained stock data {data.shape}")
                break
        conn = sqlite3.connect(database_path)

        # convert the dataframe to a temp sql table for later insertion
        temp_table = f"stock_{stock_code}_temporary_table"
        perm_table = f"stock_{stock_code}"
        data.to_sql(temp_table, conn, if_exists="replace", index="Datetime")

        conn.execute(
            f"""
create table if not exists {perm_table}
(
    Datetime    TIMESTAMP,
    Open        REAL,
    High        REAL,
    Low         REAL,
    Close       REAL,
    "Adj Close" REAL,
    Volume      INTEGER,
    constraint stocks_pk
        primary key (Datetime)
);
"""
        )

        # take temp table data and insert it into the master table
        # ignore duplicates
        conn.execute(f"INSERT OR REPLACE INTO {perm_table} SELECT * FROM {temp_table}")

        # delete temp table
        conn.execute(f"DROP TABLE {temp_table}")
        conn.commit()
