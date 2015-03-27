# coding=utf8

from subprocess import Popen, PIPE
from threading import Thread
try:
    from queue import Queue, Empty
except ImportError:
    from Queue import Queue, Empty

import sublime
import os
import time

from ..display.Message import MESSAGE

from ..utils import encode, Debug
from ..utils.pathutils import get_tss_path, find_tsconfigdir, default_node_path
from ..utils.osutils import get_kwargs
from ..utils.disabling import set_plugin_temporarily_disabled


#    PROCESSES = global Processes() instance
#     |
#     |_____has 2 TssJsStarterProcess
#     |     (1 for slow and 1 for fast commands)
#     |     for each project root
#     |
#    TssJsStarterThread()------->starts>         tss.js
#           |               |                      | | stdin stdout pipes
#           |               ---->starts>         TssAdapterThread (does debouncing and command reordering)
#           |                                      | |
#           --sending AsyncCommand() instances---->| |----> sublime.set_timeout(async_command.callback)
#               via synchronized Queue.Queue


# ----------------------------------------- PROCESSES ---------------------------------------- #

class Processes(object):
    """
        Keeps two tss.js Processes and adapters for each project root.
        Process SLOW is for slow commands like tss>errors which can last more than 5s easily.
        Process FAST is for fast reacting commands eg. for autocompletion or type.
    """

    def __init__(self, project):
        """ starts the two processes """
        self.project = project
        self.slow = None
        self.fast = None
        self.start_tss_processes()


    def is_initialized(self):
        """ Returns True if both processes (SLOW and FAST) have been started. """
        return self.slow.started and self.fast.started

    def get_initialisation_error_message(self):
        """ Returns Errormessage if initializing has failed, otherwise false"""
        if self.slow.error:
            return self.slow.error
        if self.fast.error:
            return self.fast.error
        return False

    def start_tss_processes(self):
        """
            Start tss.js (2 times).
            Displays message to user while starting and calls project.on_services_started() afterwards
        """
        Debug('notify', 'starting tsserver ' + self.project.tsconfigfile)
        self.slow = TssJsStarterThread(self.project)
        self.slow.start()

        self.fast = TssJsStarterThread(self.project)
        self.fast.start()

        self._wait_for_finish_and_notify_user()

    def kill(self):
        """ Trigger killing of adapter, tss.js and queue. """

        Debug('tss+', "Killing tss.js process and adapter thread (for slow and fast lane) (Closing project %s)"
                 % self.project.tsconfigfile)
        self.slow.kill_tssjs_queue_and_adapter()
        self.fast.kill_tssjs_queue_and_adapter()



    def _wait_for_finish_and_notify_user(self, i=1, dir=-1):
        """ Displays animated Message as long as TSS is initing. Is recoursive function. """

        if self.get_initialisation_error_message():
            sublime.error_message('Typescript initializion error for : %s\n >>> %s\n ArcticTypescript is disabled until you restart sublime.'
                         % (self.project.tsconfigfile, self.get_initialisation_error_message()))
            set_plugin_temporarily_disabled()
            return

        if not self.is_initialized():
            (i, dir) = self._display_animated_init_message(i, dir)
            # recursive:
            sublime.set_timeout(lambda: self._wait_for_finish_and_notify_user(i, dir), 100)
        else:
            # starting finished ->
            MESSAGE.show('Typescript project intialized for file : %s' % self.project.tsconfigfile, True, with_panel=False)
            self.project.on_services_started()

    def _display_animated_init_message(self, i, dir):
        if i in [1, 8]:
            dir *= -1
        i += dir
        anim_message = ' Typescript project is initializing [%s]' % '='.rjust(i).ljust(8)

        MESSAGE.repeat(anim_message, with_panel=False)

        return (i, dir)


# ----------------------------------------- THREAD: (tss.js and adapter starter) ------------------------ #

class TssJsStarterThread(Thread):
    """
        After starting, this class provides the methods and fields
            * send_async_command(...)
            * kill_tssjs_queue_and_adapter()
            * started
        for communication with the started Adapter and therewith the tss.js script.

        tss.js from: https://github.com/clausreinke/typescript-tools
    """
    def __init__(self, project):
        """ init for project <project> """
        self.project = project
        self.started = False
        self.error = False
        Thread.__init__(self)


    def run(self):
        """
            Starts the tss.js typescript services server process and the adapter thread.
        """

        node_path, cwd, cmdline = self._make_commandline()
        kwargs = get_kwargs(stderr=False)

        try:
            self.tss_process = Popen(cmdline,
                                     stdin=PIPE, stdout=PIPE, stderr=PIPE,
                                     cwd=cwd, **kwargs)

            Debug('tss', 'STARTED tss with: %s' % ' '.join(cmdline))

        except PermissionError as e:
            self.error = "\n".join(["PermissionError while starting typescript-tools.",
                    "I have tried this path: >%s<" % node_path,
                    "The total command is >%s<" % ' '.join(cmdline),
                    "The error message is >%s<" % e,
                    "If you are on windows and just have installed node, you first need to logout and login again."])
            return
        except FileNotFoundError:
            self.error = "\n".join(["Could not find nodejs.",
                    "I have tried this path: %s" % node_path,
                    "Please install nodejs and/or set node_path in the project or plugin settings to the actual executable.",
                    "If you are on windows and just have installed node, you first need to logout and login again."])
            return
        except Exception as e:
            self.error = "Unexpected Error while starting typescript-tools."
            print(e)
            return


        first_out = self.tss_process.stdout.readline()
        Debug('tss', 'FIRST TSS MESSAGE: %s' % first_out)

        self.check_process_health()

        self.tss_queue = Queue()
        self.tss_adapter = TssAdapterThread(self.tss_process.stdin,
                                              self.tss_process.stdout,
                                              self.tss_queue,
                                              self.check_process_health)
        self.tss_adapter.daemon = True
        self.tss_adapter.start()

        self.started = True


    def _make_commandline(self):
        """ generates the commandline to start either tss.js or tsserver.js,
            depending on the project settings """
        node_path = default_node_path(self.project.get_setting('node_path'))
        tss_path = get_tss_path()

        cwd = os.path.abspath(self.project.tsconfigdir)
        rootfile = self.project.get_first_file_of_tsconfigjson()
        if rootfile is None:
            Debug('error', "Please specify your files in tsconfig.json")
        cmdline = [node_path, tss_path, "--project", "."]

        return node_path, cwd, cmdline

    def send_async_command(self, async_command):
        """ Send a AsyncCommand() instance to the adapter thread. """
        self.tss_queue.put(async_command);

    def kill_tssjs_queue_and_adapter(self):
        """
            Tells adapter to leave syncronized queue and to finish
            and kills the tss.js process.
        """
        self.tss_queue.put("stop!") # setinel value to stop queue
        try:
            self.tss_process.terminate()
            self.tss_process.kill()
        except ProcessLookupError:
            pass
        try:
            # This fould fry sublime @ windows
            # but normally, the stream is closed already
            #self.tss_process.communicate() # release readline() block
            pass
        except Exception:
            pass

    def check_process_health(self):
        if self.tss_process.poll() is not None:
            Debug('error', 'TSS process has terminated unexpectly')
            errorout = self.tss_process.stderr.readlines()
            errorout_str = ''.join([str(s.decode('UTF-8')) for s in errorout])
            Debug('error', "typescript-tools error: \n %s" % errorout_str)

# ----------------------------------------- ADAPTER THREAD -------------------- #

class TssAdapterThread(Thread):
    """
        This class recieves commands from syncroized queue, merges/debounces them,
        executes them and then calls the async_command.callback in the the main_thread
        afterwards with the help of sublime.set_timeout().

        This class uses a middleware queue (simple array) to allow modification of command order.
        Every command form syncronized queue will immediatly be moved to middleware queue,
        because pythons Queue.Queue() does not allow for anything else than pop and put.

        Merging, debouncing and can then be done before poping the next command from middleware queue.

        The thread block of syncronized queue will be used to wait for new commands.
        To implement the debounce timeout, we add block release trigger commands
        to the queue via sublime.set_timeout(). This releases the queue when the command
        needs to be executed.

        If the setinel string "stop!" arrives on the syncronized queue, this thread will finish.
    """

    def __init__(self, stdin, stdout, queue, check_process_health_function):
        """
            stdin, stdout: Connection to tss.js,
            queue: Synchronized queue to receive AsyncCommand instances.
        """
        self.stdin = stdin
        self.stdout = stdout
        self.queue = queue
        self.check_process_health = check_process_health_function
        self.middleware_queue = []
        Thread.__init__(self)

    def run(self):
        """ Working Loop. """
        # block until queue is not empty anymore
        # leave loop and finish thread if "stop!" arrives
        for async_command in iter(self.queue.get, "stop!"):
            Debug('adapter', "CONTINUTE execution queue")

            self.append_to_middlewarequeue(async_command)
            self.add_pending_items_in_queue_to_middleware_queue()

            # non blocking loop: work on middleware_queue and keep up-to-date with arriving commands
            while not self.middleware_queue_is_finished():
                self.pop_and_execute_from_middleware_queue()
                self.add_pending_items_in_queue_to_middleware_queue()

            # => enter thread block
            Debug('adapter+', "WAIT for new work (%i currently debouncing)" % len(self.middleware_queue))

        Debug('adapter', "QUIT async adapter to tss process and close queue")
        try:
            self.stdin.close()
        except Exception:
            pass
        try:
            self.stdout.close()
        except Exception:
            pass


    def append_to_middlewarequeue(self, async_command, set_timer=True):
        """ Append async_command and set timer to release queue if told and needed. """
        self.middleware_queue.append(async_command)

        Debug('adapter+', "APPEND to middleware (in %fs): %s" % (async_command.time_until_execution(), async_command.id))
        if set_timer and not async_command.can_be_executed_now():
            self.trigger_queue_block_release_for(async_command)


    def trigger_queue_block_release_for(self, async_command):
        """ Sets timeout to trigger a block release just when async_command can be executed. """
        trigger_command = async_command.create_new_queue_trigger_command()
        seconds = async_command.time_until_execution()
        sublime.set_timeout(lambda: self.queue.put(trigger_command), int(seconds*1000) + 5)
        Debug('adapter+', "TRIGGER QUEUE in %fs" % seconds)


    def add_pending_items_in_queue_to_middleware_queue(self):
        """ Uses the non blocking version of get() to pop from syncronized queue. """
        try:
            while(True):
                async_command = self.queue.get_nowait()
                if async_command == "stop!":
                    return self.clear_queues_and_reappend_stop()
                self.append_to_middlewarequeue(async_command)
        except Empty:
            pass

    def clear_queues_and_reappend_stop(self):
        # forget everything else and reappend "stop!", so the blocking queue won't miss it
        try:
            while(True):
                self.queue.get_nowait()
        except Empty:
            pass
        self.middleware_queue = []
        self.queue.put("stop!")


    def middleware_queue_is_finished(self):
        """ Returns True if no more commands or only debouncing commands pending on middleware queue. """
        for cmd in self.middleware_queue:
            if cmd.can_be_executed_now():
                return False
        return True


    def pop_and_execute_from_middleware_queue(self):
        """ Executes the next command, but merge it first. If merging with procrastinating enabled, do not execute it. """
        if not self.middleware_queue_is_finished():
            command_to_execute = self.middleware_queue.pop(0)
            Debug('adapter', "POPPED from middleware: %s" % command_to_execute.id)

            if command_to_execute.is_only_a_queue_trigger_command():
                Debug('adapter+', "FOUND OLD TRIGGER object, don't execute anything")
                return

            command_to_execute = self.merge_cmd_on_middleware_queue_and_return_replacement(command_to_execute)
            if command_to_execute: # can be None if merge_procrastinate() has defered current item
                Debug('adapter', "EXECUTE now: %s" % command_to_execute.id)
                self.execute(command_to_execute)


    def merge_cmd_on_middleware_queue_and_return_replacement(self, async_command):
        """ Selecting merge behaviour and merge """
        if(async_command.merge_behaviour == async_command.MERGE_IMMEDIATE):
            return self.merge_immediate(async_command)
        elif(async_command.merge_behaviour == async_command.MERGE_PROCRASTINATE):
            return self.merge_procrastinate(async_command)


    def merge_immediate(self, command):
        """
            Removes all elements with the same id from middleware_queue.
            Remember: command is already poped from array, so there is no need to handle it
            Returns the last added aka newest same-id command
        """
        commands_to_remove = []
        newest_command = command
        for possible_replacement in self.middleware_queue: # from old to new
            if possible_replacement.id == command.id:
                newest_command = possible_replacement
                commands_to_remove.append(possible_replacement)

        if len(commands_to_remove) > 0:
            command.on_replaced(newest_command)
            for c in commands_to_remove:
                self.middleware_queue.remove(c)
                if c.id != newest_command.id:
                    c.on_replaced(newest_command)
            Debug('adapter+', "MERGED with %i other commands (immediate): %s" % (len(commands_to_remove), command.id) )

        return newest_command


    def merge_procrastinate(self, command):
        """
            If there is another command with same id, then do not execute it now.
            Delete all same-id commands except for the last one(=newest) in the array.
        """
        commands_to_remove = []
        for possible_duplicate in self.middleware_queue: # from old to new
            if possible_duplicate.id == command.id:
                commands_to_remove.append(possible_duplicate)

        if len(commands_to_remove) > 0:
            newest_command = commands_to_remove.pop() # don't delete newest duplicate command.
            command.on_replaced(newest_command)
            for c in commands_to_remove:
                c.on_replaced(newest_command)
                self.middleware_queue.remove(c)
            Debug('adapter+', "MERGED with %i other commands (procrastinated): %s" % (len(commands_to_remove), command.id) )
            return None # defer, no execution in this round
        else:
            return command # no defer, execute now, command has already been poped


    def execute(self, async_command):
        """
            Executes Command.
            If debouncing enabled und timeout not finished, add back to the end of the queue.
            This may cause unexpected behaviour but should be unnoticed mostly.
        """
        if not async_command.can_be_executed_now():
            self.append_to_middlewarequeue(async_command, set_timer=True) # reappend to end
            Debug('adapter+', "MOVED to end of queue, debouncing")
            return
        async_command.time_execute = time.time()
        try:
            self.stdin.write(encode(async_command.command))
            self.stdin.write(encode("\n"))
            self.stdin.flush()
            Debug('tss++', "Send to tss.js: %s" % async_command.command[0:100])

            async_command.on_execute()
            # causes result callback to be called async
            results = self.stdout.readline().decode('UTF-8')
            Debug('tss++', "Received from tss.js: %s" % results[0:100])
            async_command.on_result(results)
        except Exception as e:
            Debug('tss++', "ERROR: %s" % e)
            self.check_process_health()


