i = sys.argv[1]

# Tasks
grep = fw.ShellTask('cat {i:rawdata} | grep hej > {o:grepped:{i:rawdata}.grepped}')
copy = fw.ShellTask('cp {i:orig} {o:copy}.2')

# Workflow
copy.in("orig") = grep.out("grepped")

# Send in our specific indata
grep.in('rawdata') = luigi.LocalTarget(sys.argv[1])

if __name__ == '__main__':
    luigi.run()
