#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Manage collecting and formatting of stats and tooltips.
"""
#    Copyright 2008-2010, Ray E. Barker

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

#    How to write a new stat:
#        0  Do not use a name like "xyz_2". Names ending in _ and a single digit are
#           used to indicate the number of decimal places the user wants to see in the Hud.
#        1  You can see a listing of all the raw stats (e.g., from the HudCache table)
#           by running Database.py as a stand along program.  You need to combine 
#           those raw stats to get stats to present to the HUD.  If you need more 
#           information than is in the HudCache table, then you have to write SQL.
#        2  The raw stats seen when you run Database.py are available in the Stats.py
#           in the stat_dict dict.  For example the number of vpips would be
#           stat_dict[player]['vpip'].  So the % vpip is 
#           float(stat_dict[player]['vpip'])/float(stat_dict[player]['n']).  You can see how the 
#           keys of stat_dict relate to the column names in HudCache by inspecting
#           the proper section of the SQL.py module.
#           The stat_dict keys should be in lower case, i.e. vpip not VPIP, since
#           postgres returns the column names in lower case.
#        3  You have to write a small function for each stat you want to add.  See
#           the vpip() function for example.  This function has to be protected from
#           exceptions, using something like the try:/except: paragraphs in vpip.
#        4  The name of the function has to be the same as the of the stat used
#           in the config file.
#        5  The stat functions have a peculiar return value, which is outlined in
#           the do_stat function.  This format is useful for tool tips and maybe
#           other stuff.
#        6  For each stat you make add a line to the __main__ function to test it.

import L10n
_ = L10n.get_translation()

#    Standard Library modules
import sys

#    pyGTK modules
import pygtk
import gtk
import re

#    FreePokerTools modules
import Configuration
import Database
import Charset

import logging
# logging has been set up in fpdb.py or HUD_main.py, use their settings:
log = logging.getLogger("db")


re_Places = re.compile("_[0-9]$")

# String manipulation
import codecs
encoder = codecs.lookup(Configuration.LOCALE_ENCODING)


# Since tuples are immutable, we have to create a new one when
# overriding any decimal placements. Copy old ones and recreate the
# second value in tuple to specified format-
def __stat_override(decimals, stat_vals):
    s = '%.*f' % (decimals, 100.0*stat_vals[0])
    res = (stat_vals[0], s, stat_vals[2],
            stat_vals[3], stat_vals[4], stat_vals[5])
    return res


def do_tip(widget, tip):
    _tip = Charset.to_utf8(tip)
    widget.set_tooltip_text(_tip)


def do_stat(stat_dict, player = 24, stat = 'vpip'):
    statname = stat
    match = re_Places.search(stat)
    if match:   # override if necessary
        statname = stat[0:-2]

    result = eval("%(stat)s(stat_dict, %(player)d)" % {'stat': statname, 'player': player})

    # If decimal places have been defined, override result[1]
    # NOTE: decimal place override ALWAYS assumes the raw result is a
    # fraction (x/100); manual decimal places really only make sense for
    # percentage values. Also, profit/100 hands (bb/BB) already default
    # to three decimal places anyhow, so they are unlikely override
    # candidates.
    if match:
        places = int(stat[-1:])
        result = __stat_override(places, result)
    return result

#    OK, for reference the tuple returned by the stat is:
#    0 - The stat, raw, no formating, eg 0.33333333
#    1 - formatted stat with appropriate precision, eg. 33; shown in HUD
#    2 - formatted stat with appropriate precision, punctuation and a hint, eg v=33%
#    3 - same as #2 except name of stat instead of hint, eg vpip=33%
#    4 - the calculation that got the stat, eg 9/27
#    5 - the name of the stat, useful for a tooltip, eg vpip

########################################### 
#    functions that return individual stats

def totalprofit(stat_dict, player):
    """    Total Profit."""
    if stat_dict[player]['net'] != 0:
        stat = float(stat_dict[player]['net']) / 100
        return (stat, '$%.2f' % stat, 'tp=$%.2f' % stat, 'totalprofit=$%.2f' % stat, str(stat), _('Total Profit'))
    return ('0', '$0.00', 'tp=0', 'totalprofit=0', '0', _('Total Profit'))

def playername(stat_dict, player):
    """    Player Name."""
    return (stat_dict[player]['screen_name'],
            stat_dict[player]['screen_name'],
            stat_dict[player]['screen_name'],
            stat_dict[player]['screen_name'],
            stat_dict[player]['screen_name'],
            stat_dict[player]['screen_name'])

def vpip(stat_dict, player):
    """    Voluntarily put $ in the pot pre-flop."""
    stat = 0.0
    try:
        stat = float(stat_dict[player]['vpip'])/float(stat_dict[player]['n'])
        return (stat,
                '%3.1f'         % (100.0*stat),
                'v=%3.1f%%'     % (100.0*stat),
                'vpip=%3.1f%%'  % (100.0*stat),
                '(%d/%d)'       % (stat_dict[player]['vpip'], stat_dict[player]['n']),
                _('Voluntarily Put In Pot Pre-Flop%')
                )
    except: return (stat,
                    'NA',
                    'v=NA',
                    'vpip=NA',
                    '(0/0)',
                    _('Voluntarily Put In Pot Pre-Flop%')
                    )

def pfr(stat_dict, player):
    """    Preflop (3rd street) raise."""
    stat = 0.0
    try:
        stat = float(stat_dict[player]['pfr'])/float(stat_dict[player]['n'])
        return (stat,
                '%3.1f'         % (100.0*stat),
                'p=%3.1f%%'     % (100.0*stat),
                'pfr=%3.1f%%'   % (100.0*stat),
                '(%d/%d)'    % (stat_dict[player]['pfr'], stat_dict[player]['n']),
                _('Pre-Flop Raise %')
                )
    except: 
        return (stat,
                'NA',
                'p=NA',
                'pfr=NA',
                '(0/0)',
                _('Pre-Flop Raise %')
                )

def wtsd(stat_dict, player):
    """    Went to SD when saw flop/4th."""
    stat = 0.0
    try:
        stat = float(stat_dict[player]['sd'])/float(stat_dict[player]['saw_f'])
        return (stat,
                '%3.1f'         % (100.0*stat),
                'w=%3.1f%%'     % (100.0*stat),
                'wtsd=%3.1f%%'  % (100.0*stat),
                '(%d/%d)'       % (stat_dict[player]['sd'], stat_dict[player]['saw_f']),
                _('% went to showdown')
                )
    except:
        return (stat,
                'NA',
                'w=NA',
                'wtsd=NA',
                '(0/0)',
                _('% went to showdown')
                )

def wmsd(stat_dict, player):
    """    Won $ at showdown."""
    stat = 0.0
    try:
        stat = float(stat_dict[player]['wmsd'])/float(stat_dict[player]['sd'])
        return (stat,
                '%3.1f'         % (100.0*stat),
                'w=%3.1f%%'     % (100.0*stat),
                'wmsd=%3.1f%%'  % (100.0*stat),
                '(%5.1f/%d)'    % (float(stat_dict[player]['wmsd']), stat_dict[player]['sd']),
                _('% won money at showdown')
                )
    except:
        return (stat,
                'NA',
                'w=NA',
                'wmsd=NA',
                '(0/0)',
                _('% won money at showdown')
                )

# Money is stored as pennies, so there is an implicit 100-multiplier
# already in place
def profit100(stat_dict, player):
    """    Profit won per 100 hands."""
    stat = 0.0
    try:
        stat = float(stat_dict[player]['net'])/float(stat_dict[player]['n'])
        return (stat,
                '%.2f'          % (stat),
                'p=%.2f'        % (stat),
                'p/100=%.2f'    % (stat),
                '%d/%d' % (stat_dict[player]['net'], stat_dict[player]['n']),
                _('profit/100hands')
                )
    except:
            print _("exception calcing p/100: 100 * %d / %d") % (stat_dict[player]['net'], stat_dict[player]['n'])
            return (stat,
                    'NA',
                    'p=NA',
                    'p/100=NA',
                    '(0/0)',
                    _('profit/100hands')
                    )

def bbper100(stat_dict, player):
    """    big blinds won per 100 hands."""
    stat = 0.0
    try:
        stat = 100.0 * float(stat_dict[player]['net']) / float(stat_dict[player]['bigblind'])
        return (stat,
                '%5.3f'         % (stat),
                'bb100=%5.3f'   % (stat),
                'bb100=%5.3f'   % (stat),
                '(%d,%d)'       % (100*stat_dict[player]['net'],stat_dict[player]['bigblind']),
                _('big blinds/100 hands')
                )
    except:
        log.info("exception calcing bb/100: "+str(stat_dict[player]))
        return (stat,
                'NA',
                'bb100=NA',
                'bb100=NA',
                '(--)',
                _('big blinds/100 hands')
                )

def BBper100(stat_dict, player):
    """    Big Bets won per 100 hands."""
    stat = 0.0
    try:
        stat = 50 * float(stat_dict[player]['net']) / float(stat_dict[player]['bigblind'])
        return (stat,
                '%5.3f'         % (stat),
                'BB100=%5.3f'   % (stat),
                'BB100=%5.3f'   % (stat),
                '(%d,%d)'       % (100*stat_dict[player]['net'],2*stat_dict[player]['bigblind']),
                _('Big Bets/100 hands')
                )
    except:
        log.info(_("exception calcing BB/100: ")+str(stat_dict[player]))
        return (stat,
                'NA',
                'BB100=NA',
                'BB100=NA',
                '(--)',
                _('Big Bets/100 hands')
                )

def saw_f(stat_dict, player):
    """    Saw flop/4th."""
    try:
        num = float(stat_dict[player]['saw_f'])
        den = float(stat_dict[player]['n'])
        stat = num/den
        return (stat,
            '%3.1f'         % (100.0*stat),
            'sf=%3.1f%%'    % (100.0*stat),
            'saw_f=%3.1f%%' % (100.0*stat),
            '(%d/%d)'       % (stat_dict[player]['saw_f'], stat_dict[player]['n']),
            _('Flop Seen %')
            )
    except:
        stat = 0.0
        return (stat,
            'NA',
            'sf=NA',
            'saw_f=NA',
            '(0/0)',
            _('Flop Seen %')
            )

def n(stat_dict, player):
    """    Number of hands played."""
    try:
        # If sample is large enough, use X.Yk notation instead
        _n = stat_dict[player]['n']
        fmt = '%d' % _n
        if _n >= 10000:
            k = _n / 1000
            c = _n % 1000
            _c = float(c) / 100.0
            d = int(round(_c))
            if d == 10:
                k += 1
                d = 0
            fmt = '%d.%dk' % (k, d)
        return (stat_dict[player]['n'],
                '%s'        % fmt,
                'n=%d'      % (stat_dict[player]['n']),
                'n=%d'      % (stat_dict[player]['n']),
                '(%d)'      % (stat_dict[player]['n']),
                _('number hands seen')
                )
    except:
        # Number of hands shouldn't ever be "NA"; zeroes are better here
        return (0,
                '%d'        % (0),
                'n=%d'      % (0),
                'n=%d'      % (0),
                '(%d)'      % (0),
                _('number hands seen')
                )
    
def fold_f(stat_dict, player):
    """    Folded flop/4th."""
    stat = 0.0
    try:
        stat = float(stat_dict[player]['fold_2'])/float(stat_dict[player]['saw_f'])
        return (stat,
                '%3.1f'             % (100.0*stat),
                'ff=%3.1f%%'        % (100.0*stat),
                'fold_f=%3.1f%%'    % (100.0*stat),
                '(%d/%d)'           % (stat_dict[player]['fold_2'], stat_dict[player]['saw_f']),
                _('folded flop/4th')
                )
    except:
        return (stat,
                'NA',
                'ff=NA',
                'fold_f=NA',
                '(0/0)',
                _('folded flop/4th')
                )
           
def steal(stat_dict, player):
    """    Steal %."""
    stat = 0.0
    try:
        stat = float(stat_dict[player]['steal'])/float(stat_dict[player]['steal_opp'])
        return (stat,
                '%3.1f'         % (100.0*stat),
                'st=%3.1f%%'    % (100.0*stat),
                'steal=%3.1f%%' % (100.0*stat),
                '(%d/%d)'       % (stat_dict[player]['steal'], stat_dict[player]['steal_opp']),
                _('% steal attempted')
                )
    except:
        return (stat, 'NA', 'st=NA', 'steal=NA', '(0/0)', '% steal attempted')

def f_SB_steal(stat_dict, player):
    """    Folded SB to steal."""
    stat = 0.0
    try:
        stat = float(stat_dict[player]['sbnotdef'])/float(stat_dict[player]['sbstolen'])
        return (stat,
                '%3.1f'         % (100.0*stat),
                'fSB=%3.1f%%'   % (100.0*stat),
                'fSB_s=%3.1f%%' % (100.0*stat),
                '(%d/%d)'       % (stat_dict[player]['sbnotdef'], stat_dict[player]['sbstolen']),
                _('% folded SB to steal'))
    except:
        return (stat,
                'NA',
                'fSB=NA',
                'fSB_s=NA',
                '(0/0)',
                _('% folded SB to steal'))

def f_BB_steal(stat_dict, player):
    """    Folded BB to steal."""
    stat = 0.0
    try:
        stat = float(stat_dict[player]['bbnotdef'])/float(stat_dict[player]['bbstolen'])
        return (stat,
                '%3.1f'         % (100.0*stat),
                'fBB=%3.1f%%'   % (100.0*stat),
                'fBB_s=%3.1f%%' % (100.0*stat),
                '(%d/%d)'       % (stat_dict[player]['bbnotdef'], stat_dict[player]['bbstolen']),
                _('% folded BB to steal'))
    except:
        return (stat,
                'NA',
                'fBB=NA',
                'fBB_s=NA',
                '(0/0)',
                _('% folded BB to steal'))
                
def f_steal(stat_dict, player):
    """    Folded blind to steal."""
    stat = 0.0
    try:
        folded_blind = stat_dict[player]['sbnotdef'] + stat_dict[player]['bbnotdef']
        blind_stolen = stat_dict[player]['sbstolen'] + stat_dict[player]['bbstolen']
        
        stat = float(folded_blind)/float(blind_stolen)
        return (stat,
                '%3.1f'         % (100.0*stat),
                'fB=%3.1f%%'    % (100.0*stat),
                'fB_s=%3.1f%%'  % (100.0*stat),
                '(%d/%d)'       % (folded_blind, blind_stolen),
                _('% folded blind to steal'))
    except:
        return (stat,
                'NA',
                'fB=NA',
                'fB_s=NA',
                '(0/0)',
                _('% folded blind to steal'))

def three_B(stat_dict, player):
    """    Three bet preflop/3rd."""
    stat = 0.0
    try:
        stat = float(stat_dict[player]['tb_0'])/float(stat_dict[player]['tb_opp_0'])
        return (stat,
                '%3.1f'         % (100.0*stat),
                '3B=%3.1f%%'    % (100.0*stat),
                '3B_pf=%3.1f%%' % (100.0*stat),
                '(%d/%d)'       % (stat_dict[player]['tb_0'], stat_dict[player]['tb_opp_0']),
                _('% 3/4 Bet preflop/3rd'))
    except:
        return (stat,
                'NA',
                '3B=NA',
                '3B_pf=NA',
                '(0/0)',
                _('% 3/4 Bet preflop/3rd'))

def WMsF(stat_dict, player):
    """    Won $ when saw flop/4th."""
    stat = 0.0
    try:
        stat = float(stat_dict[player]['w_w_s_1'])/float(stat_dict[player]['saw_1'])
        return (stat,
                '%3.1f'         % (100.0*stat),
                'wf=%3.1f%%'    % (100.0*stat),
                'w_w_f=%3.1f%%' % (100.0*stat),
                '(%d/%d)'       % (stat_dict[player]['w_w_s_1'], stat_dict[player]['saw_f']),
                _('% won$/saw flop/4th'))
    except:
        return (stat,
                'NA',
                'wf=NA',
                'w_w_f=NA',
                '(0/0)',
                _('% won$/saw flop/4th'))

def a_freq1(stat_dict, player):
    """    Flop/4th aggression frequency."""
    stat = 0.0
    try:
        stat = float(stat_dict[player]['aggr_1'])/float(stat_dict[player]['saw_f'])
        return (stat,
                '%3.1f'             % (100.0*stat),
                'a1=%3.1f%%'        % (100.0*stat),
                'a_fq_1=%3.1f%%'    % (100.0*stat),
                '(%d/%d)'      % (stat_dict[player]['aggr_1'], stat_dict[player]['saw_f']),
                _('Aggression Freq flop/4th'))
    except:
        return (stat,
                'NA',
                'a1=NA',
                'a_fq_1=NA',
                '(0/0)',
                _('Aggression Freq flop/4th'))
    
def a_freq2(stat_dict, player):
    """    Turn/5th aggression frequency."""
    stat = 0.0
    try:
        stat = float(stat_dict[player]['aggr_2'])/float(stat_dict[player]['saw_2'])
        return (stat,
                '%3.1f'             % (100.0*stat),
                'a2=%3.1f%%'        % (100.0*stat),
                'a_fq_2=%3.1f%%'    % (100.0*stat),
                '(%d/%d)'           % (stat_dict[player]['aggr_2'], stat_dict[player]['saw_2']),
                _('Aggression Freq turn/5th'))
    except:
        return (stat,
                'NA',
                'a2=NA',
                'a_fq_2=NA',
                '(0/0)',
                _('Aggression Freq turn/5th'))
    
def a_freq3(stat_dict, player):
    """    River/6th aggression frequency."""
    stat = 0.0
    try:
        stat = float(stat_dict[player]['aggr_3'])/float(stat_dict[player]['saw_3'])
        return (stat,
                '%3.1f'             % (100.0*stat),
                'a3=%3.1f%%'        % (100.0*stat),
                'a_fq_3=%3.1f%%'    % (100.0*stat),
                '(%d/%d)'      % (stat_dict[player]['aggr_3'], stat_dict[player]['saw_3']),
                _('Aggression Freq river/6th'))
    except:
        return (stat,
                'NA',
                'a3=NA',
                'a_fq_3=NA',
                '(0/0)',
                _('Aggression Freq river/6th'))
    
def a_freq4(stat_dict, player):
    """    7th street aggression frequency."""
    stat = 0.0
    try:
        stat = float(stat_dict[player]['aggr_4'])/float(stat_dict[player]['saw_4'])
        return (stat,
                '%3.1f'             % (100.0*stat),
                'a4=%3.1f%%'        % (100.0*stat),
                'a_fq_4=%3.1f%%'    % (100.0*stat),
                '(%d/%d)'           % (stat_dict[player]['aggr_4'], stat_dict[player]['saw_4']),
                _('Aggression Freq 7th'))
    except:
        return (stat,
                'NA',
                'a4=NA',
                'a_fq_4=NA',
                '(0/0)',
                _('Aggression Freq 7th'))

def a_freq_123(stat_dict, player):
    """    Post-Flop aggression frequency."""
    stat = 0.0
    try:
        stat = float(  stat_dict[player]['aggr_1'] + stat_dict[player]['aggr_2'] + stat_dict[player]['aggr_3']
                    ) / float(  stat_dict[player]['saw_1'] + stat_dict[player]['saw_2'] + stat_dict[player]['saw_3']);
        return (stat,
                '%3.1f'                 % (100.0*stat),
                'afq=%3.1f%%'           % (100.0*stat),
                'postf_aggfq=%3.1f%%'   % (100.0*stat),
                '(%d/%d)'           % (  stat_dict[player]['aggr_1']
                                       + stat_dict[player]['aggr_2']
                                       + stat_dict[player]['aggr_3']
                                      ,  stat_dict[player]['saw_1']
                                       + stat_dict[player]['saw_2']
                                       + stat_dict[player]['saw_3']
                                      ),
                _('Post-Flop Aggression Freq'))
    except:
        return (stat,
                'NA',
                'a3=NA',
                'a_fq_3=NA',
                '(0/0)',
                _('Post-Flop Aggression Freq'))

def agg_freq(stat_dict, player):
    """    Post-Flop aggression frequency."""
    """  Aggression frequency % = (times bet or raised post-flop) * 100 / (times bet, raised, called, or folded post-flop) """
    stat = 0.0
    try:
        """ Agression on the flop and all streets """
        bet_raise = stat_dict[player]['aggr_1'] + stat_dict[player]['aggr_2'] + stat_dict[player]['aggr_3'] + stat_dict[player]['aggr_4']
        """ number post flop streets seen, this must be number of post-flop calls !! """
        post_call  = stat_dict[player]['call_1'] + stat_dict[player]['call_2'] + stat_dict[player]['call_3'] + stat_dict[player]['call_4']
        """ Number of post flop folds this info is not yet in the database """
        post_fold = stat_dict[player]['f_freq_1'] + stat_dict[player]['f_freq_2'] + stat_dict[player]['f_freq_3'] + stat_dict[player]['f_freq_4']

        stat = float (bet_raise) / float(post_call + post_fold + bet_raise)

        return (stat,
                '%3.1f'             % (100.0*stat),
                'afr=%3.1f%%'       % (100.0*stat),
                'agg_fr=%3.1f%%'    % (100.0*stat),
                '(%d/%d)'           % (bet_raise, (post_call + post_fold + bet_raise)),
                _('Aggression Freq'))
    except:
        return (stat,
                'NA',
                'af=NA',
                'agg_f=NA',
                '(0/0)',
                _('Aggression Freq'))

def agg_fact(stat_dict, player):
    """    Post-Flop aggression frequency."""
    """  Aggression factor = (times bet or raised post-flop) / (times called post-flop) """
    stat = 0.0
    try:
        bet_raise =   stat_dict[player]['aggr_1'] + stat_dict[player]['aggr_2'] + stat_dict[player]['aggr_3'] + stat_dict[player]['aggr_4']
        post_call  =  stat_dict[player]['call_1'] + stat_dict[player]['call_2'] + stat_dict[player]['call_3'] + stat_dict[player]['call_4']
       
        if post_call > 0:
            stat = float (bet_raise) / float(post_call)
        else:
            stat = float (bet_raise)
        return (stat,
                '%2.2f'        % (stat) ,
                'afa=%2.2f'    % (stat) ,
                'agg_fa=%2.2f' % (stat) ,
                '(%d/%d)'      % (bet_raise, post_call),
                _('Aggression Factor'))
    except:
        return (stat,
                'NA',
                'afa=NA',
                'agg_fa=NA',
                '(0/0)',
                _('Aggression Factor'))

def cbet(stat_dict, player):

    """    Total continuation bet."""
    """    Continuation bet % = (times made a continuation bet on any street) * 100 / (number of opportunities to make a continuation bet on any street) """

    stat = 0.0
    try:
        cbets = stat_dict[player]['cb_1']+stat_dict[player]['cb_2']+stat_dict[player]['cb_3']+stat_dict[player]['cb_4']
        oppt = stat_dict[player]['cb_opp_1']+stat_dict[player]['cb_opp_2']+stat_dict[player]['cb_opp_3']+stat_dict[player]['cb_opp_4']
        stat = float(cbets)/float(oppt)
        return (stat,
                '%3.1f'         % (100.0*stat),
                'cbet=%3.1f%%'  % (100.0*stat),
                'cbet=%3.1f%%'  % (100.0*stat),
                '(%d/%d)'       % (cbets, oppt),
                _('% continuation bet '))
    except:
        return (stat,
                'NA',
                'cbet=NA',
                'cbet=NA',
                '(0/0)',
                _('% continuation bet '))
    
def cb1(stat_dict, player):
    """    Flop continuation bet."""
    stat = 0.0
    try:
        stat = float(stat_dict[player]['cb_1'])/float(stat_dict[player]['cb_opp_1'])
        return (stat,
                '%3.1f'         % (100.0*stat),
                'cb1=%3.1f%%'   % (100.0*stat),
                'cb_1=%3.1f%%'  % (100.0*stat),
                '(%d/%d)'       % (stat_dict[player]['cb_1'], stat_dict[player]['cb_opp_1']),
                _('% continuation bet flop/4th'))
    except:
        return (stat,
                'NA',
                'cb1=NA',
                'cb_1=NA',
                '(0/0)',
                _('% continuation bet flop/4th'))
    
def cb2(stat_dict, player):
    """    Turn continuation bet."""
    stat = 0.0
    try:
        stat = float(stat_dict[player]['cb_2'])/float(stat_dict[player]['cb_opp_2'])
        return (stat,
                '%3.1f'         % (100.0*stat),
                'cb2=%3.1f%%'   % (100.0*stat),
                'cb_2=%3.1f%%'  % (100.0*stat),
                '(%d/%d)'       % (stat_dict[player]['cb_2'], stat_dict[player]['cb_opp_2']),
                _('% continuation bet turn/5th'))
    except:
        return (stat,
                'NA',
                'cb2=NA',
                'cb_2=NA',
                '(0/0)',
                _('% continuation bet turn/5th'))
    
def cb3(stat_dict, player):
    """    River continuation bet."""
    stat = 0.0
    try:
        stat = float(stat_dict[player]['cb_3'])/float(stat_dict[player]['cb_opp_3'])
        return (stat,
                '%3.1f'         % (100.0*stat),
                'cb3=%3.1f%%'   % (100.0*stat),
                'cb_3=%3.1f%%'  % (100.0*stat),
                '(%d/%d)'       % (stat_dict[player]['cb_3'], stat_dict[player]['cb_opp_3']),
                _('% continuation bet river/6th'))
    except:
        return (stat,
                'NA',
                'cb3=NA',
                'cb_3=NA',
                '(0/0)',
                _('% continuation bet river/6th'))
    
def cb4(stat_dict, player):
    """    7th street continuation bet."""
    stat = 0.0
    try:
        stat = float(stat_dict[player]['cb_4'])/float(stat_dict[player]['cb_opp_4'])
        return (stat,
                '%3.1f'         % (100.0*stat),
                'cb4=%3.1f%%'   % (100.0*stat),
                'cb_4=%3.1f%%'  % (100.0*stat),
                '(%d/%d)'      % (stat_dict[player]['cb_4'], stat_dict[player]['cb_opp_4']),
                _('% continuation bet 7th'))
    except:
        return (stat,
                'NA',
                'cb4=NA',
                'cb_4=NA',
                '(0/0)',
                _('% continuation bet 7th'))
    
def ffreq1(stat_dict, player):
    """    Flop/4th fold frequency."""
    stat = 0.0
    try:
        stat = float(stat_dict[player]['f_freq_1'])/float(stat_dict[player]['was_raised_1'])
        return (stat,
                '%3.1f'         % (100.0*stat),
                'ff1=%3.1f%%'   % (100.0*stat),
                'ff_1=%3.1f%%'  % (100.0*stat),
                '(%d/%d)'       % (stat_dict[player]['f_freq_1'], stat_dict[player]['was_raised_1']),
                _('% fold frequency flop/4th'))
    except:
        return (stat,
                'NA',
                'ff1=NA',
                'ff_1=NA',
                '(0/0)',
                _('% fold frequency flop/4th'))
    
def ffreq2(stat_dict, player):
    """    Turn/5th fold frequency."""
    stat = 0.0
    try:
        stat = float(stat_dict[player]['f_freq_2'])/float(stat_dict[player]['was_raised_2'])
        return (stat,
                '%3.1f'         % (100.0*stat),
                'ff2=%3.1f%%'   % (100.0*stat),
                'ff_2=%3.1f%%'  % (100.0*stat),
                '(%d/%d)'       % (stat_dict[player]['f_freq_2'], stat_dict[player]['was_raised_2']),
                _('% fold frequency turn/5th'))
    except:
        return (stat,
                'NA',
                'ff2=NA',
                'ff_2=NA',
                '(0/0)',
                _('% fold frequency turn/5th'))
    
def ffreq3(stat_dict, player):
    """    River/6th fold frequency."""
    stat = 0.0
    try:
        stat = float(stat_dict[player]['f_freq_3'])/float(stat_dict[player]['was_raised_3'])
        return (stat,
                '%3.1f'         % (100.0*stat),
                'ff3=%3.1f%%'   % (100.0*stat),
                'ff_3=%3.1f%%'  % (100.0*stat),
                '(%d/%d)'       % (stat_dict[player]['f_freq_3'], stat_dict[player]['was_raised_3']),
                _('% fold frequency river/6th'))
    except:
        return (stat,
                'NA',
                'ff3=NA',
                'ff_3=NA',
                '(0/0)',
                _('% fold frequency river/6th'))
    
def ffreq4(stat_dict, player):
    """    7th fold frequency."""
    stat = 0.0
    try:
        stat = float(stat_dict[player]['f_freq_4'])/float(stat_dict[player]['was_raised_4'])
        return (stat,
                '%3.1f'         % (100.0*stat),
                'ff4=%3.1f%%'   % (100.0*stat),
                'ff_4=%3.1f%%'  % (100.0*stat),
                '(%d/%d)'       % (stat_dict[player]['f_freq_4'], stat_dict[player]['was_raised_4']),
                _('% fold frequency 7th'))
    except:
        return (stat,
                'NA',
                'ff4=NA',
                'ff_4=NA',
                '(0/0)',
                _('% fold frequency 7th'))
    
if __name__== "__main__":
    statlist = dir()
    misslist = [ "Configuration", "Database", "Charset", "codecs", "encoder"
               , "do_stat", "do_tip", "GInitiallyUnowned", "gtk", "pygtk"
               , "re", "re_Places"
               ]
    statlist = [ x for x in statlist if x not in dir(sys) ]
    statlist = [ x for x in statlist if x not in dir(codecs) ]
    statlist = [ x for x in statlist if x not in misslist ]
    #print "statlist is", statlist

    c = Configuration.Config()
    #TODO: restore the below code. somehow it creates a version 119 DB but commenting this out makes it print a stat list
    db_connection = Database.Database(c)
    h = db_connection.get_last_hand()
    stat_dict = db_connection.get_stats_from_hand(h, "ring")
    
    for player in stat_dict.keys():
        print (_("Example stats, player = %s  hand = %s:") % (player, h))
        for attr in statlist:
            print "  ", do_stat(stat_dict, player=player, stat=attr)
        break
        #print "player = ", player, do_stat(stat_dict, player = player, stat = 'vpip') 
        #print "player = ", player, do_stat(stat_dict, player = player, stat = 'pfr') 
        #print "player = ", player, do_stat(stat_dict, player = player, stat = 'wtsd') 
        #print "player = ", player, do_stat(stat_dict, player = player, stat = 'profit100') 
        #print "player = ", player, do_stat(stat_dict, player = player, stat = 'saw_f') 
        #print "player = ", player, do_stat(stat_dict, player = player, stat = 'n') 
        #print "player = ", player, do_stat(stat_dict, player = player, stat = 'fold_f') 
        #print "player = ", player, do_stat(stat_dict, player = player, stat = 'wmsd') 
        #print "player = ", player, do_stat(stat_dict, player = player, stat = 'steal') 
        #print "player = ", player, do_stat(stat_dict, player = player, stat = 'f_SB_steal') 
        #print "player = ", player, do_stat(stat_dict, player = player, stat = 'f_BB_steal') 
        #print "player = ", player, do_stat(stat_dict, player = player, stat = 'f_steal')
        #print "player = ", player, do_stat(stat_dict, player = player, stat = 'three_B')
        #print "player = ", player, do_stat(stat_dict, player = player, stat = 'WMsF') 
        #print "player = ", player, do_stat(stat_dict, player = player, stat = 'a_freq1') 
        #print "player = ", player, do_stat(stat_dict, player = player, stat = 'a_freq2') 
        #print "player = ", player, do_stat(stat_dict, player = player, stat = 'a_freq3') 
        #print "player = ", player, do_stat(stat_dict, player = player, stat = 'a_freq4') 
        #print "player = ", player, do_stat(stat_dict, player = player, stat = 'a_freq_123') 
        #print "player = ", player, do_stat(stat_dict, player = player, stat = 'cb1') 
        #print "player = ", player, do_stat(stat_dict, player = player, stat = 'cb2') 
        #print "player = ", player, do_stat(stat_dict, player = player, stat = 'cb3') 
        #print "player = ", player, do_stat(stat_dict, player = player, stat = 'cb4') 
        #print "player = ", player, do_stat(stat_dict, player = player, stat = 'ffreq1') 
        #print "player = ", player, do_stat(stat_dict, player = player, stat = 'ffreq2') 
        #print "player = ", player, do_stat(stat_dict, player = player, stat = 'ffreq3') 
        #print "player = ", player, do_stat(stat_dict, player = player, stat = 'ffreq4')
        #print "\n" 

    print _("\n\nLegal stats:")
    print _("(add _0 to name to display with 0 decimal places, _1 to display with 1, etc)\n")
    for attr in statlist:
        print "%-14s %s" % (attr, eval("%s.__doc__" % (attr)))
#        print "            <pu_stat pu_stat_name = \"%s\"> </pu_stat>" % (attr)
    print

    #db_connection.close_connection

