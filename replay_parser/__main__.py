from io import BytesIO, FileIO, StringIO
import os
import base64
import json
import zlib

from constants import CommandStates
from body import ReplayBody
from reader import ReplayReader
from replay import continuous_parse, parse

def get_scfa_replay_by_data(data: bytes):
    """
    FAF and Supreme Commander has 2 kind of formats:
    1. scfareplay - that is simple binary stuff
    2. fafreplay - it's zlib compressed scfareplay data with json header
    """
    try:
        stream = StringIO(data.decode())
        header = stream.readline().strip()

        if json.loads(header):
            body = stream.read().strip()
            return zlib.decompress(base64.b64decode(body)[4:])
    except:
        pass

    return data

file = open("D:/11052825.fafreplay", "rb").read()

scfa = get_scfa_replay_by_data(file)

data = parse(
        scfa,
        True,
        parse_commands={
            CommandStates.Advance,
            CommandStates.SetCommandSource,
            CommandStates.CommandSourceTerminated,
            CommandStates.VerifyChecksum,
            CommandStates.LuaSimCallback,
            CommandStates.IssueCommand,
        }
    )

for bd in data['body']:
    print(bd)
    print("------------------------------------------------------------------------------------")