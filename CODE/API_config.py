# Configuration file for all of the API endpoints with basic parameters  # noqa: N999
API_BASE_URL = "https://dataportal-api.nordpoolgroup.com/api/"

API_ENDPOINTS = {
    "DayAheadPrices": {
        "path": "DayAheadPrices",
        "method": "GET",
        "params": {
            "date": {
                "required": True,
                "query_name": "date",
                "type": "date",
            },
            "market": {
                "required": True,
                "query_name": "market",
                "type": "enum",
                "values": ["DayAhead"],
            },
            "delivery_area": {
                "required": True,
                "query_name": "deliveryArea",
                "type": "list",
                "values": ["EE", "LV", "LT", "FI", "AT", "BE", "FR", "GER", "NL", "PL"],
            },
            "currency": {
                "required": True,
                "query_name": "currency",
                "type": "enum",
                "values": ["EUR"],
            },
        },
        "response": {
            "table_name": "day_ahead_prices",
            "record_key": "Rows",
        }
    },
    "DayAheadPriceIndices" : {
        "path": "DayAheadPriceIndices",
        "method": "GET",
        "params": {
            "date": {
                "required": True,
                "query_name": "date",
                "type": "date",
            },
            "market": {
                "required": True,
                "query_name": "market",
                "type": "enum",
                "values": ["DayAhead"],
            },
            "indexNames": {
                "required": True,
                "query_name": "indexNames",
                "type": "list",
                "values": ["EE", "LV", "LT", "FI", "AT", "BE", "FR", "GER", "NL", "PL"],
            },
            "currency": {
                "required": True,
                "query_name": "currency",
                "type": "enum",
                "values": ["EUR"],
            },
            "resolutionInMinutes" : {
                "required" : True,
                "query_name" : "resolutionInMinutes",
                "type" : "enum",
                "values" : ["15", "30", "60"]
            }
        },
        "response": {
            "table_name": "day_ahead_price_indecies",
            "record_key": "Rows",
        }
    },
    "DayAheadVolumes" : {
        "path": "DayAheadVolumes/multiple",
        "method": "GET",
        "params": {
            "date": {
                "required": True,
                "query_name": "date",
                "type": "date",
            },
            "market": {
                "required": True,
                "query_name": "market",
                "type": "enum",
                "values": ["DayAhead"],
            },
            "deliveryAreas": {
                "required": True,
                "query_name": "deliveryAreas",
                "type": "list",
                "values": ["EE", "LV", "LT", "FI", "PL"],
            }
        },
        "response": {
            "table_name": "day_ahead_volumes",
            "record_key": "Rows",
        }
    },
    "AggregatedBidCurves" : {
        "path": "AggregatedBidCurves",
        "method": "GET",
        "params": {
            "date": {
                "required": True,
                "query_name": "date",
                "type": "date",
            },
            "marketCode": {
                "required": True,
                "query_name": "marketCode",
                "type": "enum",
                "values": ["NPSDA"],
            },
            "clusterName": {
                "required": True,
                "query_name": "clusterName",
                "type": "enum",
                "values": ["BALTIC"],
            }
        },
        "response": {
            "table_name": "day_ahead_agg_sup_dem",
            "record_key": "Rows",
        }
    },
    "DayAheadCapacities" : {
        "path": "DayAheadCapacities",
        "method": "GET",
        "params": {
            "date": {
                "required": True,
                "query_name": "date",
                "type": "date",
            },
            "market": {
                "required": True,
                "query_name": "market",
                "type": "enum",
                "values": ["DayAhead"],
            },
            "deliveryAreas": {
                "required": True,
                "query_name": "deliveryAreas",
                "type": "enum",
                "values": ["EE", "LV", "LT", "FI_EL","FI_FS", "PL"],
            }
        },
        "response": {
            "table_name": "day_ahead_capacity",
            "record_key": "Rows",
        }
    },
    "DayAheadFlows" : {
        "path": "DayAheadFlows",
        "method": "GET",
        "params": {
            "date": {
                "required": True,
                "query_name": "date",
                "type": "date",
            },
            "market": {
                "required": True,
                "query_name": "market",
                "type": "enum",
                "values": ["DayAhead"],
            },
            "deliveryAreas": {
                "required": True,
                "query_name": "deliveryAreas",
                "type": "enum",
                "values": ["EE", "LV", "LT", "FI", "PL"],
            },
        },
        "response": {
            "table_name": "day_ahead_flow",
            "record_key": "Rows",
        }
    },
}