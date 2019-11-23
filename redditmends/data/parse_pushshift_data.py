import csv

if __name__ == "__main__":
	with open("./redditmends/data/raw_pushshift_parameters.txt", newline='') as parameters:
		parameter_reader = csv.reader(parameters, delimiter='\t')
		for parameter in parameter_reader:
			print(f"\"{parameter[0]}\": [\"{parameter[2]}\", \"{parameter[1]}\", \"{parameter[3]}\"],")