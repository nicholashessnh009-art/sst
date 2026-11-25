from app import collect_all, DB
import datetime
import os
import sqlite3
from contextlib import redirect_stdout

LOG = os.path.join(os.path.dirname(__file__), "cscript_log.txt")
# coletor de dados de todos os users
# executado pelo Agendador de Tarefas do Windows (no meu pc) a cada 2 horas pra coletar dados, pfvr ignore
def count_plays():
    conn = sqlite3.connect(DB)
    number = conn.execute('SELECT COUNT(*) FROM plays').fetchone()[0]
    conn.close()
    return number

with open(LOG, "a", encoding="utf-8") as log:
    with redirect_stdout(log): 
        time_now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        try:
            before_count = count_plays()
            collect_all()
            after_count = count_plays()
            print(f"[{time_now}] Coleta concluída. {after_count - before_count} novos plays. total: {after_count}")
        except Exception as e:
            print(f"[{time_now}] Erro durante a coleta: {e}")




