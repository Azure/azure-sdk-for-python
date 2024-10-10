class Transport:
    def __init__(self, callback function(frame_bytes)):
        pass

    def _loop():
        # start up receiving and sending loops.
        pass

    def write(frame_bytes):
        pass


still need keep alive thread as background thread to keep connection alive -- self.remote_idle_timeout is just for keep_alive level


what is connection's actual interface


thread 1:
    transport -> frame
    connection._process_incoming_frame(payload)
       gets receiver, calls receiver._incoming_transfer() 
        -> process_incoming_message(message)           <- this blocks the entire transport

Go's

thread 1:
   connreader() -> loop over connection, reading bytes
     frame parser -> into a channel for each link (queues)

thread2: receiver
   mux()  
    (blocks) -> read frame from queue
    dispatches frame - transfer etc

thread3: sender  -> read from queue


threadB
   block reading from queue.get()
threadA: pushes something onto queeu()

