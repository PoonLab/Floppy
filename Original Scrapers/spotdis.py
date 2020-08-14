from Bio import SeqIO
import os, sys
import time 

# Define path to data file
path = '/home/galmog/Documents/Disorder/'
path1 = "/home/galmog/Documents/Disorder/SPOT-Disorder-Single/SPOT-Disorder-Single/"
# Define dictionary
seqs = {}

# Open file with metadata sequences
fa_file = SeqIO.parse(path + "disprot_virus.fa", "fasta")

# Store sequence and ids in a dictionary
for seq_data in fa_file:
    seqs[seq_data.id] = seq_data.seq
    

for header, sequence in seqs.iteritems():
    dis = header.split("_")
    ID = dis[0]
    header = ">" + ID
    seq = header + "\n" + sequence
    #print(seq)
    
    #create temporary file to be deleted
    out_file = open(path1 + ID + ".fa", "w")
    out_file.write(str(seq))

    spotdis = "spot-disorderG.py" # spotdis script
    cmd = 'python ' + spotdis + ' ' + ID + ".fa" # python command
    print(cmd)
    #os.system(cmd)
    
    #time.sleep(50)

    #delete temporary file 
    #os.remove(path1 + ID + ".fa")
