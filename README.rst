###############
stock-collector
###############

Description
===========

Stock collector using yfinance to collect stocks into a sqlite database.

Installation
============

To install stock-collector run the following command within the project folder
containing `setup.py`:

.. code-block:: console

    pip install .

Usage
=====

After installing stock-collector, to collect MSFT stocks and store them into the sqlite
file ``stocks.sql`` run the following command:

.. code-block:: console

    stock-collector --database all_stocks.sql --stocks MSFT

To get additional help on using stock-collector run:

.. code-block:: console

    stock-collector --help
