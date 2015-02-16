import commands
import luigi
import random
import re
import time

# Convenience methods
def shell(cmd):
    # We have to add a unique id, since we sometimes have multiple
    # tasks with the same command (which is the only real parameter)
    # to ShellTask
    cmd = re.sub('\s+', ' ', cmd.strip('\n ').replace('\n', ' ').replace('\\',''))
    random_id = str(random.random())[2:]
    return ShellTask(cmd=cmd, id=random_id)

def file(file_spec):
    return shell('# <o:' + file_spec + '>')

# Task classes
class AFile(luigi.ExternalTask):
    filename = luigi.Parameter()
    def requires(self):
        return luigi.LocalTarget(self.filename)

class ShellTask(luigi.Task):
    cmd = luigi.Parameter()
    id = luigi.Parameter()

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
        ms = re.findall('(\<i:([^\>\:]+)(:([^\>\|]+)\|([^\>]+))?\>)', cmd)
        for m in ms:
            if m[2] != '':
                # Replace according to replacement syntax
                new_path = re.sub('%s$' % m[3], m[4], self.get_input(m[1]).path)
                cmd = cmd.replace(m[0], new_path)
            else:
                cmd = cmd.replace(m[0], self.get_input(m[1]).path)
        return cmd

    def _find_outputs(self, cmd):
        return re.findall('(\<o:([^\>]+)(:([^\>]+))\>)', cmd)

    def output(self):
        cmd = self._replace_inputs(self.cmd)
        ms = self._find_outputs(cmd)
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
        ms = self._find_outputs(cmd)
        for m in ms:
            cmd = cmd.replace(m[0], self.output()[m[1]].path)
        print("****** NOW RUNNING COMMAND ******: " + cmd)
        # Remove any trailing comments in the line
        cmd = re.sub('(\ )?\#.*$', '', cmd)
        print commands.getstatusoutput(cmd)

class WorkflowTask(luigi.Task):
    def output(self):
        timestamp = time.strftime('%Y%m%d.%H%M%S', time.localtime())
        return luigi.LocalTarget('workflow.complete.{t}'.format(t=timestamp))

    def run(self):
        timestamp = time.strftime('%Y%m%d.%H%M%S', time.localtime())
        with self.output().open('w') as outfile:
            outfile.write('workflow finished at {t}'.format(t=timestamp))
