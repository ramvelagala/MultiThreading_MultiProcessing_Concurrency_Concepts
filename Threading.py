"""Threading Concepts."""
"https://realpython.com/intro-to-python-threading/#what-is-a-thread"

"""
Questions in never understood.
    1)Executor.map vs Executor.submit
"""

import concurrent.futures
import logging
import threading
import time

"To start a separate thread, you create a Thread instance and then tell it to .start():"


def thread_function(name):
    logging.info("Thread %s: started", name)
    time.sleep(10)
    logging.info("Thread %s: finished", name)


# if __name__ == "__main__":
#     format = "%(asctime)s: %(message)s"
#     logging.basicConfig(format=format, level=logging.INFO,
#                         datefmt="%H:%M:%S")
#
#     logging.info("Main    : before creating thread")
#     x = threading.Thread(target=thread_function, args=(1,))
#     logging.info("Main    : before running thread")
#     x.start()
#     logging.info("Main    : wait for the thread to finish")
#     # x.join()
#     logging.info("Main    : all done")

"""x = threading.Thread(target=thread_function, args=(1,))
x.start()* """

"""
07:29:48: Main    : before creating thread
07:29:48: Main    : before running thread
07:29:48: Thread 1: started
07:29:48: Main    : wait for the thread to finish
07:29:48: Main    : all done
07:29:51: Thread 1: finished

This is the output which is weird.
"""

"Now lets look at how we can overcome this by .join()"
"To tell one thread to wait for another thread to finish, you call .join(). If you uncomment that line, the main thread will pause and wait for the thread x to complete running."

# if __name__ == "__main__":
#     format = "%(asctime)s: %(message)s"
#     logging.basicConfig(format=format, level=logging.INFO,
#                         datefmt="%H:%M:%S")
#
#     threads = list()
#     for index in range(3):
#         logging.info("Main    : create and start thread %d.", index)
#         x = threading.Thread(target=thread_function, args=(index,))
#         threads.append(x)
#         x.start()
#
#     for index, thread in enumerate(threads):
#         logging.info("Main    : before joining thread %d.", index)
#         thread.join()
#         logging.info("Main    : thread %d done", index)

"""08:09:35: Thread 1: started
08:09:35: Main    : create and start thread 2.
08:09:35: Thread 2: started
08:09:35: Main    : before joining thread 0.
08:09:45: Thread 0: finished
08:09:45: Thread 2: finished
08:09:45: Thread 1: finished
08:09:45: Main    : thread 0 done
08:09:45: Main    : before joining thread 1.
08:09:45: Main    : thread 1 done
08:09:45: Main    : before joining thread 2.
08:09:45: Main    : thread 2 done

This is the output which is also weird, but solved the threads not executing before main thread.
"""

"The order in which threads are run is determined by the operating system and can be quite hard to predict. It may (and likely will) vary from run to run, so you need to be aware of that when you design algorithms that use threading."

# if __name__ == "__main__":
#     format = "%(asctime)s: %(message)s"
#     logging.basicConfig(format=format, level=logging.INFO,
#                         datefmt="%H:%M:%S")
#
#     with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
#         executor.map(thread_function, range(3))


"""08:19:27: Thread 0: started
08:19:27: Thread 1: started
08:19:27: Thread 2: started
08:19:37: Thread 1: finished
08:19:37: Thread 2: finished
08:19:37: Thread 0: finished

this also didn't solve, it is strongly recommneded to use ThreadPoolExecutor as a context manager when you can so that you never forget to .join() the threads.
"""

# class FakeDatabase:
#     def __init__(self):
#         self.value = 0
#
#     def update(self, name):
#         logging.info("Thread %s: starting update", name)
#         local_copy = self.value
#         logging.info("starting thread %s Value: %s", name,self.value)
#         local_copy += 1
#         time.sleep(0.1)
#         self.value = local_copy
#         logging.info("finishing thread %s Value: %s", name,self.value)
#         logging.info("Thread %s: finishing update", name)

# if __name__ == "__main__":
#     format = "%(asctime)s: %(message)s"
#     logging.basicConfig(format=format, level=logging.INFO,
#                         datefmt="%H:%M:%S")
#
#     database = FakeDatabase()
#     logging.info("Testing update. Starting value is %d.", database.value)
#     with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
#         for index in range(2):
#             executor.submit(database.update, index)
#     logging.info("Testing update. Ending value is %d.", database.value)

"the two threads will be running concurrently but not at the same time. They will each have their own version of local_copy and will each point to the same database. It is this shared database object that is going to cause the problems."

"To resolve this we will be using lock, it is also called MUTEX (mutal exclusion) in some other langauges."


class FakeDatabase:
    def __init__(self):
        self.value = 0
        self._lock = threading.Lock()

    def locked_update(self, name):
        logging.info("Thread %s: starting update", name)
        logging.debug("Thread %s about to lock", name)
        with self._lock:
            logging.debug("Thread %s has lock", name)
            local_copy = self.value
            local_copy += 1
            time.sleep(0.1)
            self.value = local_copy
            logging.debug("Thread %s about to release lock", name)
        logging.debug("Thread %s after release", name)
        logging.info("Thread %s: finishing update", name)


if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.DEBUG,
                        datefmt="%H:%M:%S")

    database = FakeDatabase()
    logging.info("Testing update. Starting value is %d.", database.value)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        for index in range(2):
            executor.submit(database.locked_update, index)
    logging.info("Testing update. Ending value is %d.", database.value)

"""
14:04:41: Testing update. Starting value is 0.
14:04:41: Thread 0: starting update
14:04:41: Thread 0 about to lock
14:04:41: Thread 0 has lock
14:04:41: Thread 1: starting update
14:04:41: Thread 1 about to lock
14:04:42: Thread 0 about to release lock
14:04:42: Thread 0 after release
14:04:42: Thread 1 has lock
14:04:42: Thread 0: finishing update
14:04:42: Thread 1 about to release lock
14:04:42: Thread 1 after release
14:04:42: Thread 1: finishing update
14:04:42: Testing update. Ending value is 2.
"""

"In this output you can see Thread 0 acquires the lock and is still holding it when it goes to sleep. Thread 1 then starts and attempts to acquire the same lock. Because Thread 0 is still holding it, Thread 1 has to wait. This is the mutual exclusion that a Lock provides."


"Deadlock: Deadlock occurs when concurrent modules are stuck waiting for each other to do something. A deadlock may involve more than two modules: the signal feature of deadlock is a cycle of dependencies, e.g. A is waiting for B which is waiting for C which is waiting for A. None of them can make progress."


"Producer-Consumer Threading."