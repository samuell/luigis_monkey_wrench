## Luigi's Monkey Wrench

This library intends to make [Luigi]() workflows for typical tasks on the commandline
in e.g. bioinformatics, a tad easier and more fluent, by allowing to define workflow
tasks and dependencies in the following fashion:

````python
import luigi
import monkeywrench as lmw

class WorkFlow(luigi.Task):
    def requires(self):
        # Create tasks by initializing ShellTasks, and giving
        # the shell tasks to execute to the cmd parameter.
        # File names are given in a this special form:
        #   {i:<input name>}
        #   {o:<output name>:<output filename>}
        hejer = lmw.ShellTask(cmd="echo hej > {o:hej:hej.txt}")
        fooer = lmw.ShellTask(cmd="cat {i:bla} | sed 's/hej/foo/g' > {o:foo:foo.txt}")

        # Define how outputs from tasks are re-used in inputs
        # of other tasks
        fooer.set_inspec('bla', hejer.get_outspec('hej'))

        # Return the last task in the workflow
        return fooer

    def output(self):
        # Print some dummy file to tell that the workflow is finished
        return luigi.LocalTarget('workflow_finished')

    def run(self):
        # Write some dummy content to dummy file
        with self.output().open('w') as outfile:
            outfile.write('finished')


# We start the process by letting luigi run
if __name__ == '__main__':
    luigi.run()
````

### Current Status: Experimental

***Use on your own risk only!***
