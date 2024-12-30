import argparse
import sys
import clipboard as cb
from file_ops import load_config, shell, M_WORD,  M_CHAR

BANNER = '''    ____  _                          __   ______                  _ _    ______                
   / __ \\(_)_____________  _________/ /  / ____/___ ___  ____    (_|_)  / ____/___  ____ _   __
  / / / / / ___/ ___/ __ \\/ ___/ __  /  / __/ / __ `__ \\/ __ \\  / / /  / /   / __ \\/ __ \\ | / /
 / /_/ / (__  ) /__/ /_/ / /  / /_/ /  / /___/ / / / / / /_/ / / / /  / /___/ /_/ / / / / |/ / 
/_____/_/____/\\___/\\____/_/   \\__,_/  /_____/_/ /_/ /_/\\____/_/ /_/   \\____/\\____/_/ /_/|___/  
                                                           /___/                               '''

def main():
	for i in sys.argv:
		if i == "-h" or i == "--help":
			print(BANNER)

	parser = argparse.ArgumentParser(description="Converts text to discord emojis")
	parser.add_argument("-s", "--shell", action = "store_true")
	parser.add_argument("-S", "--show_sets", action = "store_true")
	parser.add_argument("-l", "--line", action = "store")
	parser.add_argument("-c", "--config-set", action = "store_true")
	parser.add_argument("-m", "--mode", action="store")

	args = parser.parse_args()		
	config = load_config()

	if args.shell == True:
		shell(config)
	
	elif args.config_set == True:
		config.get_character_sets()
		status = config.select_character_set()

		if status == True:
			config.update_config()
		else:
			print("Error: failed to update config")
			return
	
	elif args.line != None:
		content = config.output_string(args.line)
		cb.copy(content)
		print(content)

	elif args.mode != None:
		mode = args.mode

		if mode == M_CHAR or mode == M_WORD:
			config.mode = mode
		else:
			print("Error: unknown mode")
			return
		
		config.update_config()
	
	elif args.show_sets == True:
		config.get_character_sets()


if __name__ == "__main__":
    main()