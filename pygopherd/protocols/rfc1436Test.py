import unittest, re
from pygopherd.protocols.rfc1436 import GopherProtocol
from pygopherd import testutil
from io import BytesIO

class RFC1436TestCase(unittest.TestCase):
    def setUp(self):
        self.config = testutil.getconfig()
        self.rfile = BytesIO(b"/testfile.txt\n")
        self.wfile = BytesIO()
        self.logfile = testutil.getstringlogger()
        self.handler = testutil.gettestinghandler(self.rfile, self.wfile,
                                                  self.config)
        self.server = self.handler.server
        self.proto = GopherProtocol("/testfile.txt\n", self.server,
                                    self.handler, self.rfile, self.wfile,
                                    self.config)

    def testcanhandlerequest(self):
        assert self.proto.canhandlerequest()
        proto = GopherProtocol("/testfile.txt\tsearch\n",
                               self.server, self.handler, self.rfile,
                               self.wfile, self.config)
        assert proto.canhandlerequest()
        self.assertEqual(proto.selector, '/testfile.txt')
        self.assertEqual(proto.searchrequest, "search")

    def testrenderobjinfo(self):
        expected = "0testfile.txt\t/testfile.txt\t%s\t%d\t+\r\n" % \
                   (self.server.server_name, self.server.server_port)
        self.assertEqual(self.proto.renderobjinfo(self.proto.gethandler().getentry()),
                          expected)

    def testhandle_file(self):
        self.proto.handle()
        self.assertEqual(self.logfile.getvalue(),
                          b"10.77.77.77 [GopherProtocol/FileHandler]: /testfile.txt\n")
        self.assertEqual(self.wfile.getvalue(), b"Test\n")

    def testhandle_dir_abstracts(self):
        proto = GopherProtocol("", self.server, self.handler, self.rfile,
                               self.wfile, self.config)
        proto.handle()
        self.assertEqual(proto.selector, '/')
        self.assertEqual(self.logfile.getvalue(),
                          "10.77.77.77 [GopherProtocol/UMNDirHandler]: /\n")
        # Try to make this easy on us to fix.
        actualarr = self.wfile.getvalue().decode('ascii').splitlines()
        expectedarr = [
'iThis is the abstract for the testdata directory.\tfake\t(NULL)\t0',
'0README\t/README\tHOSTNAME\t64777\t+',
'1pygopherd\t/pygopherd\tHOSTNAME\t64777\t+',
'9symlinktest\t/symlinktest.zip\tHOSTNAME\t64777\t+',
'9testarchive\t/testarchive.tar\tHOSTNAME\t64777\t+',
'9testarchive.tar.gz\t/testarchive.tar.gz\tHOSTNAME\t64777\t+',
'9testarchive.tgz\t/testarchive.tgz\tHOSTNAME\t64777\t+',
'9testdata\t/testdata.zip\tHOSTNAME\t64777\t+',
'9testdata2\t/testdata2.zip\tHOSTNAME\t64777\t+',
'0testfile\t/testfile.txt\tHOSTNAME\t64777\t+',
'9testfile.txt.gz\t/testfile.txt.gz\tHOSTNAME\t64777\t+',
'iThis is the abstract\tfake\t(NULL)\t0',
'ifor testfile.txt.gz\tfake\t(NULL)\t0',
'9ziptorture\t/ziptorture.zip\tHOSTNAME\t64777\t+']
        expectedarr = [re.sub('HOSTNAME', self.server.server_name, x) for \
                      x in expectedarr]
        self.assertEqual(len(actualarr), len(expectedarr), str(actualarr))
        for i in range(len(actualarr)):
            self.assertEqual(actualarr[i], expectedarr[i])
        # Make sure proper line endings are present.
        self.assertEqual("\r\n".join(actualarr) + "\r\n", self.wfile.getvalue())

    def testhandle_dir_noabstract(self):
        self.config.set("pygopherd", "abstract_headers", "off")
        self.config.set("pygopherd", "abstract_entries", "off")
        proto = GopherProtocol("", self.server, self.handler, self.rfile,
                               self.wfile, self.config)
        proto.handle()
        actualarr = self.wfile.getvalue().splitlines()
        expectedarr = \
             ['0README\t/README\tHOSTNAME\t64777\t+',
              '1pygopherd\t/pygopherd\tHOSTNAME\t64777\t+',
              '9symlinktest\t/symlinktest.zip\tHOSTNAME\t64777\t+',
              '9testarchive\t/testarchive.tar\tHOSTNAME\t64777\t+',
              '9testarchive.tar.gz\t/testarchive.tar.gz\tHOSTNAME\t64777\t+',
              '9testarchive.tgz\t/testarchive.tgz\tHOSTNAME\t64777\t+',
              '9testdata\t/testdata.zip\tHOSTNAME\t64777\t+',
              '9testdata2\t/testdata2.zip\tHOSTNAME\t64777\t+',
              '0testfile\t/testfile.txt\tHOSTNAME\t64777\t+',
              '9testfile.txt.gz\t/testfile.txt.gz\tHOSTNAME\t64777\t+',
              '9ziptorture\t/ziptorture.zip\tHOSTNAME\t64777\t+']
        expectedarr = [re.sub('HOSTNAME', self.server.server_name, x) for \
                       x in expectedarr]
        self.assertEqual(len(actualarr), len(expectedarr))
        for i in range(len(actualarr)):
            self.assertEqual(actualarr[i], expectedarr[i])

