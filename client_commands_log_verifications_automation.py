import os
import string
import random
import argparse
from threading import Thread
from time import sleep
from subprocess import PIPE, run
import traceback

"""
Author: Madhu , email: msraju2009@gmail.com

Prerequisite: Server.jar needs to be executed before running this script
# tested this script with 10000 client threads

This program is intended to check different operations on the client side by executing client.jar
and verify if the commands are executed successfully and logs in the log file

How to execute this program:
---if user want to specify name,number of client threads via command line 
   else the script takes demo as name,5 client threads by default---
        ex: python execute_client_jar.py --name demo --threads 2
   else 
        python execute_client_jar.py 
"""
nl = '\n'
file_path = os.path.abspath(os.path.dirname(__file__))
# create an argument parser
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('--name', type=str, help="Name used when executed with server.jar")
arg_parser.add_argument('--threads', type=int, help="Number of client threads to execute")
args = arg_parser.parse_args()
try:
    if args.name and args.threads:
        name = args.name
        client_thread_count = args.threads
    else:
        name = "demo"
        client_thread_count = 2
except argparse.ArgumentError:
    print("Arguments provided are incorrect, pls check the help")
print("*" * 50)
print(f"Name is {name} and client thread count is {client_thread_count}")


def execute_command(command):
    """This function will take command and returns output of the command execution"""
    try:
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
        return result.stdout.strip()
    except Exception:
        print(f"Exception occurred while executing {command} and following is the exception \n {traceback.print_exc()}")


def file_content(file_name):
    """This function will take log filename and returns content of log in string format"""
    try:
        with open(os.path.join(file_path, file_name + ".log")) as fp:
            content = fp.read()
            return content
    except FileNotFoundError:
        print(f"{file_name} not found in {file_path} and following is the exception \n {traceback.print_exc()}")


def verify_slot_list_interactive_mode(name, random_slot_name):
    """This function will verify if slot name is found in list of slots"""
    list_cmd_output = execute_command(f'java -jar client.jar {name} \"list\"')
    assert random_slot_name in list_cmd_output
    print(f"Slot {random_slot_name} exists in list of slots {[slot for slot in list_cmd_output.split(nl)[1:]]}")


def verify_slot_creation_interactive_mode(name, random_slot_name):
    """This function will verify if slot name is created and is found in name.log file"""
    create_cmd_output = execute_command(f'java -jar client.jar {name} \"create {random_slot_name}\"')
    assert create_cmd_output == "CREATED"
    print(f"Created slot ----{random_slot_name}----")
    slot_creation_in_file = f"Created slot \'{random_slot_name}\' with value 0" in file_content(name)
    if slot_creation_in_file:
        print(f"Slot {random_slot_name} created successfully and written to {name}.log")
    else:
        raise Exception(f"Slot {random_slot_name} creation failed and not found in {name}.log")


def verify_slot_value_set_interactive_mode(name, random_slot_name, number):
    """This function will verify if value for slot is set and is found in name.log file"""
    set_cmd_output = execute_command(f'java -jar client.jar {name} \"set {random_slot_name} {number}\"')
    assert set_cmd_output == f'Set \'{random_slot_name}\' to {number}'
    print(f"Slot ----{random_slot_name}---- set to ----{number}----")
    slot_set_in_file = f"Processing command \'SET\' with args \'{random_slot_name} {number}\'" in file_content(name)
    if slot_set_in_file:
        print(f"Slot {random_slot_name} set successfully and written to {name}.log")
    else:
        raise Exception(f"Slot {random_slot_name} set value failed and not found in {name}.log")


def verify_slot_get_interactive_mode(name, random_slot_name, number):
    """This function will verify if we're able to get slot name and number and is found in name.log file"""
    get_cmd_output = int(execute_command(f'java -jar client.jar {name} \"get {random_slot_name}\"'))
    assert get_cmd_output == number
    print(f"Slot ----{random_slot_name}---- get value is ----{number}----")
    slot_get_in_file = f"Processing command \'GET\' with args \'{random_slot_name}\'" in file_content(name)
    if slot_get_in_file:
        print(f"Slot {random_slot_name} get successfully and written to {name}.log")
    else:
        raise Exception(f"Unable to get Slot {random_slot_name} in {name}.log")


def verify_slot_increment_interactive_mode(name, random_slot_name, number):
    """This function will verify if we're able to increment slot value and is found in name.log file"""
    increment_cmd_output = (execute_command(f'java -jar client.jar {name} \"increment {random_slot_name}\"'))
    assert increment_cmd_output == f'Incremented \'{random_slot_name}\' to {number+1}'
    print(f"Slot ----{random_slot_name}---- INCREMENTED to ----{number+1}----")
    slot_increment_in_file = f"Processing command \'INCREMENT\' with args \'{random_slot_name}\'" in file_content(name)
    if slot_increment_in_file:
        print(f"Slot {random_slot_name} incremented successfully and written to {name}.log")
    else:
        raise Exception(f"Unable to get Slot {random_slot_name} increment in {name}.log")


def verify_slot_drop_interactive_mode(name, random_slot_name):
    """This function will verify if slot name is dropped and is found in name.log file"""
    drop_cmd_output = execute_command(f'java -jar client.jar {name} \"drop {random_slot_name}\"')
    assert drop_cmd_output == "DROPPED"
    print(f"Dropped slot ----{random_slot_name}----")
    slot_drop_in_file = f"Dropped slot \'{random_slot_name}\'" in file_content(name)
    if slot_drop_in_file:
        print(f"Slot {random_slot_name} dropped successfully and written to {name}.log")
    else:
        raise Exception(f"Unable to drop Slot {random_slot_name} in {name}.log")


def execute_slot_crud_operations_in_interactive_mode():
    """This function will iterate through specified range of threads, executes commands
    like create, get, list, increment, set, drop and verifies if the entries are found in log as well"""
    for x in range(1, client_thread_count + 1):
        print("*" * 50)
        # creating a random slot name
        random_slot_name = str(''.join(random.choices(string.ascii_letters, k=10)))
        # creating a random number for setting the value to the slot
        number = random.randint(1, 1000)
        print(
            f"Executing slot count number {x} and name is {name}, slot name is {random_slot_name}, number is {number}")
        # verifying all the operations like create, list, set, increment, get, drop
        verify_slot_creation_interactive_mode(name, random_slot_name)
        verify_slot_list_interactive_mode(name, random_slot_name)
        verify_slot_value_set_interactive_mode(name, random_slot_name, number)
        verify_slot_get_interactive_mode(name, random_slot_name, number)
        verify_slot_increment_interactive_mode(name, random_slot_name, number)
        verify_slot_get_interactive_mode(name, random_slot_name, number+1)
        verify_slot_drop_interactive_mode(name, random_slot_name)
        print("*" * 50, "\n")
        sleep(1)


if __name__ == "__main__":
    T1 = Thread(target=execute_slot_crud_operations_in_interactive_mode)
    sleep(0.2)
    T1.start()
    T1.join()
