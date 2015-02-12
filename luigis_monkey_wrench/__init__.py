import luigi
import re
import commands

class AFile(luigi.ExternalTask):
    filename = luigi.Parameter()
    def requires(self):
        return luigi.LocalTarget(self.filename)

class ShellTask(luigi.Task):
    cmd = luigi.Parameter()

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
        #import pdb; pdb.set_trace()
        ms = re.findall('(\{i:([^\}]+)\})', cmd)
        for m in ms:
            cmd = cmd.replace(m[0], self.get_input(m[1]).path)
        return cmd

    def output(self):
        cmd = self._replace_inputs(self.cmd)
        ms = re.findall('(\{o:([^\}]+)(:([^\}]+))\})', cmd)
        #import pdb; pdb.set_trace()
        outputs = {m[1]: luigi.LocalTarget(m[3]) for m in ms}
        return outputs

    def get_outspec(self, outport):
        return { 'upstream' : { 'task': self, 'port': outport } }

    def set_inspec(self, inport, value):
        if not hasattr(self, 'inports'):
            self.inports = {}
        self.inports[inport] = value

    def run(self):
        cmd = self._replace_inputs(self.cmd)
        ms = re.findall('(\{o:([^\}]+)(:([^\}]+))\})', cmd)
        for m in ms:
            cmd = cmd.replace(m[0], self.output()[m[1]].path)
        commands.getstatusoutput(cmd)
