import luigi
import mario as m

class WorkFlow(luigi.Task):
    def requires(self):
        # Create tasks
        hejer = m.ShellTask(cmd='echo hej > {o:hej:hej.txt}')
        fooer = m.ShellTask(cmd='cat {i:bla} > {o:foo:foo.txt}')

        # Define workflow
        fooer.set_inspec('bla', hejer.get_outspec('hej'))

        # Return the last task in the workflow
        return fooer

    def output(self):
        return luigi.LocalTarget('workflow_finished')

    def run(self):
        with self.output().open('w') as outfile:
            outfile.write('finished')

if __name__ == '__main__':
    luigi.run()
