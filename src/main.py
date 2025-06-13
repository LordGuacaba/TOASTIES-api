"""
API for requests from the TOASTIES.
"""

from typing import Annotated

from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import Response

from actions.registry import Registry
from actions.sheets import *
from utils.anal import *
from utils.sheet_updates import *
from utils.types import Scoresheet

app = FastAPI()
registry = Registry()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/addroom")
async def addroom(response: Response, id: str | None = None):
    response.headers['Access-Control-Allow-Origin'] = "http://localhost:3000"
    registry.add_room(id)
    return {"new room number": registry.rooms()}

@app.get("/rooms")
async def rooms(response: Response):
    response.headers['Access-Control-Allow-Origin'] = "http://localhost:3000"
    return {"rooms": registry.rooms()}

@app.get("/roomstats/{room_number}")
async def room_stats(room_number: int, response: Response):
    response.headers['Access-Control-Allow-Origin'] = "http://localhost:3000"
    if room_number > registry.rooms():
        return HTTPException(404, "No room with that number exists")
    scores_id = registry.scoresheet_id(room_number)
    writers = get_sheet_names(scores_id)
    ranges = [get_scoresheet_values(name) for name in writers]
    scoresheet_list = [batch_get_values(scores_id, ranges)]
    all_stats = scoresheet_anal(writers, scoresheet_list)
    values_batch_update(registry.statsheet_id(room_number), write_stats_json(writers, all_stats))
    return {
        "writers": writers,
        "statsheets": all_stats
        }

@app.get("/combined")
async def combined_stats(response: Response):
    response.headers['Access-Control-Allow-Origin'] = "http://localhost:3000"
    combined_id = registry.combined()
    ids = registry._scoresheets
    writers = get_sheet_names(ids[0])
    ranges = [get_scoresheet_values(name) for name in writers]
    room_sheets = [batch_get_values(id, ranges) for id in ids]
    all_stats = scoresheet_anal(writers, room_sheets)
    values_batch_update(combined_id, write_stats_json(writers, all_stats))
    return {
        "writers": writers,
        "statsheets": all_stats
        }

@app.post("/submitpacket/{room}")
async def add_packet_results(room: int, writer: Annotated[str, Query(max_length=30)], results: Scoresheet, response: Response):
    response.headers['Access-Control-Allow-Origin'] = "http://localhost:3000"
    response.status_code = 201
    spreadsheet_batch_update(registry.scoresheet_id(room), [add_sheet(writer)])
    spreadsheet_batch_update(registry.statsheet_id(room), [add_sheet(writer)])
    values_batch_update(registry.scoresheet_id(room), [write_scoresheet_json(writer, results)])
    return response

@app.options("/submitpacket/{room}")
async def submit_preflight(room: int):
    headers = {
        'Access-Control-Allow-Origin': 'http://localhost:3000',
        'Access-Control-Allow-Methods': 'POST, GET, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': '*'
    }
    return Response(status_code=204, headers=headers)