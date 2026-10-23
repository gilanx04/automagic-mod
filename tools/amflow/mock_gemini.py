#!/usr/bin/env python3
"""Server Gemini tiruan untuk menguji agent tanpa API key sungguhan.

Menirukan: key pertama kena limit (429), key kedua berhasil, fase 1 mengembalikan
JSON komponen, fase 2 mengembalikan XML yang sengaja salah dulu (untuk menguji
perbaikan otomatis), lalu XML yang benar.
"""
from __future__ import annotations

import json
import re
from http.server import BaseHTTPRequestHandler, HTTPServer

GOOD_XML = """<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<data version="1.38.0">
  <flow type="flow">
    <name>Status Pagi</name>
    <group>Custom</group>
    <enabled>false</enabled>
    <lastExecutionStartTime>0</lastExecutionStartTime>
    <lastExecutionEndTime>0</lastExecutionEndTime>
    <executionPolicy>PARALLEL</executionPolicy>
    <triggercontainer id="t1" x="70.0" y="120.0">
      <trigger>Pagi</trigger>
    </triggercontainer>
    <actioncontainer id="t2" x="70.0" y="300.0">Post Status</actioncontainer>
    <connection from="t1" to="t2" type="NORMAL" sourcePosition="SOUTH" targetPosition="NORTH" />
  </flow>
  <trigger type="time">
    <useDefaultName>false</useDefaultName>
    <name>Pagi</name>
    <enabled>true</enabled>
    <weekday>Mon</weekday>
    <hour>7</hour>
    <minute>0</minute>
    <second>0</second>
    <allowInDeviceIdle>true</allowInDeviceIdle>
    <likeAlarmClock>false</likeAlarmClock>
  </trigger>
  <action type="wa_status">
    <useDefaultName>false</useDefaultName>
    <name>Post Status</name>
    <text>Selamat pagi</text>
  </action>
</data>"""

BAD_XML = """<data version="1.38.0">
  <flow type="flow">
    <name>Status Pagi</name>
    <group>Custom</group>
    <enabled>false</enabled>
    <executionPolicy>PARALLEL</executionPolicy>
    <triggercontainer id="t1" x="70.0" y="120.0"><trigger>Pagi</trigger></triggercontainer>
    <actioncontainer id="t2" x="70.0" y="300.0">Post Status</actioncontainer>
    <connection from="t1" to="t9" type="NORMAL" />
  </flow>
  <trigger type="time"><name>Pagi</name><enabled>true</enabled><hour>7</hour></trigger>
  <action type="wa_status"><name>Post Status</name><text>Selamat pagi</text></action>
</data>"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_POST(self):
        key = self.headers.get("x-goog-api-key", "")
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        prompt = body["contents"][0]["parts"][0]["text"]

        if key.startswith("limit"):
            self._send(429, {"error": {"message": "Resource has been exhausted (quota)"}})
            return

        if "Balas HANYA JSON" in prompt:
            text = json.dumps({"trigger": ["time"], "condition": [],
                               "action": ["wa_status"]})
        elif "tidak valid" in prompt:
            text = "```xml\n" + GOOD_XML + "\n```"
        else:
            text = "```xml\n" + BAD_XML + "\n```"

        self._send(200, {"candidates": [{"content": {"parts": [{"text": text}]}}]})

    def _send(self, code, payload):
        raw = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", 8099), Handler).serve_forever()
