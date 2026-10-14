import os
import shlex

BUILTINS = ["cd", "exit", "jobs", "fg", "kill"]

jobs = {}
next_job_id = 1

def parse(line):
    #parse input line
    line = line.strip()
    #background job detection
    background = False
    if line.endswith("&"):
        background = True
        line = line[:-1].strip()
    #tokenize
    tokens = shlex.split(line)
    return tokens, background

def run_external(tokens, background):
    pid = os.fork()
    
    if pid == 0:
        try:
            os.execvp(tokens[0], tokens)
        except FileNotFoundError:
            print(f"myshell: {tokens[0]}: command not found")
        finally:
            os._exit(127)
    
    if background:
        pid, status = os.waitpid(pid, 0)
        print(f"[debug] child {pid} exited with {os.waitstatus_to_exitcode(status)}")
    else:
        os.waitpid(pid, 0)

def handle_cd(args):
    if not args:
        print("myshell: cd: missing argument")
        return
    try:
        os.chdir(args[0])
    except FileNotFoundError:
        print(f"myshell: cd: {args[0]}: File or directory not found")

def handle_jobs(args):
    if not jobs:
        print("No background jobs")
        return
    for job_id in sorted(jobs):
        job = jobs[job_id]
        print(f"[{job_id}] {job.status} {job.command}")

def main():
    while True:
        try:
            line = input("myshell> ")
        except EOFError:
            print()
            break

        if not line.strip():
            continue

        try:
            tokens, background = parse(line)
        except ValueError:
            print("myshell: parsing error")
            continue

        cmd, args = tokens[0], tokens[1:]
        
        if cmd == "exit":
            break
        elif cmd == "cd":
            handle_cd(args)
        elif cmd == "jobs":
            handle_jobs(args)
        elif cmd in BUILTINS:
            print(f"myshell: under construction, coming soon")
        else:
            run_external(tokens, background)
        

if __name__ == "__main__":
    main()
