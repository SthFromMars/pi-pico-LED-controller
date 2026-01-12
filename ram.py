import gc, time

def ram_log():
    while True:
        gc.collect()
        print("Free RAM:", gc.mem_free())
        time.sleep(1)