from .future import Future
from .connection import Connection

class Task(Future):

    fut_reference = [] # used to synchronize tasks in between print statements

    def __init__(self, loop, coro=None):
        super().__init__()
        self.loop = loop
        self.coro = coro # some tasks run coros and some tasks gather tasks
        self.fut_result = {} # used to set results of fut that were not set after await somehow
        self.results = []
        self.unfinished_futures = [] # keep track of unfinished futures to avoid unfinished results

    async def gather_tasks(self,*tasks):
        """
            gather connections and tasks
            This task could be inside another task
        """
        futures = []
        for task in tasks:
            if isinstance(task,Task):
                futures.append(task)
            elif isinstance(task,Connection):
                fut = self.loop.add_connection(task, in_gather=True)
                futures.append(fut)
        if isinstance(tasks[-1],Task):
            Task.fut_reference.append(tasks[-1])
        elif isinstance(tasks[-1],Connection):
            Task.fut_reference.append(tasks[-1].fut)
        responses = [await fut for fut in futures]
        for index,response in enumerate(responses):
            if isinstance(response,Future):
                responses[index] = response.result  # set the result of futures that were somewhat not set
        self.set_result(responses)

    def start(self):
        """
            runs task without blocking
        """
        if self.coro:
            try:
                while True:
                    fut = self.coro.send(None)
                    fut.unblocking_task = self
                    self.unfinished_futures.append(fut)
                    if fut in Task.fut_reference:
                        Task.fut_reference.remove(fut)
                        break # pause continuation of task until the previous futures are set
            except StopIteration as e:
                self.set_unblocking_task_result(e.value)

    def update_progress(self,fut,result):
        self.unfinished_futures.remove(fut)
        self.fut_result[fut] = result # store the futures to results
        if len(self.unfinished_futures) == 0: # all futures/tasks are completed
            self.start() # continue task after previous await statement in task


    def set_unblocking_task_result(self,values):
        if isinstance(values, list):
            if all(isinstance(value, Future) for value in values):
                for fut in values:
                    if isinstance(fut, Future):
                        self.results.append(self.fut_result[fut])
                    else:
                        self.results.append(fut)  # fut already has a value
                self.set_result(self.results)
            else:
                self.set_result(values)
        else:
            self.set_result(values)