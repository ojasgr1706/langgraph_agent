# from app.graph.state import State

class Session():
    def __init__(self, thread_id):
        self.threads = {}
        self.cur_thread = 1
        
    def add_thread(self, thread_id, name):
        self.threads[thread_id] = name

    def thread_exists(self, thread_id):
        return thread_id in self.threads

    def is_empty(self):
        return not len(self.threads)

    def set_thread(self, thread_id):
        self.cur_thread = thread_id

    def __str__(self):
        if self.threads:
            for thread_id,name in self.threads.items():
                print(f"{thread_id} -- {name}")
        else:
            print("No chats to show yet")