"""
API for requests from the TOASTIES.
"""

from typing import Annotated

from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import Response
import uvicorn

from actions.registry import Registry
from actions.sheets import *
from utils.anal import *
from utils.sheet_updates import *
from utils.types import Scoresheet

app = FastAPI()
REGISTRY = Registry()

def get_room_stats(number: int):
    scores_id = REGISTRY.scoresheet_id(number)
    writers = get_sheet_names(scores_id)
    if len(writers) == 1 and writers[0] == "Sheet1":
        return {
            "writers": [],
            "statsheets": []
        }
    ranges = [get_scoresheet_values(name) for name in writers]
    scoresheet_list = [batch_get_values(scores_id, ranges)]
    all_stats = scoresheet_anal(writers, scoresheet_list)
    values_batch_update(REGISTRY.statsheet_id(number), write_stats_json(writers, all_stats))
    return {
        "writers": writers,
        "statsheets": all_stats
        }

def get_combined_stats():
    combined_id = REGISTRY.combined()
    ids = REGISTRY._scoresheets
    writers_lists = [get_sheet_names(id) for id in ids]
    writers = writers_lists[0]
    for lst in writers_lists:
        if len(lst) < len(writers):
            writers = lst
    ranges = [get_scoresheet_values(name) for name in writers]
    room_sheets = [batch_get_values(id, ranges) for id in ids]
    all_stats = scoresheet_anal(writers, room_sheets, REGISTRY.rooms())
    values_batch_update(combined_id, write_stats_json(writers, all_stats))
    return {
        "writers": writers,
        "statsheets": all_stats
        }

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/addroom")
async def addroom(response: Response, id: str | None = None):
    response.headers['Access-Control-Allow-Origin'] = "*"
    REGISTRY.add_room(id)
    return {"new room number": REGISTRY.rooms()}

@app.get("/rooms")
async def rooms(response: Response):
    response.headers['Access-Control-Allow-Origin'] = "*"
    return {"rooms": REGISTRY.rooms()}

@app.get("/stats/{room_number}")
async def room_stats(room_number: int, response: Response):
    response.headers['Access-Control-Allow-Origin'] = "*"
    if room_number > REGISTRY.rooms():
        return HTTPException(404, "No room with that number exists")
    elif room_number == 0:
        return get_combined_stats()
    return get_room_stats(room_number)

@app.post("/submitpacket/{room}")
async def add_packet_results(room: int, writer: Annotated[str, Query(max_length=30)], results: Scoresheet, response: Response):
    response.headers['Access-Control-Allow-Origin'] = "*"
    response.status_code = 201
    if writer not in get_sheet_names(REGISTRY.scoresheet_id(room)):
        spreadsheet_batch_update(REGISTRY.scoresheet_id(room), [add_sheet(writer)])
        spreadsheet_batch_update(REGISTRY.statsheet_id(room), [add_sheet(writer)])
    if writer not in get_sheet_names(REGISTRY.combined()):
        spreadsheet_batch_update(REGISTRY.combined(), [add_sheet(writer)])
    values_batch_update(REGISTRY.scoresheet_id(room), [write_scoresheet_json(writer, results)])
    return response

@app.post("/loadsheets")
async def load_sheets(ids: dict):
    """
    This call will load the ids of previously populated scoresheets and statsheets into the registry. For testing
    purposes or crash recovery.
    """
    REGISTRY._scoresheets = ids["scoresheets"]
    REGISTRY._statsheets = ids["statsheets"]
    REGISTRY._combined = ids["combined"]
    REGISTRY._rooms = len(ids["scoresheets"])
    return {"message": "success"}

@app.options("/submitpacket/{room}")
async def submit_preflight(room: int):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, GET, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': '*'
    }
    return Response(status_code=204, headers=headers)

if __name__ == "__main__":
    uvicorn.run("main:app", log_level="info", reload=True, host="10.117.5.224", port=8000)