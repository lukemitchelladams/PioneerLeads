# Gmail API setup: lets the agent send attachments and read attachments itself

Why: the Gmail connector can't carry multi-MB files, and SMTP is blocked in cloud sessions. gmail.googleapis.com
over HTTPS works (tested 2026-10-28). `scripts/gmail_api.py` sends with attachments and saves incoming attachments.

One time, about 10 minutes, on Luke's Mac:

1. console.cloud.google.com, signed in as luke@brownbisonco.com. Create project "Brown Bison Mail".
2. APIs & Services > Library > "Gmail API" > Enable.
3. APIs & Services > OAuth consent screen > User type **Internal** (Workspace, so no Google review) > app name
   "Brown Bison Mail" > save.
4. APIs & Services > Credentials > Create credentials > OAuth client ID > Application type **Desktop app** >
   Create > Download JSON (client_secret_....json).
5. In Terminal, in the PioneerLeads folder:
   `python3 -m pip install google-auth-oauthlib && python3 scripts/gmail_api.py token ~/Downloads/client_secret_*.json`
   A browser opens; approve. It prints GMAIL_CLIENT_ID and GMAIL_REFRESH_TOKEN. The secret is in the JSON.
6. Cloud environment settings (session title bar > environment > Edit) > environment variables / secrets: add
   `GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET`, `GMAIL_REFRESH_TOKEN`. Never paste them in chat.
7. New session: `python3 scripts/gmail_api.py check` prints luke@brownbisonco.com when it works.
