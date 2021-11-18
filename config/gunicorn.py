from os import environ
from multiprocessing import cpu_count
# -*- coding: utf-8 -*-

bind = f"0.0.0.0:{environ.get('SERVER_PORT')}"
accesslog = "-"
timeout = 10000
workers = cpu_count()
access_log_format = (
    '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" in %(D)sµs'
)
