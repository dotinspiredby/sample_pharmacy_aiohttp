from typing import Union


def ok_response(data: Union[list, dict]):
    return {
        "status": "ok",
        "data": data,
    }


def error_response(status: str, message: str, data: Union[list, dict]):
    return {
        "status": status,
        "message": message,
        "data": data,
    }


async def check_empty_table_exists(cli, tablename: str):
    db = cli.app.database.db
    query = db.text(f"SELECT count(1) FROM {tablename}")
    count = await db.scalar(query)
    assert count == 0
