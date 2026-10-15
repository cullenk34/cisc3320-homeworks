import os

def main():
	#print PID
	print(f"PID: {os.getpid()}")
	
	#print parent PID
	print(f"PPID: {os.getppid()}")
	
	#environment
	print("\nEnvironment:")
	for key, value in os.environ.items():
	    print(f"{key}={value}")
	
	#file descriptors
	print("\nFile Descriptors:")
	for fd in os.listdir('/proc/self/fd'):
	    try:
	        target = os.readlink(f'/proc/self/fd/{fd}')
	        print(f"fd {fd}: {target}")
	    except OSError:
	        print(f"fd {fd}: file closed")
	
if __name__ == "__main__":
    main()
