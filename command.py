from __future__ import annotations
from abc import ABC, abstractmethod
import click
import os
import config
import logging
import sys
import shutil
import csv

if config.COMMANDS_CONFIG['log_type'] == "log":
    log_path = '/Main/myapp.log'
else:
    log_path = '/Main/myapp.csv'

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO ,
format='%(asctime)s %(levelname)s %(message)s',
      filename=log_path,
      filemode='w')

class Command(ABC):
    """
    The Command interface declares a method for executing a command.
    """

    @abstractmethod
    def execute(self) -> None:
        pass

class CleanCommand(Command):
    """
    Some commands can implement simple operations on their own.
    """

    def __init__(self, payload: str) -> None:
        self._payload = payload

    #@click.command()
    @click.argument('path')
    def execute(self) -> None:
        '''
        This command needs to keep a specific window (number of files) in the log path. 
        If they are higher, a number (deletion_threshold ) of oldest logs will be deleted.

        PATH is the directory path to clean , delete old logs if needed.

        '''
        path = self._payload
        print(f"CleanCommand: See, I can do simple things like sort directory"
              f"({self._payload})")
        try:
            if not os.path.exists(path):
                logging.error("Path does not exist")
                return    
        
            if not os.listdir(path):
                logging.error("Directory is empty.there is no log files to clean")
                return  
        except OSError as err:
            logging.error("OS error: {0}".format(err))
        except:
            logging.error("Unexpected error:", sys.exc_info()[0])
            raise
    
        number_of_files_to_keep = config.COMMANDS_CONFIG['window_size']
        logging.info("Number of file to keep: {0}".format(number_of_files_to_keep))
        
        deletion_threshold = config.COMMANDS_CONFIG["deletion_threshold"]
        logging.info("Number of file to delete: {0}".format(deletion_threshold))

        extension = config.COMMANDS_CONFIG["log_extension"]
        logging.info("Log extension type is: {0}".format(extension))

        filelist = []
        try:
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith(extension):
                        filelist.append(os.path.join(root, file))

            #Check that we have files to sort.if there are no files print to log and exit
            current_number_of_files = len(filelist) 
            if current_number_of_files == 0:
                logging.error("Directory does not have any log files to clean(with extension type {0})".format(extension))
                return  

            # sort files list according creation time 
            sortedlist = sorted(filelist, key=os.path.getmtime)[:-number_of_files_to_keep]
            filesToDelete = sortedlist[0:deletion_threshold]
            
            if len(filesToDelete) == 0:
                logging.info("No need to delete files.Current number of files: {0}".format(current_number_of_files))
                return
            
            logging.info("Total files to delete: {0}  deletion threshold: {1} ".format(len(sortedlist),deletion_threshold))
            
            for file in filesToDelete:
                logging.info("Removing file :[{0}]".format(file))
                os.remove(file)

        except OSError as err:
            logging.error("OS error: {0}".format(err))
        except:
            logging.error("Unexpected error:", sys.exc_info()[0])
            raise
      

class SimpleCommand(Command):
    """
    Some commands can implement simple operations on their own.
    """

    def __init__(self, payload: str) -> None:
        self._payload = payload

    def execute(self) -> None:
        print(f"SimpleCommand: See, I can do simple things like printing"
              f"({self._payload})")

class SortCommand(Command):
    """
    However, some commands can delegate more complex operations to other
    objects, called "receivers."
    """

    def __init__(self, receiver: Receiver, a: str, b: str) -> None:
        """
        Complex commands can accept one or several receiver objects along with
        any context data via the constructor.
        """

        self._receiver = receiver
        self._a = a
        self._b = b

    
    #@click.command()
    @click.argument('path')
    @click.option('--hash',default="C:/Main/summary.csv",help="The path for file that  save all information about the saved files")
    def execute(self) -> None:
        '''
        This command will take a specific directory and sort its contents based on file type. 
        For example, if we have a folder that has files of types .csv, .mat, .dxl. 
        Running the command will result into 3 subfolders within the parent one, 
        each has the name of files type and collects all of the files of this specific type.

        PATH is the directory path to sort its content.
        '''
        path = self._a
        hash = self._b
        print(f"Sort with folder path :{self._a}  and save to file:{self._b}")
        try:
            if not os.path.exists(path):
                logging.error("Path does not exist")
                return  
            
            if not os.listdir(path):
                logging.error("Directory is empty")
                return  

            dict = {}
            dictFiles = {}
   
            for root, dirs, files in os.walk(path):
                for file in files:
                    dictFiles[os.path.abspath(os.path.join(root, file))] = file


            #Check that we have files to sort and not just empty folders
            if len(dictFiles)== 0:
                logging.error("Directory does not have files to sort")
                return          
        except OSError as err:
            logging.error("OS error: {0}".format(err))
        except:
            logging.error("Unexpected error:", sys.exc_info()[0])
            raise

        try:  
            # This will go through each and every file
            for file_ in dictFiles.keys():
                name, ext = os.path.splitext(dictFiles[file_])

                # This is going to store the extension type
                ext = ext[1:]

                # This forces the next iteration,
                # if it is the directory
                if ext == '':
                    continue

                destination_file = path + '/' + ext + '/' + dictFiles[file_]    
            
                # This will move the file to the directory
                # where the name 'ext' already exists
                if os.path.exists(path + '/' + ext):
                    if not os.path.isfile(destination_file):
                        shutil.move( file_,destination_file)
                        logging.info("Move file: {0} into sub folder:{1}".format(dictFiles[file_],ext))
                        if ext in dict: dict[ext] += 1

                # This will create a new directory,
                # if the directory does not already exist
                else: 
                    os.makedirs(path + '/' + ext)
                    logging.info("Create new sub folder for extension: {0}".format(ext))
                    dict[ext] = 1
                    shutil.move( file_, destination_file)
                    logging.info("Move file: {0} into sub folder:{1}".format(dictFiles[file_],ext))
               
        except OSError as e:   
            logging.error('Sort directory Failed: [{0}]'.format(e))
        except:
            logging.error("Unexpected error:", sys.exc_info()[0])
            raise  
    
        try:
            w = csv.writer(open(hash, "w"))
            for key, val in dict.items():
                w.writerow([key, val])
        except IOError as e:
            logging.error("I/O error({0}): {1}".format(e.errno, e.strerror))
        except:
            logging.error("Unexpected error:", sys.exc_info()[0])
            raise          

class ComplexCommand(Command):
    """
    However, some commands can delegate more complex operations to other
    objects, called "receivers."
    """

    def __init__(self, receiver: Receiver, a: str, b: str) -> None:
        """
        Complex commands can accept one or several receiver objects along with
        any context data via the constructor.
        """

        self._receiver = receiver
        self._a = a
        self._b = b

    def execute(self) -> None:
        """
        Commands can delegate to any methods of a receiver.
        """

        print("ComplexCommand: Complex stuff should be done by a receiver object", end="")
        self._receiver.do_something(self._a)
        self._receiver.do_something_else(self._b)


class Receiver:
    """
    The Receiver classes contain some important business logic. They know how to
    perform all kinds of operations, associated with carrying out a request. In
    fact, any class may serve as a Receiver.
    """

    def do_something(self, a: str) -> None:
        print(f"\nReceiver: Working on ({a}.)", end="")

    def do_something_else(self, b: str) -> None:
        print(f"\nReceiver: Also working on ({b}.)", end="")


class Invoker:
    """
    The Invoker is associated with one or several commands. It sends a request
    to the command.
    """

    _on_start = None
    _on_finish = None

    """
    Initialize commands.
    """

    def set_on_start(self, command: Command):
        self._on_start = command

    def set_on_finish(self, command: Command):
        self._on_finish = command

    def do_something_important(self) -> None:
        """
        The Invoker does not depend on concrete command or receiver classes. The
        Invoker passes a request to a receiver indirectly, by executing a
        command.
        """

        print("Invoker: Does anybody want something done before I begin?")
        if isinstance(self._on_start, Command):
            self._on_start.execute()

        print("Invoker: ...doing something really important...")

        print("Invoker: Does anybody want something done after I finish?")
        if isinstance(self._on_finish, Command):
            self._on_finish.execute()


if __name__ == "__main__":
    """
    The client code can parameterize an invoker with any commands.
    """

    invoker = Invoker()
    invoker.set_on_start(SimpleCommand("Say Hi!"))
    invoker.set_on_start(CleanCommand("C:\Main\log"))
    receiver = Receiver()
    invoker.set_on_finish(ComplexCommand(
        receiver, "Send email", "Save report"))
    invoker.set_on_finish(SortCommand(
        receiver, "C:\Main\mixed", "C:\Main\Info.csv"))

    invoker.do_something_important()