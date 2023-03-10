"""
Microdot webserver for thermostat interface webpage
"""
# pylint: disable=unused-argument, broad-except, line-too-long
import json
import time
from lib.microdot_asyncio import Microdot, send_file, redirect
from common import SETTINGS_FILE, WEBSERVER_PORT, LOG_FILE
from utils import AppVars, load_json, save_schedule, adjusted_time, formatted_date


app = Microdot()


@app.route("/")
async def index_route(request):
    """redirect index route"""
    return redirect("/t/index.html")


@app.route("/schedule.json")
async def schedule_route(request):
    """Serve heating_schedule.json"""
    data = load_json(SETTINGS_FILE)
    return json.dumps(data), {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
    }


@app.route("/sensor.json")
async def readsensor(request):
    """Serve sensor readings as json"""
    obj = {
        "formatted_date": formatted_date(adjusted_time()),
        "time": time.time(),
        "temp": AppVars.curr_temp.value,
        "humidity": AppVars.curr_hum.value,
        "target_temp": AppVars.target_temp.value,
        "manual_temp": AppVars.manual_temp.value,
        "heater_state": AppVars.heater_state.value,
        "update_trigger": AppVars.update_trigger,
        "use_schedule": AppVars.use_heatschedule.value,
    }
    return json.dumps(obj), {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
    }


# @app.route("/log.csv")
# async def log(request):
#     """Serve log.csv"""
#     res = ""
#     with open(LOG_FILE, "r") as f:
#         res = f.read()
#     return {res, }

@app.route("/log.csv")
async def log(request):
    return send_file(LOG_FILE, {
        "Content-Type": "text/csv",
        "Access-Control-Allow-Origin": "*",
    })


@app.route("/set_temp", methods=["POST"])
async def set_temp(request):
    """Post request to set target temperature"""
    msg = json.dumps(request.json)
    print(f"/set_temp, msg: {msg}")
    AppVars.manual_temp.set(float(msg))
    # client.publish('esp32/target', msg, retain=True)
    return json.dumps({"success": True}), {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
    }


@app.route("/schedule_update", methods=["POST"])
async def schedule_update(request):
    """Post request to update schedule"""
    print("schedule_update route ---")
    print(f"{request}")
    try:
        AppVars.use_heatschedule.set(
            request.json["use_heatschedule"]
            if request.json["use_heatschedule"]
            else False
        )
        save_schedule(SETTINGS_FILE, request.json)
        print(f'request.json["use_heatschedule"]: {request.json["use_heatschedule"]}')
    except Exception as e:
        print(f"/schedule_update --- Error: {e}")
    # return 'OK', 202
    return json.dumps({"success": True}), {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
    }


@app.route("/t")
def alpine_index(request):
    """redirect alpine index route"""
    return redirect("/alpine/index.html")


@app.route("/t/<path:path>")
def thermostat(request, path):
    """Serve svelte frontend"""
    time.sleep_ms(100)
    return send_file("/sd/web/" + path)


def webserver_start():
    """Start webserver"""
    app.run(port=WEBSERVER_PORT)
