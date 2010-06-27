#!/usr/bin/python

#Copyright 2008 Carl Gherardi
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU Affero General Public License as published by
#the Free Software Foundation, version 3 of the License.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU Affero General Public License
#along with this program. If not, see <http://www.gnu.org/licenses/>.
#In the "official" distribution you can find the license in
#agpl-3.0.txt in the docs folder of the package.

#fpdb modules
import Card
from decimal import Decimal

DEBUG = False

if DEBUG:
    import pprint
    pp = pprint.PrettyPrinter(indent=4)


class DerivedStats():
    def __init__(self, hand):
        self.hand = hand

        self.hands = {}
        self.handsplayers = {}

    def getStats(self, hand):
        
        for player in hand.players:
            self.handsplayers[player[1]] = {}
            #Init vars that may not be used, but still need to be inserted.
            # All stud street4 need this when importing holdem
            self.handsplayers[player[1]]['winnings']    = 0
            self.handsplayers[player[1]]['rake']        = 0
            self.handsplayers[player[1]]['totalProfit'] = 0
            self.handsplayers[player[1]]['street4Seen'] = False
            self.handsplayers[player[1]]['street4Aggr'] = False
            self.handsplayers[player[1]]['wonWhenSeenStreet1'] = 0.0
            self.handsplayers[player[1]]['sawShowdown'] = False
            self.handsplayers[player[1]]['wonAtSD']     = 0.0
            self.handsplayers[player[1]]['startCards']  = 0
            self.handsplayers[player[1]]['position']            = 2
            self.handsplayers[player[1]]['street0_3BChance']    = False
            self.handsplayers[player[1]]['street0_3BDone']      = False
            self.handsplayers[player[1]]['street0_4BChance']    = False
            self.handsplayers[player[1]]['street0_4BDone']      = False
            self.handsplayers[player[1]]['stealAttemptChance']  = False
            self.handsplayers[player[1]]['stealAttempted']      = False
            self.handsplayers[player[1]]['foldBbToStealChance'] = False
            self.handsplayers[player[1]]['foldSbToStealChance'] = False
            self.handsplayers[player[1]]['foldedSbToSteal']     = False
            self.handsplayers[player[1]]['foldedBbToSteal']     = False
            for i in range(5): 
                self.handsplayers[player[1]]['street%dCalls' % i] = 0
                self.handsplayers[player[1]]['street%dBets' % i] = 0
                self.handsplayers[player[1]]['street%dRaises' % i] = 0
            for i in range(1,5):
                self.handsplayers[player[1]]['street%dCBChance' %i] = False
                self.handsplayers[player[1]]['street%dCBDone' %i] = False
                self.handsplayers[player[1]]['street%dCheckCallRaiseChance' %i] = False
                self.handsplayers[player[1]]['street%dCheckCallRaiseDone' %i]   = False
                self.handsplayers[player[1]]['otherRaisedStreet%d' %i]          = False
                self.handsplayers[player[1]]['foldToOtherRaisedStreet%d' %i]    = False

            #FIXME - Everything below this point is incomplete.
            self.handsplayers[player[1]]['tourneyTypeId']       = 1
            for i in range(1,5):
                self.handsplayers[player[1]]['foldToStreet%dCBChance' %i]       = False
                self.handsplayers[player[1]]['foldToStreet%dCBDone' %i]         = False

        self.assembleHands(self.hand)
        self.assembleHandsPlayers(self.hand)


        if DEBUG:
            print "Hands:"
            pp.pprint(self.hands)
            print "HandsPlayers:"
            pp.pprint(self.handsplayers)

    def getHands(self):
        return self.hands

    def getHandsPlayers(self):
        return self.handsplayers

    def assembleHands(self, hand):
        self.hands['tableName']  = hand.tablename
        self.hands['siteHandNo'] = hand.handid
        self.hands['gametypeId'] = None                     # Leave None, handled later after checking db
        self.hands['handStart']  = hand.starttime           # format this!
        self.hands['importTime'] = None
        self.hands['seats']      = self.countPlayers(hand) 
        self.hands['maxSeats']   = hand.maxseats
        self.hands['texture']    = None                     # No calculation done for this yet.

        # This (i think...) is correct for both stud and flop games, as hand.board['street'] disappears, and
        # those values remain default in stud.
        boardcards = []
        for street in hand.communityStreets:
            boardcards += hand.board[street]
        boardcards += [u'0x', u'0x', u'0x', u'0x', u'0x']
        cards = [Card.encodeCard(c) for c in boardcards[0:5]]
        self.hands['boardcard1'] = cards[0]
        self.hands['boardcard2'] = cards[1]
        self.hands['boardcard3'] = cards[2]
        self.hands['boardcard4'] = cards[3]
        self.hands['boardcard5'] = cards[4]

        #print "DEBUG: self.getStreetTotals = (%s, %s, %s, %s, %s)" %  hand.getStreetTotals()
        totals = hand.getStreetTotals()
        totals = [int(100*i) for i in totals]
        self.hands['street1Pot']  = totals[0]
        self.hands['street2Pot']  = totals[1]
        self.hands['street3Pot']  = totals[2]
        self.hands['street4Pot']  = totals[3]
        self.hands['showdownPot'] = totals[4]

        self.vpip(hand) # Gives playersVpi (num of players vpip)
        #print "DEBUG: vpip: %s" %(self.hands['playersVpi'])
        self.playersAtStreetX(hand) # Gives playersAtStreet1..4 and Showdown
        #print "DEBUG: playersAtStreet 1:'%s' 2:'%s' 3:'%s' 4:'%s'" %(self.hands['playersAtStreet1'],self.hands['playersAtStreet2'],self.hands['playersAtStreet3'],self.hands['playersAtStreet4'])
        self.streetXRaises(hand) # Empty function currently

    def assembleHandsPlayers(self, hand):
        #street0VPI/vpip already called in Hand
        # sawShowdown is calculated in playersAtStreetX, as that calculation gives us a convenient list of names

        #hand.players = [[seat, name, chips],[seat, name, chips]]
        for player in hand.players:
            self.handsplayers[player[1]]['seatNo'] = player[0]
            self.handsplayers[player[1]]['startCash'] = int(100 * Decimal(player[2]))

        # XXX: enumerate(list, start=x) is python 2.6 syntax; 'start'
        #for i, street in enumerate(hand.actionStreets[2:], start=1):
        for i, street in enumerate(hand.actionStreets[2:]):
            self.seen(self.hand, i+1)

        for i, street in enumerate(hand.actionStreets[1:]):
            self.aggr(self.hand, i)
            self.calls(self.hand, i)
            self.bets(self.hand, i)
            if i>0:
                self.folds(self.hand, i)

        # Winnings is a non-negative value of money collected from the pot, which already includes the
        # rake taken out. hand.collectees is Decimal, database requires cents
        for player in hand.collectees:
            self.handsplayers[player]['winnings'] = int(100 * hand.collectees[player])
            #FIXME: This is pretty dodgy, rake = hand.rake/#collectees
            # You can really only pay rake when you collect money, but
            # different sites calculate rake differently.
            # Should be fine for split-pots, but won't be accurate for multi-way pots
            self.handsplayers[player]['rake'] = int(100* hand.rake)/len(hand.collectees)
            if self.handsplayers[player]['street1Seen'] == True:
                self.handsplayers[player]['wonWhenSeenStreet1'] = 1.0
            if self.handsplayers[player]['sawShowdown'] == True:
                self.handsplayers[player]['wonAtSD'] = 1.0

        for player in hand.pot.committed:
            self.handsplayers[player]['totalProfit'] = int(self.handsplayers[player]['winnings'] - (100*hand.pot.committed[player])- (100*hand.pot.common[player]))

        self.calcCBets(hand)

        for player in hand.players:
            hcs = hand.join_holecards(player[1], asList=True)
            hcs = hcs + [u'0x', u'0x', u'0x', u'0x', u'0x']
            #for i, card in enumerate(hcs[:7], 1): #Python 2.6 syntax
            #    self.handsplayers[player[1]]['card%s' % i] = Card.encodeCard(card)
            for i, card in enumerate(hcs[:7]):
                self.handsplayers[player[1]]['card%s' % (i+1)] = Card.encodeCard(card)
            self.handsplayers[player[1]]['startCards'] = Card.calcStartCards(hand, player[1])

        self.setPositions(hand)
        self.calcCheckCallRaise(hand)
        self.calc34BetStreet0(hand)
        self.calcSteals(hand)
        # Additional stats
        # 3betSB, 3betBB
        # Squeeze, Ratchet?


    def setPositions(self, hand):
        """Sets the position for each player in HandsPlayers
            any blinds are negative values, and the last person to act on the
            first betting round is 0
            NOTE: HU, both values are negative for non-stud games
            NOTE2: I've never seen a HU stud match"""
        # The position calculation must be done differently for Stud and other games as
        # Stud the 'blind' acts first - in all other games they act last.
        #
        #This function is going to get it wrong when there in situations where there
        # is no small blind. I can live with that.
        actions = hand.actions[hand.holeStreets[0]]
        # Note:  pfbao list may not include big blind if all others folded
        players = self.pfbao(actions)

        if hand.gametype['base'] == 'stud':
            positions = [7, 6, 5, 4, 3, 2, 1, 0, 'S', 'B']
            seats = len(players)
            map = []
            # Could posibly change this to be either -2 or -1 depending if they complete or bring-in
            # First player to act is -1, last player is 0 for 6 players it should look like:
            # ['S', 4, 3, 2, 1, 0]
            map = positions[-seats-1:-1] # Copy required positions from postions array anding in -1
            map = map[-1:] + map[0:-1] # and move the -1 to the start of that array

            for i, player in enumerate(players):
                #print "player %s in posn %s" % (player, str(map[i]))
                self.handsplayers[player]['position'] = map[i]
        else:
            # set blinds first, then others from pfbao list, avoids problem if bb
            # is missing from pfbao list or if there is no small blind
            bb = [x[0] for x in hand.actions[hand.actionStreets[0]] if x[2] == 'big blind']
            sb = [x[0] for x in hand.actions[hand.actionStreets[0]] if x[2] == 'small blind']
            # if there are > 1 sb or bb only the first is used!
            if bb:
                self.handsplayers[bb[0]]['position'] = 'B'
                if bb[0] in players:  players.remove(bb[0])
            if sb:
                self.handsplayers[sb[0]]['position'] = 'S'
                if sb[0] in players:  players.remove(sb[0])

            #print "bb =", bb, "sb =", sb, "players =", players
            for i,player in enumerate(reversed(players)):
                self.handsplayers[player]['position'] = i

    def assembleHudCache(self, hand):
        # No real work to be done - HandsPlayers data already contains the correct info
        pass

    def vpip(self, hand):
        vpipers = set()
        for act in hand.actions[hand.actionStreets[1]]:
            if act[1] in ('calls','bets', 'raises'):
                vpipers.add(act[0])

        self.hands['playersVpi'] = len(vpipers)

        for player in hand.players:
            if player[1] in vpipers:
                self.handsplayers[player[1]]['street0VPI'] = True
            else:
                self.handsplayers[player[1]]['street0VPI'] = False

    def playersAtStreetX(self, hand):
        """ playersAtStreet1 SMALLINT NOT NULL,   /* num of players seeing flop/street4/draw1 */"""
        # self.actions[street] is a list of all actions in a tuple, contining the player name first
        # [ (player, action, ....), (player2, action, ...) ]
        # The number of unique players in the list per street gives the value for playersAtStreetXXX

        # FIXME?? - This isn't couting people that are all in - at least showdown needs to reflect this
        #     ... new code below hopefully fixes this

        self.hands['playersAtStreet1']  = 0
        self.hands['playersAtStreet2']  = 0
        self.hands['playersAtStreet3']  = 0
        self.hands['playersAtStreet4']  = 0
        self.hands['playersAtShowdown'] = 0

#        alliners = set()
#        for (i, street) in enumerate(hand.actionStreets[2:]):
#            actors = set()
#            for action in hand.actions[street]:
#                if len(action) > 2 and action[-1]: # allin
#                    alliners.add(action[0])
#                actors.add(action[0])
#            if len(actors)==0 and len(alliners)<2:
#                alliners = set()
#            self.hands['playersAtStreet%d' % (i+1)] = len(set.union(alliners, actors))
#
#        actions = hand.actions[hand.actionStreets[-1]]
#        print "p_actions:", self.pfba(actions), "p_folds:", self.pfba(actions, l=('folds',)), "alliners:", alliners
#        pas = set.union(self.pfba(actions) - self.pfba(actions, l=('folds',)),  alliners)
        
        p_in = set(x[1] for x in hand.players)
        for (i, street) in enumerate(hand.actionStreets):
            actions = hand.actions[street]
            p_in = p_in - self.pfba(actions, l=('folds',))
            self.hands['playersAtStreet%d' % (i-1)] = len(p_in)
        
        self.hands['playersAtShowdown'] = len(p_in)

        if self.hands['playersAtShowdown'] > 1:
            for player in p_in:
                self.handsplayers[player]['sawShowdown'] = True

    def streetXRaises(self, hand):
        # self.actions[street] is a list of all actions in a tuple, contining the action as the second element
        # [ (player, action, ....), (player2, action, ...) ]
        # No idea what this value is actually supposed to be
        # In theory its "num small bets paid to see flop/street4, including blind" which makes sense for limit. Not so useful for nl
        # Leaving empty for the moment,

        for i in range(5): self.hands['street%dRaises' % i] = 0

        for (i, street) in enumerate(hand.actionStreets[1:]):
            self.hands['street%dRaises' % i] = len(filter( lambda action: action[1] in ('raises','bets'), hand.actions[street]))

    def calcSteals(self, hand):
        """Fills stealAttempt(Chance|ed, fold(Bb|Sb)ToSteal(Chance|)

        Steal attempt - open raise on positions 1 0 S - i.e. MP3, CO, BU, SB
                        (note: I don't think PT2 counts SB steals in HU hands, maybe we shouldn't?)
        Fold to steal - folding blind after steal attemp wo any other callers or raisers
        """
        steal_attempt = False
        steal_positions = (1, 0, 'S')
        if hand.gametype['base'] == 'stud':
            steal_positions = (2, 1, 0)
        for action in hand.actions[hand.actionStreets[1]]:
            pname, act = action[0], action[1]
            posn = self.handsplayers[pname]['position']
            #print "\naction:", action[0], posn, type(posn), steal_attempt, act
            if posn == 'B':
                #NOTE: Stud games will never hit this section
                self.handsplayers[pname]['foldBbToStealChance'] = steal_attempt
                self.handsplayers[pname]['foldedBbToSteal'] = steal_attempt and act == 'folds'
                break
            elif posn == 'S':
                self.handsplayers[pname]['foldSbToStealChance'] = steal_attempt
                self.handsplayers[pname]['foldedSbToSteal'] = steal_attempt and act == 'folds'

            if steal_attempt and act != 'folds':
                break

            if posn in steal_positions and not steal_attempt:
                self.handsplayers[pname]['stealAttemptChance'] = True
                if act in ('bets', 'raises'):
                    self.handsplayers[pname]['stealAttempted'] = True
                    steal_attempt = True
                if act == 'calls':
                    break
            
            if posn not in steal_positions and act != 'folds':
                break

    def calc34BetStreet0(self, hand):
        """Fills street0_(3|4)B(Chance|Done), other(3|4)BStreet0"""
        bet_level = 1 # bet_level after 3-bet is equal to 3
        for action in hand.actions[hand.actionStreets[1]]:
            # FIXME: fill other(3|4)BStreet0 - i have no idea what does it mean
            pname, aggr = action[0], action[1] in ('raises', 'bets')
            self.handsplayers[pname]['street0_3BChance'] = self.handsplayers[pname]['street0_3BChance'] or bet_level == 2
            self.handsplayers[pname]['street0_4BChance'] = bet_level == 3
            self.handsplayers[pname]['street0_3BDone'] =  self.handsplayers[pname]['street0_3BDone'] or (aggr and self.handsplayers[pname]['street0_3BChance'])
            self.handsplayers[pname]['street0_4BDone'] =  aggr and (self.handsplayers[pname]['street0_4BChance'])
            if aggr:
                bet_level += 1


    def calcCBets(self, hand):
        """Fill streetXCBChance, streetXCBDone, foldToStreetXCBDone, foldToStreetXCBChance

        Continuation Bet chance, action:
        Had the last bet (initiative) on previous street, got called, close street action
        Then no bets before the player with initiatives first action on current street
        ie. if player on street-1 had initiative and no donkbets occurred
        """
        # XXX: enumerate(list, start=x) is python 2.6 syntax; 'start'
        # came there
        #for i, street in enumerate(hand.actionStreets[2:], start=1):
        for i, street in enumerate(hand.actionStreets[2:]):
            name = self.lastBetOrRaiser(hand.actionStreets[i+1])
            if name:
                chance = self.noBetsBefore(hand.actionStreets[i+2], name)
                if chance == True:
                    self.handsplayers[name]['street%dCBChance' % (i+1)] = True
                    self.handsplayers[name]['street%dCBDone' % (i+1)] = self.betStreet(hand.actionStreets[i+2], name)

    def calcCheckCallRaise(self, hand):
        """Fill streetXCheckCallRaiseChance, streetXCheckCallRaiseDone

        streetXCheckCallRaiseChance = got raise/bet after check
        streetXCheckCallRaiseDone = checked. got raise/bet. didn't fold

        CG: CheckCall would be a much better name for this.
        """
        # XXX: enumerate(list, start=x) is python 2.6 syntax; 'start'
        #for i, street in enumerate(hand.actionStreets[2:], start=1):
        for i, street in enumerate(hand.actionStreets[2:]):
            actions = hand.actions[hand.actionStreets[i+1]]
            checkers = set()
            initial_raiser = None
            for action in actions:
                pname, act = action[0], action[1]
                if act in ('bets', 'raises') and initial_raiser is None:
                    initial_raiser = pname
                elif act == 'checks' and initial_raiser is None:
                    checkers.add(pname)
                elif initial_raiser is not None and pname in checkers:
                    self.handsplayers[pname]['street%dCheckCallRaiseChance' % (i+1)] = True
                    self.handsplayers[pname]['street%dCheckCallRaiseDone' % (i+1)] = act!='folds'

    def seen(self, hand, i):
        pas = set()
        for act in hand.actions[hand.actionStreets[i+1]]:
            pas.add(act[0])

        for player in hand.players:
            if player[1] in pas:
                self.handsplayers[player[1]]['street%sSeen' % i] = True
            else:
                self.handsplayers[player[1]]['street%sSeen' % i] = False

    def aggr(self, hand, i):
        aggrers = set()
        others = set()
        # Growl - actionStreets contains 'BLINDSANTES', which isn't actually an action street

        firstAggrMade=False
        for act in hand.actions[hand.actionStreets[i+1]]:
            if firstAggrMade:
                others.add(act[0])
            if act[1] in ('completes', 'bets', 'raises'):
                aggrers.add(act[0])
                firstAggrMade=True

        for player in hand.players:
            #print "DEBUG: actionStreet[%s]: %s" %(hand.actionStreets[i+1], i)
            if player[1] in aggrers:
                self.handsplayers[player[1]]['street%sAggr' % i] = True
            else:
                self.handsplayers[player[1]]['street%sAggr' % i] = False
                
        if len(aggrers)>0 and i>0:
            for playername in others:
                self.handsplayers[playername]['otherRaisedStreet%s' % i] = True
                #print "otherRaised detected on handid "+str(hand.handid)+" for "+playername+" on street "+str(i)

        if i > 0 and len(aggrers) > 0:
            for playername in others:
                self.handsplayers[playername]['otherRaisedStreet%s' % i] = True
                #print "DEBUG: otherRaised detected on handid %s for %s on actionStreet[%s]: %s" 
                #                           %(hand.handid, playername, hand.actionStreets[i+1], i)

    def calls(self, hand, i):
        callers = []
        for act in hand.actions[hand.actionStreets[i+1]]:
            if act[1] in ('calls'):
                self.handsplayers[act[0]]['street%sCalls' % i] = 1 + self.handsplayers[act[0]]['street%sCalls' % i]

    # CG - I'm sure this stat is wrong
    # Best guess is that raise = 2 bets
    def bets(self, hand, i):
        for act in hand.actions[hand.actionStreets[i+1]]:
            if act[1] in ('bets'):
                self.handsplayers[act[0]]['street%sBets' % i] = 1 + self.handsplayers[act[0]]['street%sBets' % i]
        
    def folds(self, hand, i):
        for act in hand.actions[hand.actionStreets[i+1]]:
            if act[1] in ('folds'):
                if self.handsplayers[act[0]]['otherRaisedStreet%s' % i] == True:
                    self.handsplayers[act[0]]['foldToOtherRaisedStreet%s' % i] = True
                    #print "DEBUG: fold detected on handid %s for %s on actionStreet[%s]: %s"
                    #                       %(hand.handid, act[0],hand.actionStreets[i+1], i)

    def countPlayers(self, hand):
        pass

    def pfba(self, actions, f=None, l=None):
        """Helper method. Returns set of PlayersFilteredByActions

        f - forbidden actions
        l - limited to actions
        """
        players = set()
        for action in actions:
            if l is not None and action[1] not in l: continue
            if f is not None and action[1] in f: continue
            players.add(action[0])
        return players

    def pfbao(self, actions, f=None, l=None, unique=True):
        """Helper method. Returns set of PlayersFilteredByActionsOrdered

        f - forbidden actions
        l - limited to actions
        """
        # Note, this is an adaptation of function 5 from:
        # http://www.peterbe.com/plog/uniqifiers-benchmark
        seen = {}
        players = []
        for action in actions:
            if l is not None and action[1] not in l: continue
            if f is not None and action[1] in f: continue
            if action[0] in seen and unique: continue
            seen[action[0]] = 1
            players.append(action[0])
        return players

    def firstsBetOrRaiser(self, actions):
        """Returns player name that placed the first bet or raise.

        None if there were no bets or raises on that street
        """
        for act in actions:
            if act[1] in ('bets', 'raises'):
                return act[0]
        return None

    def lastBetOrRaiser(self, street):
        """Returns player name that placed the last bet or raise for that street.
            None if there were no bets or raises on that street"""
        lastbet = None
        for act in self.hand.actions[street]:
            if act[1] in ('bets', 'raises'):
                lastbet = act[0]
        return lastbet


    def noBetsBefore(self, street, player):
        """Returns true if there were no bets before the specified players turn, false otherwise"""
        betOrRaise = False
        for act in self.hand.actions[street]:
            #Must test for player first in case UTG
            if act[0] == player:
                betOrRaise = True
                break
            if act[1] in ('bets', 'raises'):
                break
        return betOrRaise


    def betStreet(self, street, player):
        """Returns true if player bet/raised the street as their first action"""
        betOrRaise = False
        for act in self.hand.actions[street]:
            if act[0] == player:
                if act[1] in ('bets', 'raises'):
                    betOrRaise = True
                else:
                    # player found but did not bet or raise as their first action
                    pass
                break
            #else:
                # haven't found player's first action yet
        return betOrRaise

