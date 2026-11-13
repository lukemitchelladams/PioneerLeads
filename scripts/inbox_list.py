"""Read-only inbox listing through the local Gmail token (fallback when the Gmail connector is down).
Usage: python3 scripts/inbox_list.py [gmail search query]   (default: newer_than:1h -from:luke@brownbisonco.com)
Prints date, from, subject, thread id and snippet. Never sends, labels or deletes anything."""
import sys, json, urllib.parse, datetime as dt
sys.path.insert(0, "/home/user/PioneerLeads/scripts")
import gmail_api as g
q = sys.argv[1] if len(sys.argv) > 1 else 'newer_than:1h -from:luke@brownbisonco.com'
tok = g.access_token()
res = g.call("GET", "/gmail/v1/users/me/messages?maxResults=40&q=" + urllib.parse.quote(q), tok)
msgs = res.get("messages", []) or []
print(f"{len(msgs)} message(s) for q={q!r}")
for m in msgs:
    d = g.call("GET", f"/gmail/v1/users/me/messages/{m['id']}?format=metadata&metadataHeaders=From&metadataHeaders=Subject&metadataHeaders=Date&metadataHeaders=To", tok)
    h = {x["name"].lower(): x["value"] for x in d["payload"]["headers"]}
    ts = dt.datetime.fromtimestamp(int(d["internalDate"]) / 1000, dt.timezone.utc).strftime("%m-%d %H:%MZ")
    print(f"- {ts} | {h.get('from','?')[:60]} | {h.get('subject','?')[:80]} | thr {d['threadId']}")
    print(f"    {d.get('snippet','')[:160]}")
