# DEPRECATED!

- This library is no longer maintained. The functionality of the library has moved into [SciLuigi](https://github.com/samuell/sciluigi).

# Luigi's Monkey Wrench

This is a small library (50 LOC exactly, as of Feb 12) that intends to make writing [Luigi]() workflows that use a lot of shell commands
(which is common e.g. in bioinformatics) a tad easier by allowing to define workflow tasks with a simple shell command pattern, and
dependencies by using a simple single-assignment patter for specifying how tasks inputs depend on each other's outputs, like so:

````python
import luigi
from luigis_monkey_wrench import *

class MyWorkFlow(WorkflowTask):
    def requires(self):
		# Create some tasks
        hejer = shell('echo hej > <o:hejfile:hej.txt>')
        fooer = shell('cat <i:hejfile> | sed "s/hej/foo/g" > <o:foofile:<i:hejfile:.txt|.foo>>')

		# Connect them together
        fooer.inports['hejfile'] = hejer.outport('hejfile')

		# Return the last one in the chain
        return fooer

# Make this a runnable script, and leave control to luigi
if __name__ == '__main__':
    luigi.run()
````

Short and neat, ain't it?

But let's go though this example in a bit more detail, to see what we are really doing:

````python
import luigi
from luigis_monkey_wrench import *

# Yes, we write the workflow definition inside a normal luigi task ...
class MyWorkFlow(WorkflowTask):
    # ... and do this by setting up the dependency graph and (letting the workflow
    # task depend on it, by) returning the last task in the dependecy graph in the
	# workflow task's requires() function:
    def requires(self):
        # Create tasks by initializing ShellTasks, and giving
        # the shell tasks to execute to the cmd parameter.
        # File names are given in a this special form (including <>):
        #   <i:INPUT_NAME>
        #   <o:OUTPUT_NAME:OUTPUT_FILENAME>
        # Output file names can also include the filename of an input:
        #   <o:some_output:<i:some_input>.some_extension>
		# One can also just replace the extension, or ending, of the input
		# filename, in the output file name, using the following syntax:
        #   <o:OUTPUT_NAME:<i:INPUT_NAME:OLD_EXTENSION|NEW_EXTENSION>>
		# E.g, to create <filename>.csv as output from <filename>.txt, we do:
        #   <o:some_output:<i:some_input:.txt|.csv>>
        hejer = shell('echo hej > <o:hejfile:hej.txt>')
        fooer = shell('cat <i:hejfile> | sed "s/hej/foo/g" > <o:foofile:<i:hejfile:.txt|.foo>>')

        # Define the workflow "dependency graph" by telling how outputs
        # from tasks are re-used in inputs of other tasks
        fooer.inports['hejfile'] = hejer.outport('hejfile')

        # Return the last task in the workflow
        return fooer


# We finally make this file into an executable python file, and let luigi take of the running
# which will, among many other cool things, mean that we get a nice command line interface
# generated for us:
if __name__ == '__main__':
    luigi.run()
````
Now run this (as usual with luigi tasks) like this:
````bash
python workflow_example.py --local-scheduler MyWorkFlow
````

## Quick start

Install the dependencies, luigi (and optionally tornado):
````bash
pip install luigi
pip install tornado
````

Clone this git repo to somewhere:
````bash
mkdir testlmw
cd testlmw
git clone https://github.com/samuell/luigis_monkey_wrench.git .
````

Run the example script (or one that you have already)
````bash
python workflow_example.py --local-scheduler MyWorkFlow
````
## Examples

- [A "Real-world" NGS Bioinformatics example workflow](https://gist.github.com/samuell/6da9a7c1e03912fde62e)

## Current Status: Experimental

***Use on your own risk only!***
