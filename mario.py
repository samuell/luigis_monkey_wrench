import luigi
import re
import commands

class AFile(luigi.ExternalTask):
    filename = luigi.Parameter()
    def requires(self):
        return luigi.LocalTarget(self.filename)

class ShellTask(luigi.Task):
    inports = {}
    outports = {}

    cmd = luigi.Parameter()

    def requires(self):
        upstream_tasks = []
        print "*** INPORTS: " + str(self.inports)
        #import pdb; pdb.set_trace()
        for portname, inport in self.inports.iteritems():
            if type(inport) is dict:
                upstream_tasks.append(inport['upstream']['task'])
        print("*** UPSTREAM TASKS: " + str(upstream_tasks))
        return upstream_tasks
 
    def get_input(self, input_name):
        #import pdb; pdb.set_trace()
        param = self.inports[input_name]
        if type(param) is dict and 'upstream' in param:
            return param['upstream']['task'].output()[param['upstream']['port']]
        else: 
            return param

    def output(self):
        #import pdb; pdb.set_trace()
        ms = re.findall('\{o:(.+)(:([^\}]+))\}', self.cmd)
        outputs = []
        for m in ms:
            outputs.append(luigi.LocalTarget(m[2]))
        return outputs

    def get_out(self, outport):
        return { 'upstream' : { 'task': self, 'port': outport } }

    def set_in(self, inport, value):
        self.inports[inport] = value

    def run(self):
        cmd = self.cmd
        ms = re.findall('\{i:([A-Za-z0-9-_\.]+)(:([A-Za-z0-9-_\.]+))\}', cmd)
        for m in ms:
            cmd = cmd.replace(m[1], self.get_input(m[2]))
        cmd = re.sub('\{o:([A-Za-z0-9-_\.]+)(:([A-Za-z0-9-_\.]+))\}', '\\3', cmd)
        #import pdb; pdb.set_trace()
        print("*** Trying now to run command: " + cmd)
        print commands.getstatusoutput(cmd)


class WorkFlow(luigi.Task):
    def requires(self):
        hejer = ShellTask(cmd='echo hej > {o:hej:hej.txt}')
        hejer.inports['tjo'] = luigi.LocalTarget('tjo.txt')

        fooer = ShellTask(cmd='cat {i:bla} > {o:foo:foo.txt}')
        #fooer = ShellTask(cmd='cat {i:hej} > {o:foo:{i:hej}.foo.txt} # {i:tjo:tjo.txt}')

        # Define workflow
        #fooer.set_in('bla', hejer.get_out('hej'))

        #import pdb; pdb.set_trace()
        return hejer

    def output(self):
        #import pdb; pdb.set_trace()
        return luigi.LocalTarget(self.input()[0].path + '.workflow_finished')

    def run(self):
        with self.output().open('w') as outfile:
            outfile.write('finished')


if __name__ == '__main__':
    luigi.run()



