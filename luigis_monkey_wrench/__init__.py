import luigi
import re
import commands

class AFile(luigi.ExternalTask):
    filename = luigi.Parameter()
    def requires(self):
        return luigi.LocalTarget(self.filename)

class ShellTask(luigi.Task):
    cmd = luigi.Parameter()

    def __init__(self, *args, **kwargs):
        super(ShellTask, self).__init__(*args, **kwargs)
        self.inports = {}

    def requires(self):
        upstream_tasks = []
        if hasattr(self, 'inports'):
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

    def _replace_inputs(self, cmd):
        ms = re.findall('(\<i:([^\>]+)\>)', cmd)
        for m in ms:
            cmd = cmd.replace(m[0], self.get_input(m[1]).path)
        return cmd

    def output(self):
        cmd = self._replace_inputs(self.cmd)
        ms = re.findall('(\<o:([^\>]+)(:([^\>]+))\>)', cmd)
        outputs = {m[1]: luigi.LocalTarget(m[3]) for m in ms}
        return outputs

    def get_outport_ref(self, outport):
        return { 'upstream' : { 'task': self, 'port': outport } }
    def outport(self, outport):
        return self.get_outport_ref(outport)

    def inport(self, portname):
        if not hasattr(self, 'inports'):
            self.inports = {}
        return self.inports[portname]

    def run(self):
        cmd = self._replace_inputs(self.cmd)
        ms = re.findall('(\{o:([^\}]+)(:([^\}]+))\})', cmd)
        for m in ms:
            cmd = cmd.replace(m[0], self.output()[m[1]].path)
        commands.getstatusoutput(cmd)
