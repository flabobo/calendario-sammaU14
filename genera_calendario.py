#!/usr/bin/env python3
"""Genera un calendario ICS per Samma Under 14 da bootstrap JSON."""
import argparse
import json
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

TEAM = 'rom-93788-samma-under-14'

def esc(value):
    return str(value).replace('\\', '\\\\').replace('\n', '\\n').replace(',', '\\,').replace(';', '\\;')

def fold(line):
    # RFC 5545: max 75 octets per line; continuations start with one space.
    chunks=[]; current=''; n=0
    for c in line:
        b=len(c.encode('utf-8'))
        if n+b > 75:
            chunks.append(current); current=' '; n=1
        current+=c; n+=b
    chunks.append(current)
    return '\r\n'.join(chunks)

def read_json(source):
    if source.startswith(('https://', 'http://')):
        with urllib.request.urlopen(source, timeout=30) as response:
            return json.load(response)
    return json.loads(Path(source).read_text(encoding='utf-8'))

def make_ics(data):
    now=datetime.fromisoformat(data['aggiornato'].replace('Z','+00:00')).astimezone(timezone.utc).strftime('%Y%m%dT%H%M%SZ') if data.get('aggiornato') else datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    lines=['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//Samma//Under14 Fixtures//IT','CALSCALE:GREGORIAN','METHOD:PUBLISH','X-WR-CALNAME:Samma Under 14 - Gare','X-WR-TIMEZONE:Europe/Rome','REFRESH-INTERVAL;VALUE=DURATION:PT6H','X-PUBLISHED-TTL:PT6H']
    games=[m for group in data['gironi'] for m in group.get('gare',[]) if TEAM in (m.get('casa'),m.get('ospite')) and m.get('data_ora')]
    for m in sorted(games,key=lambda g:g['data_ora']):
        start=datetime.fromisoformat(m['data_ora'])
        end=start+timedelta(hours=2)
        venue=data.get('palestre',{}).get(str(m.get('palestra')), {})
        home=data['squadre'].get(m['casa'],{}).get('nome',m['casa'])
        away=data['squadre'].get(m['ospite'],{}).get('nome',m['ospite'])
        place=', '.join(filter(None,[venue.get('nome'),venue.get('indirizzo'),venue.get('citta')]))
        description='Giornata: '+str(m.get('giornata',''))+'\\nGara n.: '+str(m.get('numero',''))+'\\nStato: '+str(m.get('stato_fonte',m.get('stato','')))
        if venue.get('maps'):
            description+='\\nGoogle Maps: '+venue['maps']
        lines+=['BEGIN:VEVENT','UID:'+esc(m['id']+'@samma-under14-calendar'),'DTSTAMP:'+now,
                'DTSTART:'+start.astimezone(timezone.utc).strftime('%Y%m%dT%H%M%SZ'),
                'DTEND:'+end.astimezone(timezone.utc).strftime('%Y%m%dT%H%M%SZ'),
                'SUMMARY:'+esc(home+' - '+away),'LOCATION:'+esc(place),
                'DESCRIPTION:'+esc(description.replace('\\n','\n')),
                'STATUS:'+('CANCELLED' if m.get('stato') in ('annullata','annullato','cancelled') else 'CONFIRMED'),
                'END:VEVENT']
    lines+=['END:VCALENDAR']
    return '\r\n'.join(fold(s) for s in lines)+'\r\n',len(games)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source',required=True,help='File JSON locale o URL completo /api/v1/bootstrap')
    parser.add_argument('--output',default='samma-under14.ics')
    args=parser.parse_args()
    text,count=make_ics(read_json(args.source))
    if not count: raise SystemExit('Nessuna gara trovata: verificare fonte JSON')
    Path(args.output).write_bytes(text.encode('utf-8'))
    print(f'Creato {args.output} con {count} gare')

if __name__=='__main__':main()
