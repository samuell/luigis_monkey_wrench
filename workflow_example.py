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
        hejer = shell('echo hej > <o:hejfile:hej.txt>')
        fooer = shell('cat <i:hejfile> | sed "s/hej/foo/g" > <o:foofile:<i:hejfile>.foo>')

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
