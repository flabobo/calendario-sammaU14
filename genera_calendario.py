#!/usr/bin/env python3
"""Calendario Samma U14 da pagina pubblica FIPAV Romagna."""
import argparse
import re
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup

URL = 'https://www.fipavromagna.it/pagina-resp.aspx?PId=17043&ComitatoId=75&stagioneId=2455&campionatoId=93788'
TEAM = 'SAMMA UNDER 14'
ROME = ZoneInfo('Europe/Rome')

def escape(value):
    return str(value).replace('\\','\\\\').replace('\n','\\n').replace(',','\\,').replace(';','\\;')

def fold(line):
    parts=[]; chunk=''; size=0
    for c in line:
        b=len(c.encode('utf-8'))
        if size+b>75:
            parts.append(chunk);chunk=' ';size=1
        chunk+=c;size+=b
    return '\r\n'.join(parts+[chunk])

def get_html(source):
    if source.startswith(('https://','http://')):
        req=urllib.request.Request(source,headers={'User-Agent':'Mozilla/5.0 (compatible; SammaCalendar/1.0)','Accept':'text/html'})
        with urllib.request.urlopen(req,timeout=40) as r:
            return r.read().decode('utf-8-sig',errors='replace')
    return Path(source).read_text(encoding='utf-8-sig')

def parse(html):
    soup=BeautifulSoup(html,'html.parser')
    table=soup.select_one('table.gare-tab')
    if table is None:
        raise ValueError('Tabella delle gare FIPAV non trovata: formato pagina cambiato')
    rows=table.select('tr'); games=[]
    for idx,row in enumerate(rows):
        date_cell=row.select_one('td.dataOra')
        if not date_cell: continue
        names=[el.get_text(' ',strip=True) for el in row.select('.tb-team-1 h6,.tb-team-2 h6')]
        if len(names)!=2 or TEAM not in names: continue
        header=date_cell.get_text(' ',strip=True)
        match=re.search(r'G\.(\d+)\s*-\s*Gara\s*n\.\s*(\d+)\s+(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2})',header,re.I)
        if not match: raise ValueError(f'Data/numero gara non leggibili: {header}')
        day,number,date,hour=match.groups()
        start=datetime.strptime(date+' '+hour,'%d/%m/%Y %H:%M').replace(tzinfo=ROME)
        details=rows[idx+1] if idx+1<len(rows) and 'other-info' in rows[idx+1].get('class',[]) else None
        if details is None: raise ValueError(f'Dettagli palestra mancanti per gara {number}')
        venue_el=details.select_one('.imp-des b')
        address_el=details.select_one('.imp-des a')
        venue=venue_el.get_text(' ',strip=True) if venue_el else ''
        address=address_el.get_text(' ',strip=True) if address_el else ''
        maps=address_el.get('href','') if address_el else ''
        status_el=details.select_one('p.stato')
        status=status_el.get_text(' ',strip=True) if status_el else ''
        id_el=row.select_one('[id^="Risultato_Casa_"]')
        game_id=id_el.get('id','').split('_')[-1] if id_el else number
        games.append(dict(id=game_id,number=number,day=day,start=start,home=names[0],away=names[1],venue=venue,address=address,maps=maps,status=status))
    if len(games)<1: raise ValueError('Nessuna partita Samma Under 14 trovata: non sovrascrivo il calendario')
    if len({g['id'] for g in games})!=len(games): raise ValueError('Identificativi gara duplicati')
    return sorted(games,key=lambda g:g['start'])

def generate(games):
    now=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    lines=['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//Samma//Under14 FIPAV//IT','CALSCALE:GREGORIAN','METHOD:PUBLISH','X-WR-CALNAME:Samma Under 14 - Gare','X-WR-TIMEZONE:Europe/Rome','REFRESH-INTERVAL;VALUE=DURATION:PT6H','X-PUBLISHED-TTL:PT6H']
    for g in games:
        start=g['start'].astimezone(timezone.utc)
        end=(g['start']+timedelta(hours=2)).astimezone(timezone.utc)
        description=f"Giornata: {g['day']}\nGara n.: {g['number']}\nStato: {g['status']}"
        if g['maps']: description+='\nGoogle Maps: '+g['maps']
        description+='\nFonte: '+URL
        lines += ['BEGIN:VEVENT','UID:'+escape('rom-'+g['id']+'@samma-under14-calendar'),'DTSTAMP:'+now,
                  'DTSTART:'+start.strftime('%Y%m%dT%H%M%SZ'),'DTEND:'+end.strftime('%Y%m%dT%H%M%SZ'),
                  'SUMMARY:'+escape(g['home']+' - '+g['away']),
                  'LOCATION:'+escape(', '.join(filter(None,[g['venue'],g['address']]))),
                  'DESCRIPTION:'+escape(description),
                  'STATUS:'+('CANCELLED' if 'annullat' in g['status'].lower() else 'CONFIRMED'),
                  'END:VEVENT']
    lines.append('END:VCALENDAR')
    return '\r\n'.join(map(fold,lines))+'\r\n'

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',default=URL,help='URL FIPAV oppure file HTML locale')
    ap.add_argument('--output',default='samma-under14.ics')
    args=ap.parse_args()
    games=parse(get_html(args.source))
    Path(args.output).write_bytes(generate(games).encode('utf-8'))
    print(f'Calendario aggiornato: {len(games)} gare Samma Under 14')

if __name__=='__main__': main()
