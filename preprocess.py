import csv
import pandas as pd
import glob
import os

question_id = []
question_link = []
question  = []
answer_count = []
answers = []

def filter(input_name = './csv/data_unfitered.csv', output_name = './csv/data_filtered.csv', no_of_answers = 10, no_of_follows = 40):
    with open (input_name) as file:
        data = csv.reader(file)
        with open(output_name,'a') as new:
            for row in data:
                if int(row[3])>no_of_answers and int(row[4])>no_of_follows:
                    writer = csv.writer(new)
                    writer.writerow(row)

def sorting (input_name = "./csv/QuoraData_filtered.csv", output_name = "./csv/QuoraData_sorted.csv", sort_section = 'follow', ascending = False):
    '''
    if sort by section:
        follow
        ans_count
        question
        link
        id
    Use as sort_section to arrange accordingly
    '''
    (pd.read_csv(input_name, names=["id", "link", "que", "ans_count", "follow"])
   .sort_values(sort_section, ascending = ascending)
   .to_csv(output_name, index=False))

def split(strng, sep, pos):
    strng = strng.split(sep)
    return sep.join(strng[:pos]), sep.join(strng[pos:])

def limit_answers(directory = './data/answers/', reference = './csv/QuoraData_filtered.csv', limit = 10):
    '''
    Limit the no.of answers to be saved in the text file
    Inputs : directory - directory of the answers
             referenc - reference document in CSV format
    Output : rewrites the text files in 'directory'
    '''
    if (os.path.isfile(reference)):
        first_line = True
        with open(reference) as file:
            reader = csv.reader(file)
            for row in reader:
                if first_line:
                    first_line = False
                    continue
                question_id.append(row[0])
    else:
        print ('Specified refernce document not found')

    filecount = glob.glob1(directory,"*.txt")
    for file in filecount:
        with open(str(directory+file),'r+') as textfile:
            text = textfile.read()
            ans_count = text.count('\n##########\n')
            if ans_count > limit:
                modified_text = split(text, '\n##########\n', 10)[0]
                textfile.write(modified_text)
                textfile.write ('\n##########\n')

def duplicates(filename = './csv/hr_unfitered.csv'):
    from more_itertools import unique_everseen
    with open(filename,'r') as f, open('out.csv','w') as out_file:
        out_file.writelines(unique_everseen(f))

def format_csv(filename='./csv/hr_sorted.csv', directory = './data/HR_keyphrases/', output = './csv/HR_keys.csv'):
    first_line = True
    with open(filename, 'r') as csvFile:
        with open(output, 'a') as new_CSV:
            reader = csv.reader(csvFile)
            for row in reader:
                new_row = []
                if first_line:
                    first_line = False
                    continue
                new_row.append(row[0])
                new_row.append(row[2])
                try:
                    with open(str(directory+row[0]+'.txt')) as file:
                        new_row.append(file.read())
                        #print(new_row)
                        writer = csv.writer(new_CSV, quoting=csv.QUOTE_ALL)
                        writer.writerow(new_row)
                except:
                    new_row.append('-')
                    writer = csv.writer(new_CSV, quoting=csv.QUOTE_ALL)
                    writer.writerow(new_row)

if __name__ == '__main__':
    duplicates(filename='./csv/QuoraData_filtered.csv')
    format_csv(filename='./csv/QuoraData_filtered.csv', directory='./data/Interview_keyphrases/',output = './csv/interview_keys.csv')
