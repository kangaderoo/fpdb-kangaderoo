import os
import re
import codecs
import Options
import HandHistoryConverter
import Configuration
import sys

(options, argv) = Options.fpdb_options()
config = Configuration.Config()

filter = options.hhc

filter_name = filter.replace("ToFpdb", "")

mod = __import__(filter)
obj = getattr(mod, filter_name, None)

hhc = obj(config, autostart=False)

if os.path.exists(options.infile):
    in_fh = codecs.open(options.infile, 'r', "utf8")
    filecontents = in_fh.read()
    in_fh.close()
else:
    print "Could not find file %s" % options.infile
    exit(1)

m = hhc.re_PlayerInfo.finditer(filecontents)

outfile = options.infile+".anon"
print "Output being written to", outfile

savestdout = sys.stdout
fsock = open(outfile,"w")
sys.stdout = fsock

players = []
for a in m:
    players = players + [a.group('PNAME')]

uniq = set(players)

for i, name in enumerate(uniq):
    filecontents = filecontents.replace(name, 'Player%d' %i)

print filecontents

sys.stdout = savestdout
fsock.close()

