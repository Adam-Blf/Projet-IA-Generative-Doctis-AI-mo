import multiprocessing

bind = "0.0.0.0:10000"
workers = 1              # Reduced to 1 to fit SBERT model in 512MB RAM (Free Tier)
threads = 4              # Use threads for concurrency instead of processes
timeout = 180            # Extended timeout for Slower Cold Starts
accesslog = "-"
errorlog = "-"
loglevel = "info"
