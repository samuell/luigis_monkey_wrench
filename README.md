## FloWork

This library intends to make the following syntax possible, 
for defining and running command-line workflows:

````python
// Create tasks

// Create a task that runs some data through grep, which keeps
// only lines containing "hej"
grep = fw.ShellTask('cat {i:rawdata} | grep hej > {o:grepped}')

// Create a task that copies a file into another one, with .2 added
//  to the file name.
copy = fw.ShellTask('cp {i:orig} {o:copy}.2')

// Network definition (connect outports to inports)
copy.set_inport("orig") = grep.get_outport("grepped")
// the .get_outport() function would here return the
// struct that describes what to run, etc.

// For the initial inport, we have to create an inport
// "semi-manually", since we don't get it from any outport.
grep.set_inport('rawdata') = luigi.LocalTarget('hejsan.txt')

// We start the process by letting luigi run
if __name__ == '__main__':
	luigi.run()
````
