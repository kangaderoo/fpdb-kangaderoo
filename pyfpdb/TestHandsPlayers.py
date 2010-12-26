#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    Copyright 2010, Carl Gherardi
#    
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#    
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#    
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
########################################################################

import sys
import os
import codecs
import pprint
import PokerStarsToFpdb
from Hand import *
import Configuration
import Database
import SQL
import fpdb_import
import Options
import datetime
import pytz


class FpdbError:
    def __init__(self, sitename):
        self.site = sitename
        self.errorcount = 0
        self.histogram = {}
        self.statcount = {}

    def error_report(self, filename, hand, stat, ghash, testhash, player):
        print "Regression Test Error:"
        print "\tFile: %s" % filename
        print "\tStat: %s" % stat
        print "\tPlayer: %s" % player
        if filename in self.histogram:
            self.histogram[filename] += 1
        else:
            self.histogram[filename] = 1

        if stat in self.statcount:
            self.statcount[stat] += 1
        else:
            self.statcount[stat] = 1
        self.errorcount += 1

    def print_histogram(self):
        print "%s:" % self.site
        for f in self.histogram:
            idx = f.find('regression')
            print "(%3d) : %s" %(self.histogram[f], f[idx:])

def compare_handsplayers_file(filename, importer, errors):
    hashfilename = filename + '.hp'

    in_fh = codecs.open(hashfilename, 'r', 'utf8')
    whole_file = in_fh.read()
    in_fh.close()

    testhash = eval(whole_file)

    hhc = importer.getCachedHHC()
    handlist = hhc.getProcessedHands()
    #We _really_ only want to deal with a single hand here.
    for hand in handlist:
        ghash = hand.stats.getHandsPlayers()
        for p in ghash:
            #print "DEBUG: player: '%s'" % p
            pstat = ghash[p]
            teststat = testhash[p]

            for stat in pstat:
                #print "pstat[%s][%s]: %s == %s" % (p, stat, pstat[stat], teststat[stat])
                try:
                    if pstat[stat] == teststat[stat]:
                        # The stats match - continue
                        pass
                    else:
                        # Stats don't match - Doh!
                        errors.error_report(filename, hand, stat, ghash, testhash, p)
                except KeyError, e:
                    errors.error_report(filename, False, "KeyError: '%s'" % stat, False, False, p)

def compare_hands_file(filename, importer, errors):
    hashfilename = filename + '.hands'

    in_fh = codecs.open(hashfilename, 'r', 'utf8')
    whole_file = in_fh.read()
    in_fh.close()

    testhash = eval(whole_file)

    hhc = importer.getCachedHHC()
    handlist = hhc.getProcessedHands()

    for hand in handlist:
        ghash = hand.stats.getHands()
        for datum in ghash:
            #print "DEBUG: hand: '%s'" % datum
            try:
                if ghash[datum] == testhash[datum]:
                    # The stats match - continue
                    pass
                else:
                    # Stats don't match. 
                    if datum == "gametypeId":
                        # Not an error. gametypeIds are dependent on the order added to the db.
                        #print "DEBUG: Skipping mismatched gamtypeId"
                        pass
                    else:
                        errors.error_report(filename, hand, datum, ghash, testhash, None)
            except KeyError, e:
                errors.error_report(filename, False, "KeyError: '%s'" % stat, False, False, p)


def compare(leaf, importer, errors, site):
    filename = leaf
    #print "DEBUG: fileanme: %s" % filename

    # Test if this is a hand history file
    if filename.endswith('.txt'):
        # test if there is a .hp version of the file
        importer.addBulkImportImportFileOrDir(filename, site=site)
        (stored, dups, partial, errs, ttime) = importer.runImport()

        if errs > 0:
            errors.error_report(filename, False, "Parse", False, False, False)
        else:
            if os.path.isfile(filename + '.hp'):
                compare_handsplayers_file(filename, importer, errors)
            if os.path.isfile(filename + '.hands'):
                compare_hands_file(filename, importer, errors)

        importer.clearFileList()



def walk_testfiles(dir, function, importer, errors, site):
    """Walks a directory, and executes a callback on each file """
    dir = os.path.abspath(dir)
    for file in [file for file in os.listdir(dir) if not file in [".",".."]]:
        nfile = os.path.join(dir,file)
        if os.path.isdir(nfile):
            walk_testfiles(nfile, compare, importer, errors, site)
        else:
            compare(nfile, importer, errors, site)

def usage():
    print "USAGE:"
    sys.exit(0)

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    (options, argv) = Options.fpdb_options()

    test_all_sites = True

    if options.usage == True:
        usage()

    if options.sitename:
        options.sitename = Options.site_alias(options.sitename)
        if options.sitename == False:
            usage()
        print "Only regression testing '%s' files" % (options.sitename)
        test_all_sites = False

    config = Configuration.Config(file = "HUD_config.test.xml")
    db = Database.Database(config)
    sql = SQL.Sql(db_server = 'sqlite')
    settings = {}
    settings.update(config.get_db_parameters())
    settings.update(config.get_import_parameters())
    settings.update(config.get_default_paths())
    db.recreate_tables()
    importer = fpdb_import.Importer(False, settings, config, None)
    importer.setDropIndexes("don't drop")
    importer.setFailOnError(True)
    importer.setThreads(-1)
    importer.setCallHud(False)
    importer.setFakeCacheHHC(True)

    PokerStarsErrors  = FpdbError('PokerStars')
    FTPErrors         = FpdbError('Full Tilt Poker')
    PartyPokerErrors  = FpdbError('Party Poker')
    BetfairErrors     = FpdbError('Betfair')
    OnGameErrors      = FpdbError('OnGame')
    AbsoluteErrors    = FpdbError('Absolute Poker')
    UltimateBetErrors = FpdbError('Ultimate Bet')
    EverleafErrors    = FpdbError('Everleaf Poker')
    CarbonErrors      = FpdbError('Carbon')
    PKRErrors         = FpdbError('PKR')
    iPokerErrors      = FpdbError('iPoker')
    Win2dayErrors     = FpdbError('Win2day')
    WinamaxErrors     = FpdbError('Winamax')

    ErrorsList = [
                    PokerStarsErrors, FTPErrors, PartyPokerErrors,
                    BetfairErrors, OnGameErrors, AbsoluteErrors,
                    EverleafErrors, CarbonErrors, PKRErrors,
                    iPokerErrors, WinamaxErrors, UltimateBetErrors,
                    Win2dayErrors,
                ]

    sites = {
                'PokerStars' : False,
                'Full Tilt Poker' : False,
                'PartyPoker' : False,
                'Betfair' : False,
                'OnGame' : False,
                'Absolute' : False,
                'UltimateBet' : False,
                'Everleaf' : False,
                'Carbon' : False,
                #'PKR' : False,
                'iPoker' : False,
                'Win2day' : False,
                'Winamax' : False,
            }

    if test_all_sites == True:
        for s in sites:
            sites[s] = True
    else:
        sites[options.sitename] = True

    if sites['PokerStars'] == True:
        walk_testfiles("regression-test-files/cash/Stars/", compare, importer, PokerStarsErrors, "PokerStars")
        walk_testfiles("regression-test-files/tour/Stars/", compare, importer, PokerStarsErrors, "PokerStars")
    if sites['Full Tilt Poker'] == True:
        walk_testfiles("regression-test-files/cash/FTP/", compare, importer, FTPErrors, "Full Tilt Poker")
        walk_testfiles("regression-test-files/tour/FTP/", compare, importer, FTPErrors, "Full Tilt Poker")
    if sites['PartyPoker'] == True:
        walk_testfiles("regression-test-files/cash/PartyPoker/", compare, importer, PartyPokerErrors, "PartyPoker")
        walk_testfiles("regression-test-files/tour/PartyPoker/", compare, importer, PartyPokerErrors, "PartyPoker")
    if sites['Betfair'] == True:
        walk_testfiles("regression-test-files/cash/Betfair/", compare, importer, BetfairErrors, "Betfair")
    if sites['OnGame'] == True:
        walk_testfiles("regression-test-files/cash/OnGame/", compare, importer, OnGameErrors, "OnGame")
    if sites['Absolute'] == True:
        walk_testfiles("regression-test-files/cash/Absolute/", compare, importer, AbsoluteErrors, "Absolute")
    if sites['UltimateBet'] == True:
        walk_testfiles("regression-test-files/cash/UltimateBet/", compare, importer, UltimateBetErrors, "Absolute")
    if sites['Everleaf'] == True:
        walk_testfiles("regression-test-files/cash/Everleaf/", compare, importer, EverleafErrors, "Everleaf")
    if sites['Carbon'] == True:
        walk_testfiles("regression-test-files/cash/Carbon/", compare, importer, CarbonErrors, "Carbon")
    #if sites['PKR'] == True:
    #    walk_testfiles("regression-test-files/cash/PKR/", compare, importer, PKRErrors, "PKR")
    if sites['iPoker'] == True:
        walk_testfiles("regression-test-files/cash/iPoker/", compare, importer, iPokerErrors, "iPoker")
    if sites['Winamax'] == True:
        walk_testfiles("regression-test-files/cash/Winamax/", compare, importer, WinamaxErrors, "Winamax")
        walk_testfiles("regression-test-files/tour/Winamax/", compare, importer, WinamaxErrors, "Winamax")
    if sites['Win2day'] == True:
        walk_testfiles("regression-test-files/cash/Win2day/", compare, importer, Win2dayErrors, "Win2day")

    totalerrors = 0

    for i, site in enumerate(ErrorsList):
        totalerrors += ErrorsList[i].errorcount

    print "---------------------"
    print "Total Errors: %d" % totalerrors
    print "---------------------"
    for i, site in enumerate(ErrorsList):
        ErrorsList[i].print_histogram()

    # Merge the dicts of stats from the various error objects
    statdict = {}
    for i, site in enumerate(ErrorsList):
        tmp = ErrorsList[i].statcount
        for stat in tmp:
            if stat in statdict:
                statdict[stat] += tmp[stat]
            else:
                statdict[stat] = tmp[stat]

    print "\n"
    print "---------------------"
    print "Errors by stat:"
    print "---------------------"
    #for stat in statdict:
    #    print "(%3d) : %s" %(statdict[stat], stat)

    sortedstats = sorted([(value,key) for (key,value) in statdict.items()])
    for num, stat in sortedstats:
        print "(%3d) : %s" %(num, stat)


if __name__ == '__main__':
    sys.exit(main())

