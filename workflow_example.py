import luigi
import luigis_monkeywrench as lmw

class WorkFlow(luigi.Task):
    def requires(self):
        # Create tasks
        hejer = lmw.ShellTask(cmd="echo hej > {o:hej:hej.txt}")
        fooer = lmw.ShellTask(cmd="cat {i:bla} | sed 's/hej/foo/g' > {o:foo:foo.txt}")

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
