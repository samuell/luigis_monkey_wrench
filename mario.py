import luigi
import re
import commands

class AFile(luigi.ExternalTask):
    filename = luigi.Parameter()
    def requires(self):
        return luigi.LocalTarget(self.filename)

class ShellTask(luigi.Task):
    inports = luigi.Parameter(default={})
    cmd = luigi.Parameter()

    def requires(self):
        upstream_tasks = []
        for portname, inport in self.inports.iteritems():
            if type(inport) is dict:
                upstream_tasks.append(inport['upstream']['task'])
        return upstream_tasks
 
    def get_input(self, input_name):
        param = self.inports[input_name]
        if type(param) is dict and 'upstream' in param:
            return param['upstream']['task'].output()[param['upstream']['port']]
        else: 
            return param

    def output(self):
        ms = re.findall('\{o:([A-Za-z0-9-_\.]+)(:([A-Za-z0-9-_\.]+))\}', self.cmd)
        outputs = {m[0]: luigi.LocalTarget(m[2]) for m in ms}
        return outputs

    def get_out(self, outport):
        return { 'upstream' : { 'task': self, 'port': outport } }

    def set_in(self, inport, value):
        self.inports[inport] = value

    def run(self):
        cmd = self.cmd
        ms = re.findall('(\{i:([A-Za-z0-9-_\.]+)\})', cmd)
        for m in ms:
            cmd = cmd.replace(m[0], self.get_input(m[1]).path)
        ms = re.findall('(\{o:([A-Za-z0-9-_\.]+)(:([A-Za-z0-9-_\.]+))\})', cmd)
        for m in ms:
            cmd = cmd.replace(m[0], self.output()[m[1]].path)
        print("*** RUNNING COMMAND: " + cmd)
        print commands.getstatusoutput(cmd)


class WorkFlow(luigi.Task):
    def requires(self):
        hejer = ShellTask(cmd='echo hej > {o:hej:hej.txt}',inports={'tjo': luigi.LocalTarget('tjo.txt')})
        fooer = ShellTask(cmd='cat {i:bla} > {o:foo:foo.txt}')

        #hejer.inports['tjo'] = luigi.LocalTarget('tjo.txt')
        #fooer = ShellTask(cmd='cat {i:hej} > {o:foo:{i:hej}.foo.txt} # {i:tjo:tjo.txt}')

        # Define workflow
        fooer.inports['bla'] = { 'upstream' : { 'task' : hejer, 'port' : 'hej' } }
        return fooer

    def output(self):
        return luigi.LocalTarget('workflow_finished')

    def run(self):
        with self.output().open('w') as outfile:
            outfile.write('finished')


if __name__ == '__main__':
    luigi.run()



