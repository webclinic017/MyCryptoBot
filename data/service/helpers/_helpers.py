import datetime
import json
import logging
import os

import django
import pytz
from flask import jsonify

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from data.service.helpers.responses import Responses
from database.model.models import Symbol, Exchange, Pipeline
import shared.exchanges.binance.constants as const

MODEL_APP_ENDPOINTS = {
    "GENERATE_SIGNAL": lambda host_url: f"{host_url}/generate_signal",
    "CHECK_JOB": lambda host_url, job_id: f"{host_url}/check_job/{job_id}",
    "GET_STRATEGIES": lambda host_url: f"{host_url}/strategies",
}

EXECUTION_APP_ENDPOINTS = {
    "START_SYMBOL_TRADING": lambda host_url: f"{host_url}/start_symbol_trading",
    "STOP_SYMBOL_TRADING": lambda host_url: f"{host_url}/stop_symbol_trading",
}


def check_input(strategies, **kwargs):

    if "symbol" in kwargs:
        symbol = kwargs["symbol"]

        if symbol is None:
            return jsonify(Responses.SYMBOL_REQUIRED)

        try:
            Symbol.objects.get(name=symbol)
        except Symbol.DoesNotExist as e:
            logging.debug(symbol)
            logging.debug(e)
            return jsonify(Responses.SYMBOL_INVALID(symbol))

    if "exchange" in kwargs:
        exchange = kwargs["exchange"]

        if exchange is None:
            return jsonify(Responses.EXCHANGE_REQUIRED)

        try:
            Exchange.objects.get(name=exchange.lower())
        except (Exchange.DoesNotExist, AttributeError) as e:
            logging.debug(exchange)
            logging.debug(e)
            return jsonify(Responses.EXCHANGE_INVALID(exchange))

    if "candle_size" in kwargs:
        candle_size = kwargs["candle_size"]

        if candle_size is None:
            return jsonify(Responses.CANDLE_SIZE_REQUIRED)

        if candle_size not in const.CANDLE_SIZES_MAPPER:
            logging.debug(candle_size)
            return jsonify(Responses.CANDLE_SIZE_INVALID(candle_size))

    if "strategy" in kwargs:
        strategy = kwargs["strategy"]

        if strategy is None:
            return jsonify(Responses.STRATEGY_REQUIRED)

        if strategy in strategies:
            if "params" in kwargs:
                params = kwargs["params"]

                invalid_params = []
                for key in params:
                    if key not in strategies[strategy]["params"] and key not in strategies[strategy]["optional_params"]:
                        logging.debug(key)
                        invalid_params.append(key)

                if len(invalid_params) > 0:
                    return jsonify(Responses.PARAMS_INVALID(', '.join(invalid_params)))

            required_params = []
            for param in strategies[strategy]["params"]:
                if param not in kwargs.get("params", {}):
                    required_params.append(param)

            if len(required_params) > 0:
                response = Responses.PARAMS_REQUIRED(', '.join(required_params))
                logging.debug(response)
                return jsonify(response)
        else:
            logging.debug(strategy)
            return jsonify(Responses.STRATEGY_INVALID(strategy))

    if "name" not in kwargs or kwargs["name"] is None:
        return jsonify(Responses.NAME_REQUIRED)
    else:
        name = kwargs["name"]
        if not isinstance(name, str):
            return jsonify(Responses.NAME_INVALID(kwargs["name"]))

    if "color" not in kwargs or kwargs["name"] is None:
        return jsonify(Responses.COLOR_REQUIRED)

    return None


def get_or_create_pipeline(
    name,
    color,
    allocation,
    symbol,
    candle_size,
    strategy,
    exchange,
    params,
    paper_trading
):

    columns = dict(
        name=name,
        color=color,
        allocation=allocation,
        symbol_id=symbol,
        interval=candle_size,
        strategy=strategy,
        exchange_id=exchange,
        params=json.dumps(params),
        paper_trading=paper_trading
    )

    try:
        pipeline = Pipeline.objects.get(**columns)

        if pipeline.active:
            return pipeline, jsonify(Responses.DATA_PIPELINE_ONGOING(pipeline.id))
        else:
            pipeline.active = True
            pipeline.open_time = datetime.datetime.now(pytz.utc)

        pipeline.save()

    except Pipeline.DoesNotExist:
        print("we got here")
        pipeline = Pipeline.objects.create(**columns)

    return pipeline, None


def convert_queryset_to_dict(queryset):
    return {res["name"]: res for res in queryset}

