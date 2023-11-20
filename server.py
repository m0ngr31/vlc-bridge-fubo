import sys
import os
import importlib
from flask import Flask, request, redirect
from gevent.pywsgi import WSGIServer

app = Flask("vlc-bridge")
name = os.environ['PROVIDER']
providers = {
    name: importlib.import_module(name).Client(),
}

@app.get('/')
def index():
    host = request.host
    ul = ""
    for p in providers:
        pl = f"http://{host}/{p}/playlist.m3u"
        ul += f"<li>{p.upper()}: <a href='{pl}'>{pl}</a></li>\n"

    return f"<h1>Playlist</h1>\n<ul>\n{ul}</ul>"

@app.get("/<provider>/playlist.m3u")
def playlist(provider):
    host = request.host
    stations, err = providers[provider].channels()
    if err is not None:
        return err, 500
    m3u = "#EXTM3U\r\n\r\n"
    for s in stations:
        m3u += f"#EXTINF:-1 channel-id=\"{s.get('id')}\""
        m3u += f" tvg-id=\"{s.get('call_sign')}\""
        group = s.get('group')
        if group is not None:
            m3u += f" group-title=\"{';'.join(map(str, group))}\""
        logo = s.get('logo')
        if logo is not None:
            m3u += f" tvg-logo=\"{logo}\""
        gracenoteId = s.get('gracenoteId')
        if gracenoteId is not None:
            m3u += f" tvc-guide-stationid=\"{gracenoteId}\""
        else:
            # print(f"Using Fubo ID {s.get('id')} as StationID for {s.get('name')}" )
            m3u += f" tvc-guide-stationid=\"{s.get('id')}\""            

        timeShift = s.get('timeShift')
        if timeShift is not None:
            m3u += f" tvg-shift=\"{timeShift}\""
        m3u += f",{s.get('name') or s.get('call_sign')}\n"
        m3u += f"http://{host}/{provider}/watch/{s.get('watchId') or s.get('id')}\n\n"
    return m3u

@app.get("/<provider>/watch/<id>")
def watch(provider, id):
    pl, err = providers[provider].watch(id)
    if err is not None:
        return "Error", 500, {'X-Tuner-Error': err}
    return redirect(pl)

if __name__ == '__main__':
    sys.stdout.write("⇨ http server started on [::]:7777\n")
    try:
        WSGIServer(('', 7777), app, log=None).serve_forever()
    except OSError as e:
        print(str(e))