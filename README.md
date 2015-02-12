## Luigi's Monkey Wrench

This library intends to make [Luigi]() workflows for typical tasks on the commandline
in e.g. bioinformatics, a tad easier and more fluent, by allowing to define workflow
tasks and dependencies in the following fashion:

````python
import luigi
import luigis_monkey_wrench as lmw

# Yes, we write the workflow definition inside a normal luigi task ...
class MyWorkFlow(luigi.Task):

    # ... and do this by setting up the dependency graph and (letting the workflow
    # task depend on it, by) returning the last task in the dependecy graph in the
	# workflow task's requires() function:
    def requires(self):

        # Create tasks by initializing ShellTasks, and giving
        # the shell tasks to execute to the cmd parameter.
        # File names are given in a this special form:
        #   {i:<input name>}
        #   {o:<output name>:<output filename>}
        # Output file names can also include the filename of an input:
        #   {o:some_output:{i:some_input}.some_extension}
        hejer = lmw.ShellTask(cmd="echo hej > {o:hejfile:hej.txt}")
        fooer = lmw.ShellTask(cmd="cat {i:hejfile} | sed 's/hej/foo/g' > {o:foofile:{i:hejfile}.foo}")

        # Define the workflow "dependency graph" by telling how outputs
        # from tasks are re-used in inputs of other tasks
        fooer.inports['hejfile'] = hejer.get_outport_ref('hejfile')

        # Return the last task in the workflow
        return fooer


    def output(self):
        # Return a dummy file that will tell that the workflow is finished
        return luigi.LocalTarget('workflow_finished')


    def run(self):
        # Write some dummy content to dummy file
        with self.output().open('w') as outfile:
            outfile.write('finished')


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

### Current Status: Experimental

***Use on your own risk only!***
