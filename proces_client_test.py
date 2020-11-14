import hashlib
import os

na_client_path = "E:\\Steam\\steamapps\\common\\PHANTASYSTARONLINE2_NA_STEAM\\pso2_bin\\"
jp_client_path = "E:\\Games\\PHANTASYSTARONLINE2_JP\\pso2_bin\\"
na_win32_path = na_client_path + "data\\win32\\"
jp_win32_path = jp_client_path + "data\\win32\\"
matching_files_list = "matching_files_list.txt"


# Check all files in the JP win32 folder, any that are exactly the same on NA can
# stay, we'll symlink those. Any that don't exist, or are different we'll 
# redownload into the data folder and leave it accessible there
# NOTE:
# We're gonna symlink the *files*, not the entire data folder or we won't be able
# to symlink the files AND have the different/missing files be downloaded into
# the data folder for the JP client to work with NA
#
# This way when the NA client boots and looks into the data folder, it'll read the
# files that should be exactly the same as JP, and any of those files that would be
# different on JP will be downloaded from NA and dumped into the data/win32 folder

def create_symlink(from_file, to_file):
	if(os.path.isfile(to_file)):
		try:
			os.symlink(to_file, from_file)
			print(f"Symlink created!")
		except FileExistsError:
			print(f"Symlink already exists! Recreating it ({from_file} -> {to_file})")
			os.remove(from_file)
			os.symlink(to_file, from_file)
	else:
		print(f"The file you're trying to link to doesn't exist! ({to_file})")

def check_crc(filepath):
	file = open(filepath, 'rb').read()
	md5 = hashlib.md5(file).hexdigest()

	return md5

def dirty_write(file, message):
	# Yeah I know, should keep the files open so
	# we don't open close open close them. 
	# Consider this a "I wanna get to the point"
	# first implementation, will fix it later!
	log_file = open(file, 'a')
	log_file.write(message + "\n")
	log_file.close()

def found(message):
	dirty_write("found.txt", message)

def different(message):
	dirty_write("different.txt", message)

def not_found(message):
	dirty_write("not_found.txt", message)


def do_filecheck():
	file_count = len(os.listdir(jp_win32_path))
	i = 0
	print(f"Found {file_count} files in the JP client's win32 directory.")

	for filename in os.listdir(jp_win32_path):
		print(f"File: {i}/{file_count}")
		i = i + 1

		# If the same file exists in the NA folder
		if os.path.isfile(na_win32_path + filename):
			# See if the files differ or not
			na_crc = check_crc(na_win32_path + filename)
			jp_crc = check_crc(jp_win32_path + filename)

			# ..If they don't differ:
			if na_crc == jp_crc:
				output_text = f"{filename}"
				found(output_text)
			else:
				output_text = f"{filename} DIFFERENT\tJP: [{na_crc}] NA: [{jp_crc}]"
				different(output_text)
		else:
			output_text = f"{filename} doesn't exist in the NA folder"
			not_found(output_text)

def do_symlink():
	with open(matching_files_list) as file:
		lines = file.readlines()
		for line in lines:
			filename = line.split(' ')[0]
			na_file = na_win32_path + filename
			jp_file = jp_win32_path + filename
			
			# If the file actually exists
			if(os.path.isfile(na_file)):
				# Back the file up instead of removing it
				print(f"Backing up {filename}")
				os.rename(f"{na_file}", f"{na_win32_path}bkup\\{filename}")

				print(f"Creating symlink")
				create_symlink(na_file, jp_file)

do_symlink()