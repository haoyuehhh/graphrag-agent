import multiprocessing

bind = "0.0.0.0:8000"
workers = 1  # LangGraph 有状态，多 worker 需共享 checkpointer
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
keepalive = 2
accesslog = "-"
errorlog = "-"
loglevel = "info"