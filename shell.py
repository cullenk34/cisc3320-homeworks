import os
import shlex

BUILTINS = ["cd", "exit", "jobs", "fg", "kill"]

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

def main():
	while True:
		try:
			line = input("myshell> ")
		except EOFError:
			print()
			break

		if not line.strip():
			continue

		tokens, background = parse(line)
		print(f"tokens={tokens} background={background}")

if __name__ == "__main__":
	main()
