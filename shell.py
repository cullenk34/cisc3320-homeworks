import os
import shlex
import signal

BUILTINS = ["cd", "exit", "jobs", "fg", "kill"]

class Job:
    def __init__(self, job_id, pid, command):
        self.job_id = job_id
        self.pid = pid
        self.command = command
        self.status = "Running"

jobs = {}
next_job_id = 1

def run_external(tokens, background):
    global next_job_id
    pid = os.fork()
    
    if pid == 0:
        try:
            os.execvp(tokens[0], tokens)
        except FileNotFoundError:
            print(f"myshell: {tokens[0]}: command not found")
        finally:
            os._exit(127)
    
    if background:
        job = Job(next_job_id, pid, " ".join(tokens))
        jobs[next_job_id] = job
        print(f"[{job.job_id}] {pid} {job.command}")
        next_job_id += 1
    else:
        os.waitpid(pid, 0)

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

def handle_cd(args):
    if not args:
        print("myshell: cd: missing argument")
        return
    try:
        os.chdir(args[0])
    except FileNotFoundError:
        print(f"myshell: cd: {args[0]}: File or directory not found")

def handle_jobs(args):
    done_ids = []
    for job_id in sorted(jobs):
        job = jobs[job_id]
        print(f"[{job_id}] {job.status} {job.command}")
        if job.status == "Done":
            done_ids.append(job_id)
    for job_id in done_ids:
        del jobs[job_id]

def reap():
    while True:
        pid, status = os.waitpid(-1, os.WNOHANG)
        if pid == 0:
            return
        for job in jobs.values():
            if job.pid == pid:
                job.status = "Done"
                break

def get_job(job_id_str=None):
    #takes job_id as string as input
    #no argument gets most recent job, returns None if jobs is empty
    if job_id_str is None:
        if not jobs:
            return None
        job_id = max(jobs.keys())
    #else get then return the job or None for non-int-able input
    else:
        try:
            job_id = int(job_id_str)
        except ValueError:
            return None
    return jobs.get(job_id)

def handle_fg(args):
    #get the specified job, the most recent job if no argument, or None if invalid argument
    job = get_job(args[0] if args else None)
    if job is None:
        print(f"myshell: fg: job {args[0] if args else 'n/a'} not found")
        return
    #bring the job forward, wait to finish, and set status to Done
    pid, status = os.waitpid(job.pid, 0)
    job.status = "Done"
    print(f"myshell: fg: {job.command} ({job.job_id}) done")

def handle_kill(args):
    #no argument prints an error instead of getting most recent job like fg does so kill always has to be explicit
    if not args:
        print("myshell: kill: missing job number")
        return
    #get the job or print an error for invalid input
    job = get_job(args[0])
    if job is None:
        print(f"myshell: kill: job {args[0]} not found")
        return
    #try to send the SIGTERM signal
    try:
        os.kill(job.pid, signal.SIGTERM)
    #process already dead
    except ProcessLookupError:
        pass
    #just in case permission issue
    except PermissionError:
        print(f"myshell: kill: permission denied for job {job.job_id}")
        return
    #reap or pass if already reaped
    try:
        pid, status = os.waitpid(job.pid, os.WNOHANG)
        if pid == job.pid:
            job.status = "Done"
    except ChildProcessError:
        pass
    
    print(f"[{job.job_id}] Terminated {job.command}")
    del jobs[job.job_id]

def main():
    while True:
        try:
            reap()
        except ChildProcessError:
            pass
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
        elif cmd == "fg":
            handle_fg(args)
        elif cmd == "kill":
            handle_kill(args)
        else:
            run_external(tokens, background)
        

if __name__ == "__main__":
    main()
