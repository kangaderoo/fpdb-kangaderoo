#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Returns a dict of SQL statements used in fpdb.
"""
#    Copyright 2008-2011, Ray E. Barker
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

#    NOTES:  The sql statements use the placeholder %s for bind variables
#            which is then replaced by ? for sqlite. Comments can be included 
#            within sql statements using C style /* ... */ comments, BUT
#            THE COMMENTS MUST NOT INCLUDE %s OR ?.

########################################################################

#    Standard Library modules
import re

#    pyGTK modules

#    FreePokerTools modules

class Sql:
   
    def __init__(self, game = 'holdem', db_server = 'mysql'):
        self.query = {}
###############################################################################3
#    Support for the Free Poker DataBase = fpdb   http://fpdb.sourceforge.net/
#

        ################################
        # List tables
        ################################
        if db_server == 'mysql':
            self.query['list_tables'] = """SHOW TABLES"""
        elif db_server == 'postgresql':
            self.query['list_tables'] = """SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"""
        elif db_server == 'sqlite':
            self.query['list_tables'] = """SELECT name FROM sqlite_master
            WHERE type='table'
            ORDER BY name;"""

        ################################
        # List indexes
        ################################
        if db_server == 'mysql':
            self.query['list_indexes'] = """SHOW INDEXES"""
        elif db_server == 'postgresql':
            self.query['list_indexes'] = """SELECT tablename, indexname FROM PG_INDEXES""" 
        elif db_server == 'sqlite':
            self.query['list_indexes'] = """SELECT name FROM sqlite_master
                                            WHERE type='index'
                                            ORDER BY name;"""

        ##################################################################
        # Drop Tables - MySQL, PostgreSQL and SQLite all share same syntax
        ##################################################################

        self.query['drop_table'] = """DROP TABLE IF EXISTS """   


        ##################################################################
        # Set transaction isolation level
        ##################################################################

        if db_server == 'mysql' or db_server == 'postgresql':
            self.query['set tx level'] = """SET SESSION TRANSACTION
            ISOLATION LEVEL READ COMMITTED"""
        elif db_server == 'sqlite':
            self.query['set tx level'] = """ """


        ################################
        # Select basic info
        ################################

        self.query['getSiteId'] = """SELECT id from Sites where name = %s"""

        self.query['getGames'] = """SELECT DISTINCT category from Gametypes"""
        
        self.query['getLimits'] = """SELECT DISTINCT bigBlind from Gametypes ORDER by bigBlind DESC"""

        self.query['getTourneyTypesIds'] = "SELECT id FROM TourneyTypes"

        ################################
        # Create Settings
        ################################
        if db_server == 'mysql':
            self.query['createSettingsTable'] = """CREATE TABLE Settings (
                                        version SMALLINT NOT NULL)
                                ENGINE=INNODB"""
        elif db_server == 'postgresql':
            self.query['createSettingsTable'] =  """CREATE TABLE Settings (version SMALLINT NOT NULL)"""

        elif db_server == 'sqlite':
            self.query['createSettingsTable'] = """CREATE TABLE Settings
            (version INTEGER NOT NULL) """
            
        ################################
        # Create InsertLock
        ################################
        if db_server == 'mysql':
            self.query['createLockTable'] = """CREATE TABLE InsertLock (
                        id BIGINT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                        locked BOOLEAN NOT NULL DEFAULT FALSE)
                        ENGINE=INNODB"""

        ################################
        # Create RawHands (this table is all but identical with RawTourneys)
        ################################
        if db_server == 'mysql':
            self.query['createRawHands'] = """CREATE TABLE RawHands (
                        id BIGINT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                        handId BIGINT NOT NULL,
                        rawHand TEXT NOT NULL,
                        complain BOOLEAN NOT NULL DEFAULT FALSE)
                        ENGINE=INNODB"""
        elif db_server == 'postgresql':
            self.query['createRawHands'] =  """CREATE TABLE RawHands (
                        id BIGSERIAL, PRIMARY KEY (id),
                        handId BIGINT NOT NULL,
                        rawHand TEXT NOT NULL,
                        complain BOOLEAN NOT NULL DEFAULT FALSE)"""
        elif db_server == 'sqlite':
            self.query['createRawHands'] = """CREATE TABLE RawHands (
                        id INTEGER PRIMARY KEY,
                        handId BIGINT NOT NULL,
                        rawHand TEXT NOT NULL,
                        complain BOOLEAN NOT NULL DEFAULT FALSE)"""
        
        ################################
        # Create RawTourneys (this table is all but identical with RawHands)
        ################################
        if db_server == 'mysql':
            self.query['createRawTourneys'] = """CREATE TABLE RawTourneys (
                        id BIGINT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                        tourneyId BIGINT NOT NULL,
                        rawTourney TEXT NOT NULL,
                        complain BOOLEAN NOT NULL DEFAULT FALSE)
                        ENGINE=INNODB"""
        elif db_server == 'postgresql':
            self.query['createRawTourneys'] =  """CREATE TABLE RawTourneys (
                        id BIGSERIAL, PRIMARY KEY (id),
                        tourneyId BIGINT NOT NULL,
                        rawTourney TEXT NOT NULL,
                        complain BOOLEAN NOT NULL DEFAULT FALSE)"""
        elif db_server == 'sqlite':
            self.query['createRawTourneys'] = """CREATE TABLE RawTourneys (
                        id INTEGER PRIMARY KEY,
                        tourneyId BIGINT NOT NULL,
                        rawTourney TEXT NOT NULL,
                        complain BOOLEAN NOT NULL DEFAULT FALSE)"""
                        
        ################################
        # Create Actions
        ################################

        if db_server == 'mysql':
            self.query['createActionsTable'] = """CREATE TABLE Actions (
                        id SMALLINT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                        name varchar(32) NOT NULL,
                        code char(4) NOT NULL)
                        ENGINE=INNODB"""
        elif db_server == 'postgresql':
            self.query['createActionsTable'] = """CREATE TABLE Actions (
                        id SERIAL, PRIMARY KEY (id),
                        name varchar(32),
                        code char(4))"""
        elif db_server == 'sqlite':
            self.query['createActionsTable'] = """CREATE TABLE Actions (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        code TEXT NOT NULL)"""        
                        
        ################################
        # Create Sites
        ################################

        if db_server == 'mysql':
            self.query['createSitesTable'] = """CREATE TABLE Sites (
                        id SMALLINT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                        name varchar(32) NOT NULL,
                        code char(2) NOT NULL)
                        ENGINE=INNODB"""
        elif db_server == 'postgresql':
            self.query['createSitesTable'] = """CREATE TABLE Sites (
                        id SERIAL, PRIMARY KEY (id),
                        name varchar(32),
                        code char(2))"""
        elif db_server == 'sqlite':
            self.query['createSitesTable'] = """CREATE TABLE Sites (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        code TEXT NOT NULL)"""

        ################################
        # Create Backings
        ################################
        
        if db_server == 'mysql':
            self.query['createBackingsTable'] = """CREATE TABLE Backings (
                        id SMALLINT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                        tourneysPlayersId BIGINT UNSIGNED NOT NULL, FOREIGN KEY (tourneysPlayersId) REFERENCES TourneysPlayers(id),
                        playerId INT UNSIGNED NOT NULL, FOREIGN KEY (playerId) REFERENCES Players(id),
                        buyInPercentage FLOAT UNSIGNED NOT NULL,
                        payOffPercentage FLOAT UNSIGNED NOT NULL) ENGINE=INNODB"""
        elif db_server == 'postgresql':
            self.query['createBackingsTable'] = """CREATE TABLE Backings (
                        id BIGSERIAL, PRIMARY KEY (id),
                        tourneysPlayersId INT NOT NULL, FOREIGN KEY (tourneysPlayersId) REFERENCES TourneysPlayers(id),
                        playerId INT NOT NULL, FOREIGN KEY (playerId) REFERENCES Players(id),
                        buyInPercentage FLOAT NOT NULL,
                        payOffPercentage FLOAT NOT NULL)"""
        elif db_server == 'sqlite':
            self.query['createBackingsTable'] = """CREATE TABLE Backings (
                        id INTEGER PRIMARY KEY,
                        tourneysPlayersId INT NOT NULL,
                        playerId INT NOT NULL,
                        buyInPercentage REAL UNSIGNED NOT NULL,
                        payOffPercentage REAL UNSIGNED NOT NULL)"""
        
        ################################
        # Create Gametypes
        ################################

        if db_server == 'mysql':
            self.query['createGametypesTable'] = """CREATE TABLE Gametypes (
                        id SMALLINT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                        siteId SMALLINT UNSIGNED NOT NULL, FOREIGN KEY (siteId) REFERENCES Sites(id),
                        currency varchar(4) NOT NULL,
                        type char(4) NOT NULL,
                        base char(4) NOT NULL,
                        category varchar(9) NOT NULL,
                        limitType char(2) NOT NULL,
                        hiLo char(1) NOT NULL,
                        smallBlind int,
                        bigBlind int,
                        smallBet int NOT NULL,
                        bigBet int NOT NULL)
                        ENGINE=INNODB"""
        elif db_server == 'postgresql':
            self.query['createGametypesTable'] = """CREATE TABLE Gametypes (
                        id SERIAL, PRIMARY KEY (id),
                        siteId INTEGER, FOREIGN KEY (siteId) REFERENCES Sites(id),
                        currency varchar(4),
                        type char(4),
                        base char(4),
                        category varchar(9),
                        limitType char(2),
                        hiLo char(1),
                        smallBlind int,
                        bigBlind int,
                        smallBet int,
                        bigBet int)"""
        elif db_server == 'sqlite':
            self.query['createGametypesTable'] = """CREATE TABLE Gametypes (
                        id INTEGER PRIMARY KEY,
                        siteId INTEGER,
                        currency TEXT,
                        type TEXT,
                        base TEXT,
                        category TEXT,
                        limitType TEXT,
                        hiLo TEXT,
                        smallBlind INTEGER,
                        bigBlind INTEGER,
                        smallBet INTEGER,
                        bigBet INTEGER,
                        FOREIGN KEY(siteId) REFERENCES Sites(id) ON DELETE CASCADE)"""


        ################################
        # Create Players
        ################################

        if db_server == 'mysql':
            self.query['createPlayersTable'] = """CREATE TABLE Players (
                        id INT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                        name VARCHAR(32) NOT NULL,
                        siteId SMALLINT UNSIGNED NOT NULL, FOREIGN KEY (siteId) REFERENCES Sites(id),
                        comment text,
                        commentTs DATETIME)
                        ENGINE=INNODB"""
        elif db_server == 'postgresql':
            self.query['createPlayersTable'] = """CREATE TABLE Players (
                        id SERIAL, PRIMARY KEY (id),
                        name VARCHAR(32),
                        siteId INTEGER, FOREIGN KEY (siteId) REFERENCES Sites(id),
                        comment text,
                        commentTs timestamp without time zone)"""
        elif db_server == 'sqlite':
            self.query['createPlayersTable'] = """CREATE TABLE Players (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        siteId INTEGER,
                        comment TEXT,
                        commentTs REAL,
                        FOREIGN KEY(siteId) REFERENCES Sites(id) ON DELETE CASCADE)"""


        ################################
        # Create Autorates
        ################################

        if db_server == 'mysql':
            self.query['createAutoratesTable'] = """CREATE TABLE Autorates (
                            id BIGINT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                            playerId INT UNSIGNED NOT NULL, FOREIGN KEY (playerId) REFERENCES Players(id),
                            gametypeId SMALLINT UNSIGNED NOT NULL, FOREIGN KEY (gametypeId) REFERENCES Gametypes(id),
                            description varchar(50) NOT NULL,
                            shortDesc char(8) NOT NULL,
                            ratingTime DATETIME NOT NULL,
                            handCount int NOT NULL)
                        ENGINE=INNODB"""
        elif db_server == 'postgresql':
            self.query['createAutoratesTable'] = """CREATE TABLE Autorates (
                            id BIGSERIAL, PRIMARY KEY (id),
                            playerId INT, FOREIGN KEY (playerId) REFERENCES Players(id),
                            gametypeId INT, FOREIGN KEY (gametypeId) REFERENCES Gametypes(id),
                            description varchar(50),
                            shortDesc char(8),
                            ratingTime timestamp without time zone,
                            handCount int)"""
        elif db_server == 'sqlite':
            self.query['createAutoratesTable'] = """CREATE TABLE Autorates (
                            id INTEGER PRIMARY KEY,
                            playerId INT,
                            gametypeId INT,
                            description TEXT,
                            shortDesc TEXT,
                            ratingTime REAL,
                            handCount int)"""


        ################################
        # Create Hands
        ################################

        if db_server == 'mysql':
            self.query['createHandsTable'] = """CREATE TABLE Hands (
                            id BIGINT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                            tableName VARCHAR(22) NOT NULL,
                            siteHandNo BIGINT NOT NULL,
                            tourneyId INT UNSIGNED, 
                            gametypeId SMALLINT UNSIGNED NOT NULL, FOREIGN KEY (gametypeId) REFERENCES Gametypes(id),
                            sessionId INT UNSIGNED,
                            gameSessionId INT UNSIGNED, 
                            startTime DATETIME NOT NULL,
                            importTime DATETIME NOT NULL,
                            seats TINYINT NOT NULL,
                            maxSeats TINYINT NOT NULL,
                            rush BOOLEAN,
                            boardcard1 smallint,  /* 0=none, 1-13=2-Ah 14-26=2-Ad 27-39=2-Ac 40-52=2-As */
                            boardcard2 smallint,
                            boardcard3 smallint,
                            boardcard4 smallint,
                            boardcard5 smallint,
                            texture smallint,
                            playersVpi SMALLINT NOT NULL,         /* num of players vpi */
                            playersAtStreet1 SMALLINT NOT NULL,   /* num of players seeing flop/street4 */
                            playersAtStreet2 SMALLINT NOT NULL,
                            playersAtStreet3 SMALLINT NOT NULL,
                            playersAtStreet4 SMALLINT NOT NULL,
                            playersAtShowdown SMALLINT NOT NULL,
                            street0Raises TINYINT NOT NULL, /* num small bets paid to see flop/street4, including blind */
                            street1Raises TINYINT NOT NULL, /* num small bets paid to see turn/street5 */
                            street2Raises TINYINT NOT NULL, /* num big bets paid to see river/street6 */
                            street3Raises TINYINT NOT NULL, /* num big bets paid to see sd/street7 */
                            street4Raises TINYINT NOT NULL, /* num big bets paid to see showdown */
                            street1Pot INT,                  /* pot size at flop/street4 */
                            street2Pot INT,                  /* pot size at turn/street5 */
                            street3Pot INT,                  /* pot size at river/street6 */
                            street4Pot INT,                  /* pot size at sd/street7 */
                            showdownPot INT,                 /* pot size at sd/street7 */
                            comment TEXT,
                            commentTs DATETIME)
                        ENGINE=INNODB"""
        elif db_server == 'postgresql':
            self.query['createHandsTable'] = """CREATE TABLE Hands (
                            id BIGSERIAL, PRIMARY KEY (id),
                            tableName VARCHAR(22) NOT NULL,
                            siteHandNo BIGINT NOT NULL,
                            tourneyId INT,
                            gametypeId INT NOT NULL, FOREIGN KEY (gametypeId) REFERENCES Gametypes(id),
                            sessionId INT,
                            gameSessionId INT,
                            startTime timestamp without time zone NOT NULL,
                            importTime timestamp without time zone NOT NULL,
                            seats SMALLINT NOT NULL,
                            maxSeats SMALLINT NOT NULL,
                            rush BOOLEAN,
                            boardcard1 smallint,  /* 0=none, 1-13=2-Ah 14-26=2-Ad 27-39=2-Ac 40-52=2-As */
                            boardcard2 smallint,
                            boardcard3 smallint,
                            boardcard4 smallint,
                            boardcard5 smallint,
                            texture smallint,
                            playersVpi SMALLINT NOT NULL,         /* num of players vpi */
                            playersAtStreet1 SMALLINT NOT NULL,   /* num of players seeing flop/street4 */
                            playersAtStreet2 SMALLINT NOT NULL,
                            playersAtStreet3 SMALLINT NOT NULL,
                            playersAtStreet4 SMALLINT NOT NULL,
                            playersAtShowdown SMALLINT NOT NULL,
                            street0Raises SMALLINT NOT NULL, /* num small bets paid to see flop/street4, including blind */
                            street1Raises SMALLINT NOT NULL, /* num small bets paid to see turn/street5 */
                            street2Raises SMALLINT NOT NULL, /* num big bets paid to see river/street6 */
                            street3Raises SMALLINT NOT NULL, /* num big bets paid to see sd/street7 */
                            street4Raises SMALLINT NOT NULL, /* num big bets paid to see showdown */
                            street1Pot INT,                 /* pot size at flop/street4 */
                            street2Pot INT,                 /* pot size at turn/street5 */
                            street3Pot INT,                 /* pot size at river/street6 */
                            street4Pot INT,                 /* pot size at sd/street7 */
                            showdownPot INT,                /* pot size at sd/street7 */
                            comment TEXT,
                            commentTs timestamp without time zone)"""
        elif db_server == 'sqlite':
            self.query['createHandsTable'] = """CREATE TABLE Hands (
                            id INTEGER PRIMARY KEY,
                            tableName TEXT(22) NOT NULL,
                            siteHandNo INT NOT NULL,
                            tourneyId INT,
                            gametypeId INT NOT NULL,
                            sessionId INT,
                            gameSessionId INT,
                            startTime REAL NOT NULL,
                            importTime REAL NOT NULL,
                            seats INT NOT NULL,
                            maxSeats INT NOT NULL,
                            rush BOOLEAN,
                            boardcard1 INT,  /* 0=none, 1-13=2-Ah 14-26=2-Ad 27-39=2-Ac 40-52=2-As */
                            boardcard2 INT,
                            boardcard3 INT,
                            boardcard4 INT,
                            boardcard5 INT,
                            texture INT,
                            playersVpi INT NOT NULL,         /* num of players vpi */
                            playersAtStreet1 INT NOT NULL,   /* num of players seeing flop/street4 */
                            playersAtStreet2 INT NOT NULL,
                            playersAtStreet3 INT NOT NULL,
                            playersAtStreet4 INT NOT NULL,
                            playersAtShowdown INT NOT NULL,
                            street0Raises INT NOT NULL, /* num small bets paid to see flop/street4, including blind */
                            street1Raises INT NOT NULL, /* num small bets paid to see turn/street5 */
                            street2Raises INT NOT NULL, /* num big bets paid to see river/street6 */
                            street3Raises INT NOT NULL, /* num big bets paid to see sd/street7 */
                            street4Raises INT NOT NULL, /* num big bets paid to see showdown */
                            street1Pot INT,                 /* pot size at flop/street4 */
                            street2Pot INT,                 /* pot size at turn/street5 */
                            street3Pot INT,                 /* pot size at river/street6 */
                            street4Pot INT,                 /* pot size at sd/street7 */
                            showdownPot INT,                /* pot size at sd/street7 */
                            comment TEXT,
                            commentTs REAL)"""


        ################################
        # Create TourneyTypes
        ################################

        if db_server == 'mysql':
            self.query['createTourneyTypesTable'] = """CREATE TABLE TourneyTypes (
                        id SMALLINT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                        siteId SMALLINT UNSIGNED NOT NULL, FOREIGN KEY (siteId) REFERENCES Sites(id),
                        currency varchar(4),
                        buyIn INT,
                        fee INT,
                        category varchar(9) NOT NULL,
                        limitType char(2) NOT NULL,
                        buyInChips INT,
                        maxSeats INT,
                        rebuy BOOLEAN,
                        rebuyCost INT,
                        rebuyFee INT,
                        rebuyChips INT,
                        addOn BOOLEAN,
                        addOnCost INT,
                        addOnFee INT,
                        addOnChips INT,
                        knockout BOOLEAN,
                        koBounty INT,
                        speed varchar(10),
                        shootout BOOLEAN,
                        matrix BOOLEAN,
                        sng BOOLEAN,
                        satellite BOOLEAN,
                        doubleOrNothing BOOLEAN,
                        guarantee INT,
                        added INT,
                        addedCurrency VARCHAR(4))
                        ENGINE=INNODB"""
        elif db_server == 'postgresql':
            self.query['createTourneyTypesTable'] = """CREATE TABLE TourneyTypes (
                        id SERIAL, PRIMARY KEY (id),
                        siteId INT NOT NULL, FOREIGN KEY (siteId) REFERENCES Sites(id),
                        currency varchar(4),
                        buyin INT,
                        fee INT,
                        category varchar(9),
                        limitType char(2),
                        buyInChips INT,
                        maxSeats INT,
                        rebuy BOOLEAN,
                        rebuyCost INT,
                        rebuyFee INT,
                        rebuyChips INT,
                        addOn BOOLEAN,
                        addOnCost INT,
                        addOnFee INT,
                        addOnChips INT,
                        knockout BOOLEAN,
                        koBounty INT,
                        speed varchar(10),
                        shootout BOOLEAN,
                        matrix BOOLEAN,
                        sng BOOLEAN,
                        satellite BOOLEAN,
                        doubleOrNothing BOOLEAN,
                        guarantee INT,
                        added INT,
                        addedCurrency VARCHAR(4))"""
        elif db_server == 'sqlite':
            self.query['createTourneyTypesTable'] = """CREATE TABLE TourneyTypes (
                        id INTEGER PRIMARY KEY,
                        siteId INT NOT NULL,
                        currency VARCHAR(4),
                        buyin INT,
                        fee INT,
                        category TEXT,
                        limitType TEXT,
                        buyInChips INT,
                        maxSeats INT,
                        rebuy BOOLEAN,
                        rebuyCost INT,
                        rebuyFee INT,
                        rebuyChips INT,
                        addOn BOOLEAN,
                        addOnCost INT,
                        addOnFee INT,
                        addOnChips INT,
                        knockout BOOLEAN,
                        koBounty INT,
                        speed TEXT,
                        shootout BOOLEAN,
                        matrix BOOLEAN,
                        sng BOOLEAN,
                        satellite BOOLEAN,
                        doubleOrNothing BOOLEAN,
                        guarantee INT,
                        added INT,
                        addedCurrency VARCHAR(4))"""

        ################################
        # Create Tourneys
        ################################

        if db_server == 'mysql':
            self.query['createTourneysTable'] = """CREATE TABLE Tourneys (
                        id INT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                        tourneyTypeId SMALLINT UNSIGNED NOT NULL, FOREIGN KEY (tourneyTypeId) REFERENCES TourneyTypes(id),
                        siteTourneyNo BIGINT NOT NULL,
                        entries INT,
                        prizepool INT,
                        startTime DATETIME NOT NULL,
                        endTime DATETIME,
                        tourneyName varchar(40),
                        matrixIdProcessed TINYINT UNSIGNED DEFAULT 0,    /* Mask use : 1=Positionnal Winnings|2=Match1|4=Match2|...|pow(2,n)=Matchn */
                        totalRebuyCount INT,
                        totalAddOnCount INT,
                        comment TEXT,
                        commentTs DATETIME)
                        ENGINE=INNODB"""
        elif db_server == 'postgresql':
            self.query['createTourneysTable'] = """CREATE TABLE Tourneys (
                        id SERIAL, PRIMARY KEY (id),
                        tourneyTypeId INT, FOREIGN KEY (tourneyTypeId) REFERENCES TourneyTypes(id),
                        siteTourneyNo BIGINT,
                        entries INT,
                        prizepool INT,
                        startTime timestamp without time zone,
                        endTime timestamp without time zone,
                        tourneyName varchar(40),
                        matrixIdProcessed SMALLINT DEFAULT 0,    /* Mask use : 1=Positionnal Winnings|2=Match1|4=Match2|...|pow(2,n)=Matchn */
                        totalRebuyCount INT,
                        totalAddOnCount INT,
                        comment TEXT,
                        commentTs timestamp without time zone)"""
        elif db_server == 'sqlite':
            self.query['createTourneysTable'] = """CREATE TABLE Tourneys (
                        id INTEGER PRIMARY KEY,
                        tourneyTypeId INT,
                        siteTourneyNo INT,
                        entries INT,
                        prizepool INT,
                        startTime REAL,
                        endTime REAL,
                        tourneyName TEXT,
                        matrixIdProcessed INT UNSIGNED DEFAULT 0,    /* Mask use : 1=Positionnal Winnings|2=Match1|4=Match2|...|pow(2,n)=Matchn */
                        totalRebuyCount INT,
                        totalAddOnCount INT,
                        comment TEXT,
                        commentTs REAL)"""
        ################################
        # Create HandsPlayers
        ################################

        if db_server == 'mysql':
            self.query['createHandsPlayersTable'] = """CREATE TABLE HandsPlayers (
                        id BIGINT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                        handId BIGINT UNSIGNED NOT NULL, FOREIGN KEY (handId) REFERENCES Hands(id),
                        playerId INT UNSIGNED NOT NULL, FOREIGN KEY (playerId) REFERENCES Players(id),
                        startCash INT NOT NULL,
                        position CHAR(1),
                        seatNo SMALLINT NOT NULL,
                        sitout BOOLEAN NOT NULL,
                        wentAllInOnStreet SMALLINT,
                    
                        card1 smallint NOT NULL,  /* 0=none, 1-13=2-Ah 14-26=2-Ad 27-39=2-Ac 40-52=2-As */
                        card2 smallint NOT NULL,
                        card3 smallint,
                        card4 smallint,
                        card5 smallint,
                        card6 smallint,
                        card7 smallint,
                        card8 smallint,  /* cards 8-20 for draw hands */
                        card9 smallint,
                        card10 smallint,
                        card11 smallint,
                        card12 smallint,
                        card13 smallint,
                        card14 smallint,
                        card15 smallint,
                        card16 smallint,
                        card17 smallint,
                        card18 smallint,
                        card19 smallint,
                        card20 smallint,
                        startCards smallint,
                    
                        ante INT,
                        winnings int NOT NULL,
                        rake int NOT NULL,
                        totalProfit INT,
                        comment text,
                        commentTs DATETIME,
                        tourneysPlayersId BIGINT UNSIGNED, FOREIGN KEY (tourneysPlayersId) REFERENCES TourneysPlayers(id),

                        wonWhenSeenStreet1 FLOAT,
                        wonWhenSeenStreet2 FLOAT,
                        wonWhenSeenStreet3 FLOAT,
                        wonWhenSeenStreet4 FLOAT,
                        wonAtSD FLOAT,

                        street0VPI BOOLEAN,
                        street0Aggr BOOLEAN,
                        street0_3BChance BOOLEAN,
                        street0_3BDone BOOLEAN,
                        street0_4BChance BOOLEAN,
                        street0_C4BChance BOOLEAN,
                        street0_4BDone BOOLEAN,
                        street0_C4BDone BOOLEAN,
                        street0_FoldTo3BChance BOOLEAN,
                        street0_FoldTo3BDone BOOLEAN,
                        street0_FoldTo4BChance BOOLEAN,
                        street0_FoldTo4BDone BOOLEAN,
                        street0_SqueezeChance BOOLEAN,
                        street0_SqueezeDone BOOLEAN,

                        raiseToStealChance BOOLEAN,
                        raiseToStealDone BOOLEAN,
                        success_Steal BOOLEAN,

                        street1Seen BOOLEAN,
                        street2Seen BOOLEAN,
                        street3Seen BOOLEAN,
                        street4Seen BOOLEAN,
                        sawShowdown BOOLEAN,

                        street1Aggr BOOLEAN,
                        street2Aggr BOOLEAN,
                        street3Aggr BOOLEAN,
                        street4Aggr BOOLEAN,

                        otherRaisedStreet0 BOOLEAN,
                        otherRaisedStreet1 BOOLEAN,
                        otherRaisedStreet2 BOOLEAN,
                        otherRaisedStreet3 BOOLEAN,
                        otherRaisedStreet4 BOOLEAN,
                        foldToOtherRaisedStreet0 BOOLEAN,
                        foldToOtherRaisedStreet1 BOOLEAN,
                        foldToOtherRaisedStreet2 BOOLEAN,
                        foldToOtherRaisedStreet3 BOOLEAN,
                        foldToOtherRaisedStreet4 BOOLEAN,

                        raiseFirstInChance BOOLEAN,
                        raisedFirstIn BOOLEAN,
                        foldBbToStealChance BOOLEAN,
                        foldedBbToSteal BOOLEAN,
                        foldSbToStealChance BOOLEAN,
                        foldedSbToSteal BOOLEAN,

                        street1CBChance BOOLEAN,
                        street1CBDone BOOLEAN,
                        street2CBChance BOOLEAN,
                        street2CBDone BOOLEAN,
                        street3CBChance BOOLEAN,
                        street3CBDone BOOLEAN,
                        street4CBChance BOOLEAN,
                        street4CBDone BOOLEAN,

                        foldToStreet1CBChance BOOLEAN,
                        foldToStreet1CBDone BOOLEAN,
                        foldToStreet2CBChance BOOLEAN,
                        foldToStreet2CBDone BOOLEAN,
                        foldToStreet3CBChance BOOLEAN,
                        foldToStreet3CBDone BOOLEAN,
                        foldToStreet4CBChance BOOLEAN,
                        foldToStreet4CBDone BOOLEAN,

                        street1CheckCallRaiseChance BOOLEAN,
                        street1CheckCallRaiseDone BOOLEAN,
                        street2CheckCallRaiseChance BOOLEAN,
                        street2CheckCallRaiseDone BOOLEAN,
                        street3CheckCallRaiseChance BOOLEAN,
                        street3CheckCallRaiseDone BOOLEAN,
                        street4CheckCallRaiseChance BOOLEAN,
                        street4CheckCallRaiseDone BOOLEAN,

                        street0Calls TINYINT,
                        street1Calls TINYINT,
                        street2Calls TINYINT,
                        street3Calls TINYINT,
                        street4Calls TINYINT,
                        street0Bets TINYINT,
                        street1Bets TINYINT,
                        street2Bets TINYINT,
                        street3Bets TINYINT,
                        street4Bets TINYINT,
                        street0Raises TINYINT,
                        street1Raises TINYINT,
                        street2Raises TINYINT,
                        street3Raises TINYINT,
                        street4Raises TINYINT,

                        actionString VARCHAR(15))
                        ENGINE=INNODB"""
        elif db_server == 'postgresql':
            self.query['createHandsPlayersTable'] = """CREATE TABLE HandsPlayers (
                        id BIGSERIAL, PRIMARY KEY (id),
                        handId BIGINT NOT NULL, FOREIGN KEY (handId) REFERENCES Hands(id),
                        playerId INT NOT NULL, FOREIGN KEY (playerId) REFERENCES Players(id),
                        startCash INT NOT NULL,
                        position CHAR(1),
                        seatNo SMALLINT NOT NULL,
                        sitout BOOLEAN NOT NULL,
                        wentAllInOnStreet SMALLINT,

                        card1 smallint NOT NULL,  /* 0=none, 1-13=2-Ah 14-26=2-Ad 27-39=2-Ac 40-52=2-As */
                        card2 smallint NOT NULL,
                        card3 smallint,
                        card4 smallint,
                        card5 smallint,
                        card6 smallint,
                        card7 smallint,
                        card8 smallint,  /* cards 8-20 for draw hands */
                        card9 smallint,
                        card10 smallint,
                        card11 smallint,
                        card12 smallint,
                        card13 smallint,
                        card14 smallint,
                        card15 smallint,
                        card16 smallint,
                        card17 smallint,
                        card18 smallint,
                        card19 smallint,
                        card20 smallint, 
                        startCards smallint,

                        ante INT,
                        winnings int NOT NULL,
                        rake int NOT NULL,
                        totalProfit INT,
                        comment text,
                        commentTs timestamp without time zone,
                        tourneysPlayersId BIGINT, FOREIGN KEY (tourneysPlayersId) REFERENCES TourneysPlayers(id),

                        wonWhenSeenStreet1 FLOAT,
                        wonWhenSeenStreet2 FLOAT,
                        wonWhenSeenStreet3 FLOAT,
                        wonWhenSeenStreet4 FLOAT,
                        wonAtSD FLOAT,

                        street0VPI BOOLEAN,
                        street0Aggr BOOLEAN,
                        street0_3BChance BOOLEAN,
                        street0_3BDone BOOLEAN,
                        street0_4BChance BOOLEAN,
                        street0_4BDone BOOLEAN,
                        street0_C4BChance BOOLEAN,
                        street0_C4BDone BOOLEAN,
                        street0_FoldTo3BChance BOOLEAN,
                        street0_FoldTo3BDone BOOLEAN,
                        street0_FoldTo4BChance BOOLEAN,
                        street0_FoldTo4BDone BOOLEAN,
                        street0_SqueezeChance BOOLEAN,
                        street0_SqueezeDone BOOLEAN,

                        raiseToStealChance BOOLEAN,
                        raiseToStealDone BOOLEAN,
                        success_Steal BOOLEAN,

                        street1Seen BOOLEAN,
                        street2Seen BOOLEAN,
                        street3Seen BOOLEAN,
                        street4Seen BOOLEAN,
                        sawShowdown BOOLEAN,

                        street1Aggr BOOLEAN,
                        street2Aggr BOOLEAN,
                        street3Aggr BOOLEAN,
                        street4Aggr BOOLEAN,

                        otherRaisedStreet0 BOOLEAN,
                        otherRaisedStreet1 BOOLEAN,
                        otherRaisedStreet2 BOOLEAN,
                        otherRaisedStreet3 BOOLEAN,
                        otherRaisedStreet4 BOOLEAN,
                        foldToOtherRaisedStreet0 BOOLEAN,
                        foldToOtherRaisedStreet1 BOOLEAN,
                        foldToOtherRaisedStreet2 BOOLEAN,
                        foldToOtherRaisedStreet3 BOOLEAN,
                        foldToOtherRaisedStreet4 BOOLEAN,

                        raiseFirstInChance BOOLEAN,
                        raisedFirstIn BOOLEAN,
                        foldBbToStealChance BOOLEAN,
                        foldedBbToSteal BOOLEAN,
                        foldSbToStealChance BOOLEAN,
                        foldedSbToSteal BOOLEAN,

                        street1CBChance BOOLEAN,
                        street1CBDone BOOLEAN,
                        street2CBChance BOOLEAN,
                        street2CBDone BOOLEAN,
                        street3CBChance BOOLEAN,
                        street3CBDone BOOLEAN,
                        street4CBChance BOOLEAN,
                        street4CBDone BOOLEAN,

                        foldToStreet1CBChance BOOLEAN,
                        foldToStreet1CBDone BOOLEAN,
                        foldToStreet2CBChance BOOLEAN,
                        foldToStreet2CBDone BOOLEAN,
                        foldToStreet3CBChance BOOLEAN,
                        foldToStreet3CBDone BOOLEAN,
                        foldToStreet4CBChance BOOLEAN,
                        foldToStreet4CBDone BOOLEAN,

                        street1CheckCallRaiseChance BOOLEAN,
                        street1CheckCallRaiseDone BOOLEAN,
                        street2CheckCallRaiseChance BOOLEAN,
                        street2CheckCallRaiseDone BOOLEAN,
                        street3CheckCallRaiseChance BOOLEAN,
                        street3CheckCallRaiseDone BOOLEAN,
                        street4CheckCallRaiseChance BOOLEAN,
                        street4CheckCallRaiseDone BOOLEAN,

                        street0Calls SMALLINT,
                        street1Calls SMALLINT,
                        street2Calls SMALLINT,
                        street3Calls SMALLINT,
                        street4Calls SMALLINT,
                        street0Bets SMALLINT,
                        street1Bets SMALLINT,
                        street2Bets SMALLINT,
                        street3Bets SMALLINT,
                        street4Bets SMALLINT,
                        street0Raises SMALLINT,
                        street1Raises SMALLINT,
                        street2Raises SMALLINT,
                        street3Raises SMALLINT,
                        street4Raises SMALLINT,

                        actionString VARCHAR(15))"""
        elif db_server == 'sqlite':
            self.query['createHandsPlayersTable'] = """CREATE TABLE HandsPlayers (
                        id INTEGER PRIMARY KEY,
                        handId INT NOT NULL,
                        playerId INT NOT NULL,
                        startCash INT NOT NULL,
                        position TEXT,
                        seatNo INT NOT NULL,
                        sitout BOOLEAN NOT NULL,
                        wentAllInOnStreet INT,
                    
                        card1 INT NOT NULL,  /* 0=none, 1-13=2-Ah 14-26=2-Ad 27-39=2-Ac 40-52=2-As */
                        card2 INT NOT NULL,
                        card3 INT,
                        card4 INT,
                        card5 INT,
                        card6 INT,
                        card7 INT,
                        card8 INT,  /* cards 8-20 for draw hands */
                        card9 INT,
                        card10 INT,
                        card11 INT,
                        card12 INT,
                        card13 INT,
                        card14 INT,
                        card15 INT,
                        card16 INT,
                        card17 INT,
                        card18 INT,
                        card19 INT,
                        card20 INT,
                        startCards INT,
                    
                        ante INT,
                        winnings INT NOT NULL,
                        rake INT NOT NULL,
                        totalProfit INT,
                        comment TEXT,
                        commentTs REAL,
                        tourneysPlayersId INT,

                        wonWhenSeenStreet1 REAL,
                        wonWhenSeenStreet2 REAL,
                        wonWhenSeenStreet3 REAL,
                        wonWhenSeenStreet4 REAL,
                        wonAtSD REAL,

                        street0VPI INT,
                        street0Aggr INT,
                        street0_3BChance INT,
                        street0_3BDone INT,
                        street0_4BChance INT,
                        street0_4BDone INT,
                        street0_C4BChance INT,
                        street0_C4BDone INT,
                        street0_FoldTo3BChance INT,
                        street0_FoldTo3BDone INT,
                        street0_FoldTo4BChance INT,
                        street0_FoldTo4BDone INT,
                        street0_SqueezeChance INT,
                        street0_SqueezeDone INT,

                        raiseToStealChance INT,
                        raiseToStealDone INT,
                        success_Steal INT,

                        street1Seen INT,
                        street2Seen INT,
                        street3Seen INT,
                        street4Seen INT,
                        sawShowdown INT,

                        street1Aggr INT,
                        street2Aggr INT,
                        street3Aggr INT,
                        street4Aggr INT,

                        otherRaisedStreet0 INT,
                        otherRaisedStreet1 INT,
                        otherRaisedStreet2 INT,
                        otherRaisedStreet3 INT,
                        otherRaisedStreet4 INT,
                        foldToOtherRaisedStreet0 INT,
                        foldToOtherRaisedStreet1 INT,
                        foldToOtherRaisedStreet2 INT,
                        foldToOtherRaisedStreet3 INT,
                        foldToOtherRaisedStreet4 INT,

                        raiseFirstInChance INT,
                        raisedFirstIn INT,
                        foldBbToStealChance INT,
                        foldedBbToSteal INT,
                        foldSbToStealChance INT,
                        foldedSbToSteal INT,

                        street1CBChance INT,
                        street1CBDone INT,
                        street2CBChance INT,
                        street2CBDone INT,
                        street3CBChance INT,
                        street3CBDone INT,
                        street4CBChance INT,
                        street4CBDone INT,

                        foldToStreet1CBChance INT,
                        foldToStreet1CBDone INT,
                        foldToStreet2CBChance INT,
                        foldToStreet2CBDone INT,
                        foldToStreet3CBChance INT,
                        foldToStreet3CBDone INT,
                        foldToStreet4CBChance INT,
                        foldToStreet4CBDone INT,

                        street1CheckCallRaiseChance INT,
                        street1CheckCallRaiseDone INT,
                        street2CheckCallRaiseChance INT,
                        street2CheckCallRaiseDone INT,
                        street3CheckCallRaiseChance INT,
                        street3CheckCallRaiseDone INT,
                        street4CheckCallRaiseChance INT,
                        street4CheckCallRaiseDone INT,

                        street0Calls INT,
                        street1Calls INT,
                        street2Calls INT,
                        street3Calls INT,
                        street4Calls INT,
                        street0Bets INT,
                        street1Bets INT,
                        street2Bets INT,
                        street3Bets INT,
                        street4Bets INT,
                        street0Raises INT,
                        street1Raises INT,
                        street2Raises INT,
                        street3Raises INT,
                        street4Raises INT,
                        actionString VARCHAR(15))
                        """


        ################################
        # Create TourneysPlayers
        ################################

        if db_server == 'mysql':
            self.query['createTourneysPlayersTable'] = """CREATE TABLE TourneysPlayers (
                        id BIGINT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                        tourneyId INT UNSIGNED NOT NULL, FOREIGN KEY (tourneyId) REFERENCES Tourneys(id),
                        playerId INT UNSIGNED NOT NULL, FOREIGN KEY (playerId) REFERENCES Players(id),
                        rank INT,
                        winnings INT,
                        winningsCurrency VARCHAR(4),
                        rebuyCount INT,
                        addOnCount INT,
                        koCount INT,
                        comment TEXT,
                        commentTs DATETIME)
                        ENGINE=INNODB"""
        elif db_server == 'postgresql':
            self.query['createTourneysPlayersTable'] = """CREATE TABLE TourneysPlayers (
                        id BIGSERIAL, PRIMARY KEY (id),
                        tourneyId INT, FOREIGN KEY (tourneyId) REFERENCES Tourneys(id),
                        playerId INT, FOREIGN KEY (playerId) REFERENCES Players(id),
                        rank INT,
                        winnings INT,
                        winningsCurrency VARCHAR(4),
                        rebuyCount INT,
                        addOnCount INT,
                        koCount INT,
                        comment TEXT,
                        commentTs timestamp without time zone)"""
        elif db_server == 'sqlite':
            self.query['createTourneysPlayersTable'] = """CREATE TABLE TourneysPlayers (
                        id INTEGER PRIMARY KEY,
                        tourneyId INT,
                        playerId INT,
                        rank INT,
                        winnings INT,
                        winningsCurrency VARCHAR(4),
                        rebuyCount INT,
                        addOnCount INT,
                        koCount INT,
                        comment TEXT,
                        commentTs timestamp without time zone,
                        FOREIGN KEY (tourneyId) REFERENCES Tourneys(id),
                        FOREIGN KEY (playerId) REFERENCES Players(id)
                        )"""


        ################################
        # Create HandsActions
        ################################

        if db_server == 'mysql':
            self.query['createHandsActionsTable'] = """CREATE TABLE HandsActions (
                        id BIGINT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                        handId BIGINT UNSIGNED NOT NULL, FOREIGN KEY (handId) REFERENCES Hands(id),
                        playerId INT UNSIGNED NOT NULL, FOREIGN KEY (playerId) REFERENCES Players(id),
                        street SMALLINT NOT NULL,
                        actionNo SMALLINT NOT NULL,
                        streetActionNo SMALLINT NOT NULL,
                        actionId SMALLINT UNSIGNED NOT NULL, FOREIGN KEY (actionId) REFERENCES Actions(id),
                        amount INT NOT NULL,
                        raiseTo INT NOT NULL,
                        amountCalled INT NOT NULL,
                        numDiscarded SMALLINT NOT NULL,
                        cardsDiscarded varchar(14),
                        allIn BOOLEAN NOT NULL)
                        ENGINE=INNODB"""
        elif db_server == 'postgresql':
            self.query['createHandsActionsTable'] = """CREATE TABLE HandsActions (
                        id BIGSERIAL, PRIMARY KEY (id),
                        handId BIGINT NOT NULL, FOREIGN KEY (handId) REFERENCES Hands(id),
                        playerId INT NOT NULL, FOREIGN KEY (playerId) REFERENCES Players(id),
                        street SMALLINT,
                        actionNo SMALLINT,
                        streetActionNo SMALLINT,
                        actionId SMALLINT, FOREIGN KEY (actionId) REFERENCES Actions(id),
                        amount INT,
                        raiseTo INT,
                        amountCalled INT,
                        numDiscarded SMALLINT,
                        cardsDiscarded varchar(14),
                        allIn BOOLEAN)"""
        elif db_server == 'sqlite':
            self.query['createHandsActionsTable'] = """CREATE TABLE HandsActions (
                        id INTEGER PRIMARY KEY,
                        handId INT NOT NULL,
                        playerId INT NOT NULL,
                        street SMALLINT,
                        actionNo SMALLINT,
                        streetActionNo SMALLINT,
                        actionId SMALLINT,
                        amount INT,
                        raiseTo INT,
                        amountCalled INT,
                        numDiscarded SMALLINT,
                        cardsDiscarded TEXT,
                        allIn BOOLEAN
                        )""" 


        ################################
        # Create HudCache
        ################################

        if db_server == 'mysql':
            self.query['createHudCacheTable'] = """CREATE TABLE HudCache (
                        id BIGINT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                        gametypeId SMALLINT UNSIGNED NOT NULL, FOREIGN KEY (gametypeId) REFERENCES Gametypes(id),
                        playerId INT UNSIGNED NOT NULL, FOREIGN KEY (playerId) REFERENCES Players(id),
                        activeSeats SMALLINT NOT NULL,
                        position CHAR(1),
                        tourneyTypeId SMALLINT UNSIGNED, FOREIGN KEY (tourneyTypeId) REFERENCES TourneyTypes(id),
                        styleKey CHAR(7) NOT NULL,  /* 1st char is style (A/T/H/S), other 6 are the key */
                        HDs INT NOT NULL,

                        wonWhenSeenStreet1 FLOAT,
                        wonWhenSeenStreet2 FLOAT,
                        wonWhenSeenStreet3 FLOAT,
                        wonWhenSeenStreet4 FLOAT,
                        wonAtSD FLOAT,

                        street0VPI INT,
                        street0Aggr INT,
                        street0_3BChance INT,
                        street0_3BDone INT,
                        street0_4BChance INT,
                        street0_4BDone INT,
                        street0_C4BChance INT,
                        street0_C4BDone INT,
                        street0_FoldTo3BChance INT,
                        street0_FoldTo3BDone INT,
                        street0_FoldTo4BChance INT,
                        street0_FoldTo4BDone INT,
                        street0_SqueezeChance INT,
                        street0_SqueezeDone INT,

                        raiseToStealChance INT,
                        raiseToStealDone INT,
                        success_Steal INT,


                        street1Seen INT,
                        street2Seen INT,
                        street3Seen INT,
                        street4Seen INT,
                        sawShowdown INT,
                        
                        street1Aggr INT,
                        street2Aggr INT,
                        street3Aggr INT,
                        street4Aggr INT,

                        otherRaisedStreet0 INT,
                        otherRaisedStreet1 INT,
                        otherRaisedStreet2 INT,
                        otherRaisedStreet3 INT,
                        otherRaisedStreet4 INT,
                        foldToOtherRaisedStreet0 INT,
                        foldToOtherRaisedStreet1 INT,
                        foldToOtherRaisedStreet2 INT,
                        foldToOtherRaisedStreet3 INT,
                        foldToOtherRaisedStreet4 INT,
                        
                        raiseFirstInChance INT,
                        raisedFirstIn INT,
                        foldBbToStealChance INT,
                        foldedBbToSteal INT,
                        foldSbToStealChance INT,
                        foldedSbToSteal INT,

                        street1CBChance INT,
                        street1CBDone INT,
                        street2CBChance INT,
                        street2CBDone INT,
                        street3CBChance INT,
                        street3CBDone INT,
                        street4CBChance INT,
                        street4CBDone INT,
                        
                        foldToStreet1CBChance INT,
                        foldToStreet1CBDone INT,
                        foldToStreet2CBChance INT,
                        foldToStreet2CBDone INT,
                        foldToStreet3CBChance INT,
                        foldToStreet3CBDone INT,
                        foldToStreet4CBChance INT,
                        foldToStreet4CBDone INT,
                        
                        totalProfit INT,
                        
                        street1CheckCallRaiseChance INT,
                        street1CheckCallRaiseDone INT,
                        street2CheckCallRaiseChance INT,
                        street2CheckCallRaiseDone INT,
                        street3CheckCallRaiseChance INT,
                        street3CheckCallRaiseDone INT,
                        street4CheckCallRaiseChance INT,
                        street4CheckCallRaiseDone INT,

                        street0Calls INT,
                        street1Calls INT,
                        street2Calls INT,
                        street3Calls INT,
                        street4Calls INT,
                        street0Bets INT,
                        street1Bets INT,
                        street2Bets INT,
                        street3Bets INT,
                        street4Bets INT,
                        street0Raises INT,
                        street1Raises INT,
                        street2Raises INT,
                        street3Raises INT,
                        street4Raises INT)

                        ENGINE=INNODB"""
        elif db_server == 'postgresql':
            self.query['createHudCacheTable'] = """CREATE TABLE HudCache (
                        id BIGSERIAL, PRIMARY KEY (id),
                        gametypeId INT, FOREIGN KEY (gametypeId) REFERENCES Gametypes(id),
                        playerId INT, FOREIGN KEY (playerId) REFERENCES Players(id),
                        activeSeats SMALLINT,
                        position CHAR(1),
                        tourneyTypeId INT, FOREIGN KEY (tourneyTypeId) REFERENCES TourneyTypes(id),
                        styleKey CHAR(7) NOT NULL,  /* 1st char is style (A/T/H/S), other 6 are the key */
                        HDs INT,

                        wonWhenSeenStreet1 FLOAT,
                        wonWhenSeenStreet2 FLOAT,
                        wonWhenSeenStreet3 FLOAT,
                        wonWhenSeenStreet4 FLOAT,
                        wonAtSD FLOAT,

                        street0VPI INT,
                        street0Aggr INT,
                        street0_3BChance INT,
                        street0_3BDone INT,
                        street0_4BChance INT,
                        street0_4BDone INT,
                        street0_C4BChance INT,
                        street0_C4BDone INT,
                        street0_FoldTo3BChance INT,
                        street0_FoldTo3BDone INT,
                        street0_FoldTo4BChance INT,
                        street0_FoldTo4BDone INT,
                        street0_SqueezeChance INT,
                        street0_SqueezeDone INT,

                        raiseToStealChance INT,
                        raiseToStealDone INT,
                        success_Steal INT,

                        street1Seen INT,
                        street2Seen INT,
                        street3Seen INT,
                        street4Seen INT,
                        sawShowdown INT,
                        street1Aggr INT,
                        street2Aggr INT,
                        street3Aggr INT,
                        street4Aggr INT,

                        otherRaisedStreet0 INT,
                        otherRaisedStreet1 INT,
                        otherRaisedStreet2 INT,
                        otherRaisedStreet3 INT,
                        otherRaisedStreet4 INT,
                        foldToOtherRaisedStreet0 INT,
                        foldToOtherRaisedStreet1 INT,
                        foldToOtherRaisedStreet2 INT,
                        foldToOtherRaisedStreet3 INT,
                        foldToOtherRaisedStreet4 INT,

                        raiseFirstInChance INT,
                        raisedFirstIn INT,
                        foldBbToStealChance INT,
                        foldedBbToSteal INT,
                        foldSbToStealChance INT,
                        foldedSbToSteal INT,

                        street1CBChance INT,
                        street1CBDone INT,
                        street2CBChance INT,
                        street2CBDone INT,
                        street3CBChance INT,
                        street3CBDone INT,
                        street4CBChance INT,
                        street4CBDone INT,

                        foldToStreet1CBChance INT,
                        foldToStreet1CBDone INT,
                        foldToStreet2CBChance INT,
                        foldToStreet2CBDone INT,
                        foldToStreet3CBChance INT,
                        foldToStreet3CBDone INT,
                        foldToStreet4CBChance INT,
                        foldToStreet4CBDone INT,

                        totalProfit INT,

                        street1CheckCallRaiseChance INT,
                        street1CheckCallRaiseDone INT,
                        street2CheckCallRaiseChance INT,
                        street2CheckCallRaiseDone INT,
                        street3CheckCallRaiseChance INT,
                        street3CheckCallRaiseDone INT,
                        street4CheckCallRaiseChance INT,
                        street4CheckCallRaiseDone INT,

                        street0Calls INT,
                        street1Calls INT,
                        street2Calls INT,
                        street3Calls INT,
                        street4Calls INT,
                        street0Bets INT,
                        street1Bets INT,
                        street2Bets INT,
                        street3Bets INT,
                        street4Bets INT,
                        street0Raises INT,
                        street1Raises INT,
                        street2Raises INT,
                        street3Raises INT,
                        street4Raises INT)
                        """
        elif db_server == 'sqlite':
            self.query['createHudCacheTable'] = """CREATE TABLE HudCache (
                        id INTEGER PRIMARY KEY,
                        gametypeId INT,
                        playerId INT,
                        activeSeats INT,
                        position TEXT,
                        tourneyTypeId INT,
                        styleKey TEXT NOT NULL,  /* 1st char is style (A/T/H/S), other 6 are the key */
                        HDs INT,

                        wonWhenSeenStreet1 REAL,
                        wonWhenSeenStreet2 REAL,
                        wonWhenSeenStreet3 REAL,
                        wonWhenSeenStreet4 REAL,
                        wonAtSD REAL,

                        street0VPI INT,
                        street0Aggr INT,
                        street0_3BChance INT,
                        street0_3BDone INT,
                        street0_4BChance INT,
                        street0_4BDone INT,
                        street0_C4BChance INT,
                        street0_C4BDone INT,
                        street0_FoldTo3BChance INT,
                        street0_FoldTo3BDone INT,
                        street0_FoldTo4BChance INT,
                        street0_FoldTo4BDone INT,
                        street0_SqueezeChance INT,
                        street0_SqueezeDone INT,

                        raiseToStealChance INT,
                        raiseToStealDone INT,
                        success_Steal INT,

                        street1Seen INT,
                        street2Seen INT,
                        street3Seen INT,
                        street4Seen INT,
                        sawShowdown INT,
                        street1Aggr INT,
                        street2Aggr INT,
                        street3Aggr INT,
                        street4Aggr INT,

                        otherRaisedStreet0 INT,
                        otherRaisedStreet1 INT,
                        otherRaisedStreet2 INT,
                        otherRaisedStreet3 INT,
                        otherRaisedStreet4 INT,
                        foldToOtherRaisedStreet0 INT,
                        foldToOtherRaisedStreet1 INT,
                        foldToOtherRaisedStreet2 INT,
                        foldToOtherRaisedStreet3 INT,
                        foldToOtherRaisedStreet4 INT,

                        raiseFirstInChance INT,
                        raisedFirstIn INT,
                        foldBbToStealChance INT,
                        foldedBbToSteal INT,
                        foldSbToStealChance INT,
                        foldedSbToSteal INT,

                        street1CBChance INT,
                        street1CBDone INT,
                        street2CBChance INT,
                        street2CBDone INT,
                        street3CBChance INT,
                        street3CBDone INT,
                        street4CBChance INT,
                        street4CBDone INT,

                        foldToStreet1CBChance INT,
                        foldToStreet1CBDone INT,
                        foldToStreet2CBChance INT,
                        foldToStreet2CBDone INT,
                        foldToStreet3CBChance INT,
                        foldToStreet3CBDone INT,
                        foldToStreet4CBChance INT,
                        foldToStreet4CBDone INT,

                        totalProfit INT,

                        street1CheckCallRaiseChance INT,
                        street1CheckCallRaiseDone INT,
                        street2CheckCallRaiseChance INT,
                        street2CheckCallRaiseDone INT,
                        street3CheckCallRaiseChance INT,
                        street3CheckCallRaiseDone INT,
                        street4CheckCallRaiseChance INT,
                        street4CheckCallRaiseDone INT,

                        street0Calls INT,
                        street1Calls INT,
                        street2Calls INT,
                        street3Calls INT,
                        street4Calls INT,
                        street0Bets INT,
                        street1Bets INT,
                        street2Bets INT,
                        street3Bets INT,
                        street4Bets INT,
                        street0Raises INT,
                        street1Raises INT,
                        street2Raises INT,
                        street3Raises INT,
                        street4Raises INT)
                        """
                        
        ################################
        # Create SessionsCache
        ################################

        if db_server == 'mysql':
            self.query['createSessionsCacheTable'] = """CREATE TABLE SessionsCache (
                        id BIGINT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                        sessionStart DATETIME NOT NULL,
                        sessionEnd DATETIME NOT NULL,
                        gameStart DATETIME NOT NULL,
                        gameEnd DATETIME NOT NULL,
                        sessionId BIGINT,
                        date CHAR(7) NOT NULL,  /* 1st char is style (A/T/H/S), other 6 are the key */
                        type char(7) NOT NULL,
                        gametypeId SMALLINT UNSIGNED, FOREIGN KEY (gametypeId) REFERENCES Gametypes(id),
                        tourneyTypeId SMALLINT UNSIGNED, FOREIGN KEY (tourneyTypeId) REFERENCES TourneyTypes(id),
                        playerId INT UNSIGNED NOT NULL, FOREIGN KEY (playerId) REFERENCES Players(id),
                        hands INT NOT NULL,
                        tourneys INT NOT NULL,
                        totalProfit INT)
                        ENGINE=INNODB
                        """
                        
        elif db_server == 'postgresql':
            self.query['createSessionsCacheTable'] = """CREATE TABLE SessionsCache (
                        id BIGSERIAL, PRIMARY KEY (id),
                        sessionStart REAL NOT NULL,
                        sessionEnd REAL NOT NULL,
                        gameStart REAL NOT NULL,
                        gameEnd REAL NOT NULL,
                        sessionId INT,
                        date CHAR(7) NOT NULL, /* 1st char is style (A/T/H/S), other 6 are the key */
                        type char(7),
                        gametypeId INT, FOREIGN KEY (gametypeId) REFERENCES Gametypes(id),
                        tourneyTypeId INT, FOREIGN KEY (tourneyTypeId) REFERENCES TourneyTypes(id),
                        playerId INT, FOREIGN KEY (playerId) REFERENCES Players(id),
                        hands INT,
                        tourneys INT,
                        totalProfit INT)
                        """
                        
        elif db_server == 'sqlite':
            self.query['createSessionsCacheTable'] = """CREATE TABLE SessionsCache (
                        id INTEGER PRIMARY KEY,
                        sessionStart timestamp NOT NULL,
                        sessionEnd timestamp NOT NULL,
                        gameStart timestamp NOT NULL,
                        gameEnd timestamp NOT NULL,
                        sessionId INT,
                        date TEXT NOT NULL, /* 1st char is style (A/T/H/S), other 6 are the key */
                        type TEXT,
                        gametypeId INT,
                        tourneyTypeId INT,
                        playerId INT,
                        hands INT,
                        tourneys INT,
                        totalProfit INT)
                        """
                        
        self.query['addSessionIdIndex'] = """CREATE INDEX index_SessionId ON SessionsCache (sessionId)"""
        
        self.query['addHandsSessionIdIndex'] = """CREATE INDEX index_handsSessionId ON Hands (sessionId)"""
        
        self.query['addHandsGameSessionIdIndex'] = """CREATE INDEX index_handsGameSessionId ON Hands (gameSessionId)"""

        if db_server == 'mysql':
            self.query['addTourneyIndex'] = """ALTER TABLE Tourneys ADD UNIQUE INDEX siteTourneyNo(siteTourneyNo, tourneyTypeId)"""
        elif db_server == 'postgresql':
            self.query['addTourneyIndex'] = """CREATE UNIQUE INDEX siteTourneyNo ON Tourneys (siteTourneyNo, tourneyTypeId)"""
        elif db_server == 'sqlite':
            self.query['addTourneyIndex'] = """CREATE UNIQUE INDEX siteTourneyNo ON Tourneys (siteTourneyNo, tourneyTypeId)"""

        if db_server == 'mysql':
            self.query['addHandsIndex'] = """ALTER TABLE Hands ADD UNIQUE INDEX siteHandNo(siteHandNo, gametypeId)"""
        elif db_server == 'postgresql':
            self.query['addHandsIndex'] = """CREATE UNIQUE INDEX siteHandNo ON Hands (siteHandNo, gametypeId)"""
        elif db_server == 'sqlite':
            self.query['addHandsIndex'] = """CREATE UNIQUE INDEX siteHandNo ON Hands (siteHandNo, gametypeId)"""

        if db_server == 'mysql':
            self.query['addPlayersIndex'] = """ALTER TABLE Players ADD UNIQUE INDEX name(name, siteId)"""
        elif db_server == 'postgresql':
            self.query['addPlayersIndex'] = """CREATE UNIQUE INDEX name ON Players (name, siteId)"""
        elif db_server == 'sqlite':
            self.query['addPlayersIndex'] = """CREATE UNIQUE INDEX name ON Players (name, siteId)"""

        if db_server == 'mysql':
            self.query['addTPlayersIndex'] = """ALTER TABLE TourneysPlayers ADD UNIQUE INDEX _tourneyId(tourneyId, playerId)"""
        elif db_server == 'postgresql':
            self.query['addTPlayersIndex'] = """CREATE UNIQUE INDEX tourneyId ON TourneysPlayers (tourneyId, playerId)"""
        elif db_server == 'sqlite':
            self.query['addTPlayersIndex'] = """CREATE UNIQUE INDEX tourneyId ON TourneysPlayers (tourneyId, playerId)"""

        if db_server == 'mysql':
            self.query['addTTypesIndex'] = """ALTER TABLE TourneyTypes ADD UNIQUE INDEX tourneytypes_all(siteId, buyin, fee
                                             , maxSeats, knockout, rebuy, addOn, speed, shootout, matrix, sng)"""
        elif db_server == 'postgresql':
            self.query['addTTypesIndex'] = """CREATE UNIQUE INDEX tourneyTypes_all ON TourneyTypes (siteId, buyin, fee
                                             , maxSeats, knockout, rebuy, addOn, speed, shootout, matrix, sng)"""
        elif db_server == 'sqlite':
            self.query['addTTypesIndex'] = """CREATE UNIQUE INDEX tourneyTypes_all ON TourneyTypes (siteId, buyin, fee
                                             , maxSeats, knockout, rebuy, addOn, speed, shootout, matrix, sng)"""

        self.query['get_last_hand'] = "select max(id) from Hands"
        
        self.query['get_last_date'] = "SELECT MAX(startTime) FROM Hands"
        
        self.query['get_first_date'] = "SELECT MIN(startTime) FROM Hands"

        self.query['get_player_id'] = """
                select Players.id AS player_id 
                from Players, Sites
                where Players.name = %s
                and Sites.name = %s
                and Players.siteId = Sites.id
            """

        self.query['get_player_names'] = """
                select p.name
                from Players p
                where lower(p.name) like lower(%s)
                and   (p.siteId = %s or %s = -1)
            """

        self.query['get_gameinfo_from_hid'] = """
                SELECT
                        s.name,
                        g.category,
                        g.base,
                        g.type,
                        g.limitType,
                        g.hilo,
                        round(g.smallBlind / 100.0,2),
                        round(g.bigBlind / 100.0,2),
                        round(g.smallBet / 100.0,2),
                        round(g.bigBet / 100.0,2),
                        g.currency
                    FROM
                        Hands as h,
                        Sites as s,
                        Gametypes as g,
                        HandsPlayers as hp,
                        Players as p
                    WHERE
                        h.id = %s
                    and g.id = h.gametypeid
                    and hp.handid = h.id
                    and p.id = hp.playerid
                    and s.id = p.siteid
                    limit 1
            """

        self.query['get_stats_from_hand'] = """
                SELECT hc.playerId                      AS player_id,
                    hp.seatNo                           AS seat,
                    p.name                              AS screen_name,
                    sum(hc.HDs)                         AS n,
                    sum(hc.street0VPI)                  AS vpip,
                    sum(hc.street0Aggr)                 AS pfr,
                    sum(hc.street0_3BChance)            AS TB_opp_0,
                    sum(hc.street0_3BDone)              AS TB_0,
                    sum(hc.street0_4BChance)            AS FB_opp_0,
                    sum(hc.street0_4BDone)              AS FB_0,
                    sum(hc.street0_C4BChance)           AS CFB_opp_0,
                    sum(hc.street0_C4BDone)             AS CFB_0,
                    sum(hc.street0_FoldTo3BChance)      AS F3B_opp_0,
                    sum(hc.street0_FoldTo3BDone)        AS F3B_0,
                    sum(hc.street0_FoldTo4BChance)      AS F4B_opp_0,
                    sum(hc.street0_FoldTo4BDone)        AS F4B_0,
                    sum(hc.street0_SqueezeChance)       AS SQZ_opp_0,
                    sum(hc.street0_SqueezeDone)         AS SQZ_0,
                    sum(hc.raiseToStealChance)          AS RTS_opp,
                    sum(hc.raiseToStealDone)            AS RTS,
                    sum(hc.success_Steal)               AS SUC_ST,
                    sum(hc.street1Seen)                 AS saw_f,
                    sum(hc.street1Seen)                 AS saw_1,
                    sum(hc.street2Seen)                 AS saw_2,
                    sum(hc.street3Seen)                 AS saw_3,
                    sum(hc.street4Seen)                 AS saw_4,
                    sum(hc.sawShowdown)                 AS sd,
                    sum(hc.street1Aggr)                 AS aggr_1,
                    sum(hc.street2Aggr)                 AS aggr_2,
                    sum(hc.street3Aggr)                 AS aggr_3,
                    sum(hc.street4Aggr)                 AS aggr_4,
                    sum(hc.otherRaisedStreet1)          AS was_raised_1,
                    sum(hc.otherRaisedStreet2)          AS was_raised_2,
                    sum(hc.otherRaisedStreet3)          AS was_raised_3,
                    sum(hc.otherRaisedStreet4)          AS was_raised_4,
                    sum(hc.foldToOtherRaisedStreet1)    AS f_freq_1,
                    sum(hc.foldToOtherRaisedStreet2)    AS f_freq_2,
                    sum(hc.foldToOtherRaisedStreet3)    AS f_freq_3,
                    sum(hc.foldToOtherRaisedStreet4)    AS f_freq_4,
                    sum(hc.wonWhenSeenStreet1)          AS w_w_s_1,
                    sum(hc.wonAtSD)                     AS wmsd,
                    sum(case hc.position
                        when 'S' then hc.raiseFirstInChance
                        when '0' then hc.raiseFirstInChance
                        when '1' then hc.raiseFirstInChance
                        else 0
                       )                                AS steal_opp,
                    sum(case hc.position
                        when 'S' then hc.raisedFirstIn
                        when '0' then hc.raisedFirstIn
                        when '1' then hc.raisedFirstIn
                        else 0
                       )                                AS steal,
                    sum(hc.foldSbToStealChance)         AS SBstolen,
                    sum(hc.foldedSbToSteal)             AS SBnotDef,
                    sum(hc.foldBbToStealChance)         AS BBstolen,
                    sum(hc.foldedBbToSteal)             AS BBnotDef,
                    sum(hc.street1CBChance)             AS CB_opp_1,
                    sum(hc.street1CBDone)               AS CB_1,
                    sum(hc.street2CBChance)             AS CB_opp_2,
                    sum(hc.street2CBDone)               AS CB_2,
                    sum(hc.street3CBChance)             AS CB_opp_3,
                    sum(hc.street3CBDone)               AS CB_3,
                    sum(hc.street4CBChance)             AS CB_opp_4,
                    sum(hc.street4CBDone)               AS CB_4,
                    sum(hc.foldToStreet1CBChance)       AS f_cb_opp_1,
                    sum(hc.foldToStreet1CBDone)         AS f_cb_1,
                    sum(hc.foldToStreet2CBChance)       AS f_cb_opp_2,
                    sum(hc.foldToStreet2CBDone)         AS f_cb_2,
                    sum(hc.foldToStreet3CBChance)       AS f_cb_opp_3,
                    sum(hc.foldToStreet3CBDone)         AS f_cb_3,
                    sum(hc.foldToStreet4CBChance)       AS f_cb_opp_4,
                    sum(hc.foldToStreet4CBDone)         AS f_cb_4,
                    sum(hc.totalProfit)                 AS net,
                    sum(gt.bigblind)                    AS bigblind,
                    sum(hc.street1CheckCallRaiseChance) AS ccr_opp_1,
                    sum(hc.street1CheckCallRaiseDone)   AS ccr_1,
                    sum(hc.street2CheckCallRaiseChance) AS ccr_opp_2,
                    sum(hc.street2CheckCallRaiseDone)   AS ccr_2,
                    sum(hc.street3CheckCallRaiseChance) AS ccr_opp_3,
                    sum(hc.street3CheckCallRaiseDone)   AS ccr_3,
                    sum(hc.street4CheckCallRaiseChance) AS ccr_opp_4,
                    sum(hc.street4CheckCallRaiseDone)   AS ccr_4
                    sum(hc.street0Calls)                AS call_0,
                    sum(hc.street1Calls)                AS call_1,
                    sum(hc.street2Calls)                AS call_2,
                    sum(hc.street3Calls)                AS call_3,
                    sum(hc.street4Calls)                AS call_4,
                    sum(hc.street0Bets)                 AS bet_0,
                    sum(hc.street1Bets)                 AS bet_1,
                    sum(hc.street2Bets)                 AS bet_2,
                    sum(hc.street3Bets)                 AS bet_3,
                    sum(hc.street4Bets)                 AS bet_4,
                    sum(hc.street0Raises)               AS raise_0,
                    sum(hc.street1Raises)               AS raise_1,
                    sum(hc.street2Raises)               AS raise_2,
                    sum(hc.street3Raises)               AS raise_3,
                    sum(hc.street4Raises)               AS raise_4
                FROM Hands h
                     INNER JOIN HandsPlayers hp ON (hp.handId = h.id)
                     INNER JOIN HudCache hc ON (    hc.PlayerId = hp.PlayerId+0
                                                AND hc.gametypeId+0 = h.gametypeId+0)
                     INNER JOIN Players p ON (p.id = hp.PlayerId+0)
                     INNER JOIN Gametypes gt ON (gt.id = hc.gametypeId)
                WHERE h.id = %s
                AND   hc.styleKey > %s
                      /* styleKey is currently 'd' (for date) followed by a yyyymmdd
                         date key. Set it to 0000000 or similar to get all records  */
                /* also check activeseats here even if only 3 groups eg 2-3/4-6/7+ 
                   e.g. could use a multiplier:
                   AND   h.seats > X / 1.25  and  hp.seats < X * 1.25
                   where X is the number of active players at the current table (and
                   1.25 would be a config value so user could change it)
                */
                GROUP BY hc.PlayerId, hp.seatNo, p.name
                ORDER BY hc.PlayerId, hp.seatNo, p.name
            """

#    same as above except stats are aggregated for all blind/limit levels
        self.query['get_stats_from_hand_aggregated'] = """
                /* explain query plan */
                SELECT hc.playerId                         AS player_id,
                       max(case when hc.gametypeId = h.gametypeId
                                then hp.seatNo
                                else -1
                           end)                            AS seat,
                       p.name                              AS screen_name,
                       sum(hc.HDs)                         AS n,
                       sum(hc.street0VPI)                  AS vpip,
                       sum(hc.street0Aggr)                 AS pfr,
                       sum(hc.street0_3BChance)            AS TB_opp_0,
                       sum(hc.street0_3BDone)              AS TB_0,
                       sum(hc.street0_4BChance)            AS FB_opp_0,
                       sum(hc.street0_4BDone)              AS FB_0,
                       sum(hc.street0_C4BChance)           AS CFB_opp_0,
                       sum(hc.street0_C4BDone)             AS CFB_0,
                       sum(hc.street0_FoldTo3BChance)      AS F3B_opp_0,
                       sum(hc.street0_FoldTo3BDone)        AS F3B_0,
                       sum(hc.street0_FoldTo4BChance)      AS F4B_opp_0,
                       sum(hc.street0_FoldTo4BDone)        AS F4B_0,
                       sum(hc.street0_SqueezeChance)       AS SQZ_opp_0,
                       sum(hc.street0_SqueezeDone)         AS SQZ_0,
                       sum(hc.raiseToStealChance)          AS RTS_opp,
                       sum(hc.raiseToStealDone)            AS RTS,
                       sum(hc.success_Steal)               AS SUC_ST,
                       sum(hc.street1Seen)                 AS saw_f,
                       sum(hc.street1Seen)                 AS saw_1,
                       sum(hc.street2Seen)                 AS saw_2,
                       sum(hc.street3Seen)                 AS saw_3,
                       sum(hc.street4Seen)                 AS saw_4,
                       sum(hc.sawShowdown)                 AS sd,
                       sum(hc.street1Aggr)                 AS aggr_1,
                       sum(hc.street2Aggr)                 AS aggr_2,
                       sum(hc.street3Aggr)                 AS aggr_3,
                       sum(hc.street4Aggr)                 AS aggr_4,
                       sum(hc.otherRaisedStreet1)          AS was_raised_1,
                       sum(hc.otherRaisedStreet2)          AS was_raised_2,
                       sum(hc.otherRaisedStreet3)          AS was_raised_3,
                       sum(hc.otherRaisedStreet4)          AS was_raised_4,
                       sum(hc.foldToOtherRaisedStreet1)    AS f_freq_1,
                       sum(hc.foldToOtherRaisedStreet2)    AS f_freq_2,
                       sum(hc.foldToOtherRaisedStreet3)    AS f_freq_3,
                       sum(hc.foldToOtherRaisedStreet4)    AS f_freq_4,
                       sum(hc.wonWhenSeenStreet1)          AS w_w_s_1,
                       sum(hc.wonAtSD)                     AS wmsd,
                       sum(hc.raiseFirstInChance)          AS steal_opp,
                       sum(hc.raisedFirstIn)               AS steal,
                       sum(hc.foldSbToStealChance)         AS SBstolen,
                       sum(hc.foldedSbToSteal)             AS SBnotDef,
                       sum(hc.foldBbToStealChance)         AS BBstolen,
                       sum(hc.foldedBbToSteal)             AS BBnotDef,
                       sum(hc.street1CBChance)             AS CB_opp_1,
                       sum(hc.street1CBDone)               AS CB_1,
                       sum(hc.street2CBChance)             AS CB_opp_2,
                       sum(hc.street2CBDone)               AS CB_2,
                       sum(hc.street3CBChance)             AS CB_opp_3,
                       sum(hc.street3CBDone)               AS CB_3,
                       sum(hc.street4CBChance)             AS CB_opp_4,
                       sum(hc.street4CBDone)               AS CB_4,
                       sum(hc.foldToStreet1CBChance)       AS f_cb_opp_1,
                       sum(hc.foldToStreet1CBDone)         AS f_cb_1,
                       sum(hc.foldToStreet2CBChance)       AS f_cb_opp_2,
                       sum(hc.foldToStreet2CBDone)         AS f_cb_2,
                       sum(hc.foldToStreet3CBChance)       AS f_cb_opp_3,
                       sum(hc.foldToStreet3CBDone)         AS f_cb_3,
                       sum(hc.foldToStreet4CBChance)       AS f_cb_opp_4,
                       sum(hc.foldToStreet4CBDone)         AS f_cb_4,
                       sum(hc.totalProfit)                 AS net,
                       sum(gt.bigblind)                    AS bigblind,
                       sum(hc.street1CheckCallRaiseChance) AS ccr_opp_1,
                       sum(hc.street1CheckCallRaiseDone)   AS ccr_1,
                       sum(hc.street2CheckCallRaiseChance) AS ccr_opp_2,
                       sum(hc.street2CheckCallRaiseDone)   AS ccr_2,
                       sum(hc.street3CheckCallRaiseChance) AS ccr_opp_3,
                       sum(hc.street3CheckCallRaiseDone)   AS ccr_3,
                       sum(hc.street4CheckCallRaiseChance) AS ccr_opp_4,
                       sum(hc.street4CheckCallRaiseDone)   AS ccr_4,
                       sum(hc.street0Calls)                AS call_0,
                       sum(hc.street1Calls)                AS call_1,
                       sum(hc.street2Calls)                AS call_2,
                       sum(hc.street3Calls)                AS call_3,
                       sum(hc.street4Calls)                AS call_4,
                       sum(hc.street0Bets)                 AS bet_0,
                       sum(hc.street1Bets)                 AS bet_1,
                       sum(hc.street2Bets)                 AS bet_2,
                       sum(hc.street3Bets)                 AS bet_3,
                       sum(hc.street4Bets)                 AS bet_4,
                       sum(hc.street0Raises)               AS raise_0,
                       sum(hc.street1Raises)               AS raise_1,
                       sum(hc.street2Raises)               AS raise_2,
                       sum(hc.street3Raises)               AS raise_3,
                       sum(hc.street4Raises)               AS raise_4
                FROM Hands h
                     INNER JOIN HandsPlayers hp ON (hp.handId = h.id)
                     INNER JOIN HudCache hc     ON (hc.playerId = hp.playerId)
                     INNER JOIN Players p       ON (p.id = hc.playerId)
                     INNER JOIN Gametypes gt    ON (gt.id = hc.gametypeId)
                WHERE h.id = %s
                AND   (   /* 2 separate parts for hero and opponents */
                          (    hp.playerId != %s
                           AND hc.styleKey > %s
                           AND hc.gametypeId+0 in
                                 (SELECT gt1.id from Gametypes gt1, Gametypes gt2
                                  WHERE  gt1.siteid = gt2.siteid  /* find gametypes where these match: */
                                  AND    gt1.type = gt2.type               /* ring/tourney */
                                  AND    gt1.category = gt2.category       /* holdem/stud*/
                                  AND    gt1.limittype = gt2.limittype     /* fl/nl */
                                  AND    gt1.bigblind <= gt2.bigblind * %s  /* bigblind similar size */
                                  AND    gt1.bigblind >= gt2.bigblind / %s
                                  AND    gt2.id = h.gametypeId)
                           AND hc.activeSeats between %s and %s
                          )
                       OR
                          (    hp.playerId = %s
                           AND hc.styleKey > %s
                           AND hc.gametypeId+0 in
                                 (SELECT gt1.id from Gametypes gt1, Gametypes gt2
                                  WHERE  gt1.siteid = gt2.siteid  /* find gametypes where these match: */
                                  AND    gt1.type = gt2.type               /* ring/tourney */
                                  AND    gt1.category = gt2.category       /* holdem/stud*/
                                  AND    gt1.limittype = gt2.limittype     /* fl/nl */
                                  AND    gt1.bigblind <= gt2.bigblind * %s  /* bigblind similar size */
                                  AND    gt1.bigblind >= gt2.bigblind / %s
                                  AND    gt2.id = h.gametypeId)
                           AND hc.activeSeats between %s and %s
                          )
                      )
                GROUP BY hc.PlayerId, p.name
                ORDER BY hc.PlayerId, p.name
            """
                #  NOTES on above cursor:
                #  - Do NOT include %s inside query in a comment - the db api thinks 
                #  they are actual arguments.
                #  - styleKey is currently 'd' (for date) followed by a yyyymmdd
                #  date key. Set it to 0000000 or similar to get all records
                #  Could also check activeseats here even if only 3 groups eg 2-3/4-6/7+ 
                #  e.g. could use a multiplier:
                #  AND   h.seats > %s / 1.25  and  hp.seats < %s * 1.25
                #  where %s is the number of active players at the current table (and
                #  1.25 would be a config value so user could change it)

        if db_server == 'mysql':
            self.query['get_stats_from_hand_session'] = """
                    SELECT hp.playerId                                              AS player_id, /* playerId and seats must */
                           h.seats                                                  AS seats,     /* be first and second field */
                           hp.handId                                                AS hand_id,
                           hp.seatNo                                                AS seat,
                           p.name                                                   AS screen_name,
                           1                                                        AS n,
                           cast(hp2.street0VPI as <signed>integer)                  AS vpip,
                           cast(hp2.street0Aggr as <signed>integer)                 AS pfr,
                           cast(hp2.street0_3BChance as <signed>integer)            AS TB_opp_0,
                           cast(hp2.street0_3BDone as <signed>integer)              AS TB_0,
                           cast(hp2.street0_4BChance as <signed>integer)            AS FB_opp_0,
                           cast(hp2.street0_4BDone as <signed>integer)              AS FB_0,
                           cast(hp2.street0_C4BChance as <signed>integer)           AS CFB_opp_0,
                           cast(hp2.street0_C4BDone as <signed>integer)             AS CFB_0,
                           cast(hp2.street0_FoldTo3BChance as <signed>integer)      AS F3B_opp_0,
                           cast(hp2.street0_FoldTo3BDone as <signed>integer)        AS F3B_0,
                           cast(hp2.street0_FoldTo4BChance as <signed>integer)      AS F4B_opp_0,
                           cast(hp2.street0_FoldTo4BDone as <signed>integer)        AS F4B_0,
                           cast(hp2.street0_SqueezeChance as <signed>integer)       AS SQZ_opp_0,
                           cast(hp2.street0_SqueezeDone as <signed>integer)         AS SQZ_0,
                           cast(hp2.raiseToStealChance as <signed>integer)          AS RTS_opp,
                           cast(hp2.raiseToStealDone as <signed>integer)            AS RTS,
                           cast(hp2.success_Steal as <signed>integer)               AS SUC_ST,
                           cast(hp2.street1Seen as <signed>integer)                 AS saw_f,
                           cast(hp2.street1Seen as <signed>integer)                 AS saw_1,
                           cast(hp2.street2Seen as <signed>integer)                 AS saw_2,
                           cast(hp2.street3Seen as <signed>integer)                 AS saw_3,
                           cast(hp2.street4Seen as <signed>integer)                 AS saw_4,
                           cast(hp2.sawShowdown as <signed>integer)                 AS sd,
                           cast(hp2.street1Aggr as <signed>integer)                 AS aggr_1,
                           cast(hp2.street2Aggr as <signed>integer)                 AS aggr_2,
                           cast(hp2.street3Aggr as <signed>integer)                 AS aggr_3,
                           cast(hp2.street4Aggr as <signed>integer)                 AS aggr_4,
                           cast(hp2.otherRaisedStreet1 as <signed>integer)          AS was_raised_1,
                           cast(hp2.otherRaisedStreet2 as <signed>integer)          AS was_raised_2,
                           cast(hp2.otherRaisedStreet3 as <signed>integer)          AS was_raised_3,
                           cast(hp2.otherRaisedStreet4 as <signed>integer)          AS was_raised_4,
                           cast(hp2.foldToOtherRaisedStreet1 as <signed>integer)    AS f_freq_1,
                           cast(hp2.foldToOtherRaisedStreet2 as <signed>integer)    AS f_freq_2,
                           cast(hp2.foldToOtherRaisedStreet3 as <signed>integer)    AS f_freq_3,
                           cast(hp2.foldToOtherRaisedStreet4 as <signed>integer)    AS f_freq_4,
                           cast(hp2.wonWhenSeenStreet1 as <signed>integer)          AS w_w_s_1,
                           cast(hp2.wonAtSD as <signed>integer)                     AS wmsd,
                           cast(hp2.raiseFirstInChance as <signed>integer)          AS steal_opp,
                           cast(hp2.raisedFirstIn as <signed>integer)               AS steal,
                           cast(hp2.foldSbToStealChance as <signed>integer)         AS SBstolen,
                           cast(hp2.foldedSbToSteal as <signed>integer)             AS SBnotDef,
                           cast(hp2.foldBbToStealChance as <signed>integer)         AS BBstolen,
                           cast(hp2.foldedBbToSteal as <signed>integer)             AS BBnotDef,
                           cast(hp2.street1CBChance as <signed>integer)             AS CB_opp_1,
                           cast(hp2.street1CBDone as <signed>integer)               AS CB_1,
                           cast(hp2.street2CBChance as <signed>integer)             AS CB_opp_2,
                           cast(hp2.street2CBDone as <signed>integer)               AS CB_2,
                           cast(hp2.street3CBChance as <signed>integer)             AS CB_opp_3,
                           cast(hp2.street3CBDone as <signed>integer)               AS CB_3,
                           cast(hp2.street4CBChance as <signed>integer)             AS CB_opp_4,
                           cast(hp2.street4CBDone as <signed>integer)               AS CB_4,
                           cast(hp2.foldToStreet1CBChance as <signed>integer)       AS f_cb_opp_1,
                           cast(hp2.foldToStreet1CBDone as <signed>integer)         AS f_cb_1,
                           cast(hp2.foldToStreet2CBChance as <signed>integer)       AS f_cb_opp_2,
                           cast(hp2.foldToStreet2CBDone as <signed>integer)         AS f_cb_2,
                           cast(hp2.foldToStreet3CBChance as <signed>integer)       AS f_cb_opp_3,
                           cast(hp2.foldToStreet3CBDone as <signed>integer)         AS f_cb_3,
                           cast(hp2.foldToStreet4CBChance as <signed>integer)       AS f_cb_opp_4,
                           cast(hp2.foldToStreet4CBDone as <signed>integer)         AS f_cb_4,
                           cast(hp2.totalProfit as <signed>integer)                 AS net,
                           cast(gt.bigblind as <signed>integer)                     AS bigblind,
                           cast(hp2.street1CheckCallRaiseChance as <signed>integer) AS ccr_opp_1,
                           cast(hp2.street1CheckCallRaiseDone as <signed>integer)   AS ccr_1,
                           cast(hp2.street2CheckCallRaiseChance as <signed>integer) AS ccr_opp_2,
                           cast(hp2.street2CheckCallRaiseDone as <signed>integer)   AS ccr_2,
                           cast(hp2.street3CheckCallRaiseChance as <signed>integer) AS ccr_opp_3,
                           cast(hp2.street3CheckCallRaiseDone as <signed>integer)   AS ccr_3,
                           cast(hp2.street4CheckCallRaiseChance as <signed>integer) AS ccr_opp_4,
                           cast(hp2.street4CheckCallRaiseDone as <signed>integer)   AS ccr_4,
                           cast(hp2.street0Calls as <signed>integer)                AS call_0,
                           cast(hp2.street1Calls as <signed>integer)                AS call_1,
                           cast(hp2.street2Calls as <signed>integer)                AS call_2,
                           cast(hp2.street3Calls as <signed>integer)                AS call_3,
                           cast(hp2.street4Calls as <signed>integer)                AS call_4,
                           cast(hp2.street0Bets as <signed>integer)                 AS bet_0,
                           cast(hp2.street1Bets as <signed>integer)                 AS bet_1,
                           cast(hp2.street2Bets as <signed>integer)                 AS bet_2,
                           cast(hp2.street3Bets as <signed>integer)                 AS bet_3,
                           cast(hp2.street4Bets as <signed>integer)                 AS bet_4,
                           cast(hp2.street0Raises as <signed>integer)               AS raise_0,
                           cast(hp2.street1Raises as <signed>integer)               AS raise_1,
                           cast(hp2.street2Raises as <signed>integer)               AS raise_2,
                           cast(hp2.street3Raises as <signed>integer)               AS raise_3,
                           cast(hp2.street4Raises as <signed>integer)               AS raise_4
                    FROM
                         Hands h
                         INNER JOIN Hands h2         ON (h2.id >= %s AND   h2.tableName = h.tableName)
                         INNER JOIN HandsPlayers hp  ON (h.id = hp.handId)         /* players in this hand */
                         INNER JOIN HandsPlayers hp2 ON (hp2.playerId+0 = hp.playerId+0 AND (hp2.handId = h2.id+0))  /* other hands by these players */
                         INNER JOIN Players p        ON (p.id = hp2.PlayerId+0)
                         INNER JOIN Gametypes gt     ON (gt.id = h2.gametypeId)
                    WHERE hp.handId = %s
                    /* check activeseats once this data returned (don't want to do that here as it might
                       assume a session ended just because the number of seats dipped for a few hands)
                    */
                    AND   (   /* 2 separate parts for hero and opponents */
                              (    hp2.playerId != %s
                               AND h2.seats between %s and %s
                              )
                           OR
                              (    hp2.playerId = %s
                               AND h2.seats between %s and %s
                              )
                          )
                    ORDER BY h.startTime desc, hp2.PlayerId
                    /* order rows by handstart descending so that we can stop reading rows when
                       there's a gap over X minutes between hands (ie. when we get back to start of
                       the session */
                """
        elif db_server == 'postgresql':
            self.query['get_stats_from_hand_session'] = """
                    SELECT hp.playerId                                              AS player_id,
                           hp.handId                                                AS hand_id,
                           hp.seatNo                                                AS seat,
                           p.name                                                   AS screen_name,
                           h.seats                                                  AS seats,
                           1                                                        AS n,
                           cast(hp2.street0VPI as <signed>integer)                  AS vpip,
                           cast(hp2.street0Aggr as <signed>integer)                 AS pfr,
                           cast(hp2.street0_3BChance as <signed>integer)            AS TB_opp_0,
                           cast(hp2.street0_3BDone as <signed>integer)              AS TB_0,
                           cast(hp2.street0_4BChance as <signed>integer)            AS FB_opp_0,
                           cast(hp2.street0_4BDone as <signed>integer)              AS FB_0,
                           cast(hp2.street0_C4BChance as <signed>integer)           AS CFB_opp_0,
                           cast(hp2.street0_C4BDone as <signed>integer)             AS CFB_0,
                           cast(hp2.street0_FoldTo3BChance as <signed>integer)      AS F3B_opp_0,
                           cast(hp2.street0_FoldTo3BDone as <signed>integer)        AS F3B_0,
                           cast(hp2.street0_FoldTo4BChance as <signed>integer)      AS F4B_opp_0,
                           cast(hp2.street0_FoldTo4BDone as <signed>integer)        AS F4B_0,
                           cast(hp2.street0_SqueezeChance as <signed>integer)       AS SQZ_opp_0,
                           cast(hp2.street0_SqueezeDone as <signed>integer)         AS SQZ_0,
                           cast(hp2.raiseToStealChance as <signed>integer)          AS RTS_opp,
                           cast(hp2.raiseToStealDone as <signed>integer)            AS RTS,
                           cast(hp2.success_Steal as <signed>integer)               AS SUC_ST,
                           cast(hp2.street1Seen as <signed>integer)                 AS saw_f,
                           cast(hp2.street1Seen as <signed>integer)                 AS saw_1,
                           cast(hp2.street2Seen as <signed>integer)                 AS saw_2,
                           cast(hp2.street3Seen as <signed>integer)                 AS saw_3,
                           cast(hp2.street4Seen as <signed>integer)                 AS saw_4,
                           cast(hp2.sawShowdown as <signed>integer)                 AS sd,
                           cast(hp2.street1Aggr as <signed>integer)                 AS aggr_1,
                           cast(hp2.street2Aggr as <signed>integer)                 AS aggr_2,
                           cast(hp2.street3Aggr as <signed>integer)                 AS aggr_3,
                           cast(hp2.street4Aggr as <signed>integer)                 AS aggr_4,
                           cast(hp2.otherRaisedStreet1 as <signed>integer)          AS was_raised_1,
                           cast(hp2.otherRaisedStreet2 as <signed>integer)          AS was_raised_2,
                           cast(hp2.otherRaisedStreet3 as <signed>integer)          AS was_raised_3,
                           cast(hp2.otherRaisedStreet4 as <signed>integer)          AS was_raised_4,
                           cast(hp2.foldToOtherRaisedStreet1 as <signed>integer)    AS f_freq_1,
                           cast(hp2.foldToOtherRaisedStreet2 as <signed>integer)    AS f_freq_2,
                           cast(hp2.foldToOtherRaisedStreet3 as <signed>integer)    AS f_freq_3,
                           cast(hp2.foldToOtherRaisedStreet4 as <signed>integer)    AS f_freq_4,
                           cast(hp2.wonWhenSeenStreet1 as <signed>integer)          AS w_w_s_1,
                           cast(hp2.wonAtSD as <signed>integer)                     AS wmsd,
                           cast(hp2.raiseFirstInChance as <signed>integer)          AS steal_opp,
                           cast(hp2.raisedFirstIn as <signed>integer)               AS steal,
                           cast(hp2.foldSbToStealChance as <signed>integer)         AS SBstolen,
                           cast(hp2.foldedSbToSteal as <signed>integer)             AS SBnotDef,
                           cast(hp2.foldBbToStealChance as <signed>integer)         AS BBstolen,
                           cast(hp2.foldedBbToSteal as <signed>integer)             AS BBnotDef,
                           cast(hp2.street1CBChance as <signed>integer)             AS CB_opp_1,
                           cast(hp2.street1CBDone as <signed>integer)               AS CB_1,
                           cast(hp2.street2CBChance as <signed>integer)             AS CB_opp_2,
                           cast(hp2.street2CBDone as <signed>integer)               AS CB_2,
                           cast(hp2.street3CBChance as <signed>integer)             AS CB_opp_3,
                           cast(hp2.street3CBDone as <signed>integer)               AS CB_3,
                           cast(hp2.street4CBChance as <signed>integer)             AS CB_opp_4,
                           cast(hp2.street4CBDone as <signed>integer)               AS CB_4,
                           cast(hp2.foldToStreet1CBChance as <signed>integer)       AS f_cb_opp_1,
                           cast(hp2.foldToStreet1CBDone as <signed>integer)         AS f_cb_1,
                           cast(hp2.foldToStreet2CBChance as <signed>integer)       AS f_cb_opp_2,
                           cast(hp2.foldToStreet2CBDone as <signed>integer)         AS f_cb_2,
                           cast(hp2.foldToStreet3CBChance as <signed>integer)       AS f_cb_opp_3,
                           cast(hp2.foldToStreet3CBDone as <signed>integer)         AS f_cb_3,
                           cast(hp2.foldToStreet4CBChance as <signed>integer)       AS f_cb_opp_4,
                           cast(hp2.foldToStreet4CBDone as <signed>integer)         AS f_cb_4,
                           cast(hp2.totalProfit as <signed>integer)                 AS net,
                           cast(gt.bigblind as <signed>integer)                     AS bigblind,
                           cast(hp2.street1CheckCallRaiseChance as <signed>integer) AS ccr_opp_1,
                           cast(hp2.street1CheckCallRaiseDone as <signed>integer)   AS ccr_1,
                           cast(hp2.street2CheckCallRaiseChance as <signed>integer) AS ccr_opp_2,
                           cast(hp2.street2CheckCallRaiseDone as <signed>integer)   AS ccr_2,
                           cast(hp2.street3CheckCallRaiseChance as <signed>integer) AS ccr_opp_3,
                           cast(hp2.street3CheckCallRaiseDone as <signed>integer)   AS ccr_3,
                           cast(hp2.street4CheckCallRaiseChance as <signed>integer) AS ccr_opp_4,
                           cast(hp2.street4CheckCallRaiseDone as <signed>integer)   AS ccr_4,
                           cast(hp2.street0Calls as <signed>integer)                AS call_0,
                           cast(hp2.street1Calls as <signed>integer)                AS call_1,
                           cast(hp2.street2Calls as <signed>integer)                AS call_2,
                           cast(hp2.street3Calls as <signed>integer)                AS call_3,
                           cast(hp2.street4Calls as <signed>integer)                AS call_4,
                           cast(hp2.street0Bets as <signed>integer)                 AS bet_0,
                           cast(hp2.street1Bets as <signed>integer)                 AS bet_1,
                           cast(hp2.street2Bets as <signed>integer)                 AS bet_2,
                           cast(hp2.street3Bets as <signed>integer)                 AS bet_3,
                           cast(hp2.street4Bets as <signed>integer)                 AS bet_4,
                           cast(hp2.street0Raises as <signed>integer)               AS raise_0,
                           cast(hp2.street1Raises as <signed>integer)               AS raise_1,
                           cast(hp2.street2Raises as <signed>integer)               AS raise_2,
                           cast(hp2.street3Raises as <signed>integer)               AS raise_3,
                           cast(hp2.street4Raises as <signed>integer)               AS raise_4
                         FROM Hands h                                                  /* this hand */
                         INNER JOIN Hands h2         ON (    h2.id >= %s           /* other hands */
                                                         AND h2.tableName = h.tableName)
                         INNER JOIN HandsPlayers hp  ON (h.id = hp.handId)        /* players in this hand */
                         INNER JOIN HandsPlayers hp2 ON (    hp2.playerId+0 = hp.playerId+0
                                                         AND hp2.handId = h2.id)  /* other hands by these players */
                         INNER JOIN Players p        ON (p.id = hp2.PlayerId+0)
                         INNER JOIN Gametypes gt     ON (gt.id = h2.gametypeId)
                    WHERE h.id = %s
                    /* check activeseats once this data returned (don't want to do that here as it might
                       assume a session ended just because the number of seats dipped for a few hands)
                    */
                    AND   (   /* 2 separate parts for hero and opponents */
                              (    hp2.playerId != %s
                               AND h2.seats between %s and %s
                              )
                           OR
                              (    hp2.playerId = %s
                               AND h2.seats between %s and %s
                              )
                          )
                    ORDER BY h.startTime desc, hp2.PlayerId
                    /* order rows by handstart descending so that we can stop reading rows when
                       there's a gap over X minutes between hands (ie. when we get back to start of
                       the session */
                """
        elif db_server == 'sqlite':
            self.query['get_stats_from_hand_session'] = """
                    SELECT hp.playerId                                              AS player_id,
                           hp.handId                                                AS hand_id,
                           hp.seatNo                                                AS seat,
                           p.name                                                   AS screen_name,
                           h.seats                                                  AS seats,
                           1                                                        AS n,
                           cast(hp2.street0VPI as <signed>integer)                  AS vpip,
                           cast(hp2.street0Aggr as <signed>integer)                 AS pfr,
                           cast(hp2.street0_3BChance as <signed>integer)            AS TB_opp_0,
                           cast(hp2.street0_3BDone as <signed>integer)              AS TB_0,
                           cast(hp2.street0_4BChance as <signed>integer)            AS FB_opp_0,
                           cast(hp2.street0_4BDone as <signed>integer)              AS FB_0,
                           cast(hp2.street0_C4BChance as <signed>integer)           AS CFB_opp_0,
                           cast(hp2.street0_C4BDone as <signed>integer)             AS CFB_0,
                           cast(hp2.street0_FoldTo3BChance as <signed>integer)      AS F3B_opp_0,
                           cast(hp2.street0_FoldTo3BDone as <signed>integer)        AS F3B_0,
                           cast(hp2.street0_FoldTo4BChance as <signed>integer)      AS F4B_opp_0,
                           cast(hp2.street0_FoldTo4BDone as <signed>integer)        AS F4B_0,
                           cast(hp2.street0_SqueezeChance as <signed>integer)       AS SQZ_opp_0,
                           cast(hp2.street0_SqueezeDone as <signed>integer)         AS SQZ_0,
                           cast(hp2.raiseToStealChance as <signed>integer)          AS RTS_opp,
                           cast(hp2.raiseToStealDone as <signed>integer)            AS RTS,
                           cast(hp2.success_Steal as <signed>integer)               AS SUC_ST,
                           cast(hp2.street1Seen as <signed>integer)                 AS saw_f,
                           cast(hp2.street1Seen as <signed>integer)                 AS saw_1,
                           cast(hp2.street2Seen as <signed>integer)                 AS saw_2,
                           cast(hp2.street3Seen as <signed>integer)                 AS saw_3,
                           cast(hp2.street4Seen as <signed>integer)                 AS saw_4,
                           cast(hp2.sawShowdown as <signed>integer)                 AS sd,
                           cast(hp2.street1Aggr as <signed>integer)                 AS aggr_1,
                           cast(hp2.street2Aggr as <signed>integer)                 AS aggr_2,
                           cast(hp2.street3Aggr as <signed>integer)                 AS aggr_3,
                           cast(hp2.street4Aggr as <signed>integer)                 AS aggr_4,
                           cast(hp2.otherRaisedStreet1 as <signed>integer)          AS was_raised_1,
                           cast(hp2.otherRaisedStreet2 as <signed>integer)          AS was_raised_2,
                           cast(hp2.otherRaisedStreet3 as <signed>integer)          AS was_raised_3,
                           cast(hp2.otherRaisedStreet4 as <signed>integer)          AS was_raised_4,
                           cast(hp2.foldToOtherRaisedStreet1 as <signed>integer)    AS f_freq_1,
                           cast(hp2.foldToOtherRaisedStreet2 as <signed>integer)    AS f_freq_2,
                           cast(hp2.foldToOtherRaisedStreet3 as <signed>integer)    AS f_freq_3,
                           cast(hp2.foldToOtherRaisedStreet4 as <signed>integer)    AS f_freq_4,
                           cast(hp2.wonWhenSeenStreet1 as <signed>integer)          AS w_w_s_1,
                           cast(hp2.wonAtSD as <signed>integer)                     AS wmsd,
                           cast(hp2.raiseFirstInChance as <signed>integer)          AS steal_opp,
                           cast(hp2.raisedFirstIn as <signed>integer)               AS steal,
                           cast(hp2.foldSbToStealChance as <signed>integer)         AS SBstolen,
                           cast(hp2.foldedSbToSteal as <signed>integer)             AS SBnotDef,
                           cast(hp2.foldBbToStealChance as <signed>integer)         AS BBstolen,
                           cast(hp2.foldedBbToSteal as <signed>integer)             AS BBnotDef,
                           cast(hp2.street1CBChance as <signed>integer)             AS CB_opp_1,
                           cast(hp2.street1CBDone as <signed>integer)               AS CB_1,
                           cast(hp2.street2CBChance as <signed>integer)             AS CB_opp_2,
                           cast(hp2.street2CBDone as <signed>integer)               AS CB_2,
                           cast(hp2.street3CBChance as <signed>integer)             AS CB_opp_3,
                           cast(hp2.street3CBDone as <signed>integer)               AS CB_3,
                           cast(hp2.street4CBChance as <signed>integer)             AS CB_opp_4,
                           cast(hp2.street4CBDone as <signed>integer)               AS CB_4,
                           cast(hp2.foldToStreet1CBChance as <signed>integer)       AS f_cb_opp_1,
                           cast(hp2.foldToStreet1CBDone as <signed>integer)         AS f_cb_1,
                           cast(hp2.foldToStreet2CBChance as <signed>integer)       AS f_cb_opp_2,
                           cast(hp2.foldToStreet2CBDone as <signed>integer)         AS f_cb_2,
                           cast(hp2.foldToStreet3CBChance as <signed>integer)       AS f_cb_opp_3,
                           cast(hp2.foldToStreet3CBDone as <signed>integer)         AS f_cb_3,
                           cast(hp2.foldToStreet4CBChance as <signed>integer)       AS f_cb_opp_4,
                           cast(hp2.foldToStreet4CBDone as <signed>integer)         AS f_cb_4,
                           cast(hp2.totalProfit as <signed>integer)                 AS net,
                           cast(gt.bigblind as <signed>integer)                     AS bigblind,
                           cast(hp2.street1CheckCallRaiseChance as <signed>integer) AS ccr_opp_1,
                           cast(hp2.street1CheckCallRaiseDone as <signed>integer)   AS ccr_1,
                           cast(hp2.street2CheckCallRaiseChance as <signed>integer) AS ccr_opp_2,
                           cast(hp2.street2CheckCallRaiseDone as <signed>integer)   AS ccr_2,
                           cast(hp2.street3CheckCallRaiseChance as <signed>integer) AS ccr_opp_3,
                           cast(hp2.street3CheckCallRaiseDone as <signed>integer)   AS ccr_3,
                           cast(hp2.street4CheckCallRaiseChance as <signed>integer) AS ccr_opp_4,
                           cast(hp2.street4CheckCallRaiseDone as <signed>integer)   AS ccr_4,
                           cast(hp2.street0Calls as <signed>integer)                AS call_0,
                           cast(hp2.street1Calls as <signed>integer)                AS call_1,
                           cast(hp2.street2Calls as <signed>integer)                AS call_2,
                           cast(hp2.street3Calls as <signed>integer)                AS call_3,
                           cast(hp2.street4Calls as <signed>integer)                AS call_4,
                           cast(hp2.street0Bets as <signed>integer)                 AS bet_0,
                           cast(hp2.street1Bets as <signed>integer)                 AS bet_1,
                           cast(hp2.street2Bets as <signed>integer)                 AS bet_2,
                           cast(hp2.street3Bets as <signed>integer)                 AS bet_3,
                           cast(hp2.street4Bets as <signed>integer)                 AS bet_4,
                           cast(hp2.street0Raises as <signed>integer)               AS raise_0,
                           cast(hp2.street1Raises as <signed>integer)               AS raise_1,
                           cast(hp2.street2Raises as <signed>integer)               AS raise_2,
                           cast(hp2.street3Raises as <signed>integer)               AS raise_3,
                           cast(hp2.street4Raises as <signed>integer)               AS raise_4
                         FROM Hands h                                                  /* this hand */
                         INNER JOIN Hands h2         ON (    h2.id >= %s           /* other hands */
                                                         AND h2.tableName = h.tableName)
                         INNER JOIN HandsPlayers hp  ON (h.id = hp.handId)        /* players in this hand */
                         INNER JOIN HandsPlayers hp2 ON (    hp2.playerId+0 = hp.playerId+0
                                                         AND hp2.handId = h2.id)  /* other hands by these players */
                         INNER JOIN Players p        ON (p.id = hp2.PlayerId+0)
                         INNER JOIN Gametypes gt     ON (gt.id = h2.gametypeId)
                    WHERE h.id = %s
                    /* check activeseats once this data returned (don't want to do that here as it might
                       assume a session ended just because the number of seats dipped for a few hands)
                    */
                    AND   (   /* 2 separate parts for hero and opponents */
                              (    hp2.playerId != %s
                               AND h2.seats between %s and %s
                              )
                           OR
                              (    hp2.playerId = %s
                               AND h2.seats between %s and %s
                              )
                          )
                    ORDER BY h.startTime desc, hp2.PlayerId
                    /* order rows by handstart descending so that we can stop reading rows when
                       there's a gap over X minutes between hands (ie. when we get back to start of
                       the session */
                """
     
        self.query['get_players_from_hand'] = """
                SELECT HandsPlayers.playerId, seatNo, name
                FROM  HandsPlayers INNER JOIN Players ON (HandsPlayers.playerId = Players.id)
                WHERE handId = %s
            """
#                    WHERE handId = %s AND Players.id LIKE %s

        self.query['get_winners_from_hand'] = """
                SELECT name, winnings
                FROM HandsPlayers, Players
                WHERE winnings > 0
                    AND Players.id = HandsPlayers.playerId
                    AND handId = %s;
            """

        self.query['get_table_name'] = """
                SELECT h.tableName, h.maxSeats, gt.category, gt.type, s.id, s.name
                     , count(1) as numseats
                FROM Hands h, Gametypes gt, Sites s, HandsPlayers hp
                WHERE h.id = %s
                    AND   gt.id = h.gametypeId
                    AND   s.id = gt.siteID
                    AND   hp.handId = h.id
                GROUP BY h.tableName, h.maxSeats, gt.category, gt.type, s.id, s.name
            """

        self.query['get_actual_seat'] = """
                select seatNo
                from HandsPlayers
                where HandsPlayers.handId = %s
                and   HandsPlayers.playerId  = (select Players.id from Players
                                                where Players.name = %s)
            """

        self.query['get_cards'] = """
                select
                    seatNo     AS seat_number,
                    card1, /*card1Value, card1Suit, */
                    card2, /*card2Value, card2Suit, */
                    card3, /*card3Value, card3Suit, */
                    card4, /*card4Value, card4Suit, */
                    card5, /*card5Value, card5Suit, */
                    card6, /*card6Value, card6Suit, */
                    card7  /*card7Value, card7Suit */
                from HandsPlayers, Players
                where handID = %s and HandsPlayers.playerId = Players.id
                order by seatNo
            """

        self.query['get_common_cards'] = """
                select
                boardcard1,
                boardcard2,
                boardcard3,
                boardcard4,
                boardcard5
                from Hands
                where Id = %s
            """

        if db_server == 'mysql':
            self.query['get_hand_1day_ago'] = """
                select coalesce(max(id),0)
                from Hands
                where startTime < date_sub(utc_timestamp(), interval '1' day)"""
        elif db_server == 'postgresql':
            self.query['get_hand_1day_ago'] = """
                select coalesce(max(id),0)
                from Hands
                where startTime < now() at time zone 'UTC' - interval '1 day'"""
        elif db_server == 'sqlite':
            self.query['get_hand_1day_ago'] = """
                select coalesce(max(id),0)
                from Hands
                where startTime < strftime('%J', 'now') - 1"""

        # not used yet ...
        # gets a date, would need to use handsplayers (not hudcache) to get exact hand Id
        if db_server == 'mysql':
            self.query['get_date_nhands_ago'] = """
                select concat( 'd', date_format(max(h.startTime), '%Y%m%d') )
                from (select hp.playerId
                            ,coalesce(greatest(max(hp.handId)-%s,1),1) as maxminusx
                      from HandsPlayers hp
                      where hp.playerId = %s
                      group by hp.playerId) hp2
                inner join HandsPlayers hp3 on (    hp3.handId <= hp2.maxminusx
                                                and hp3.playerId = hp2.playerId)
                inner join Hands h          on (h.id = hp3.handId)
                """
        elif db_server == 'postgresql':
            self.query['get_date_nhands_ago'] = """
                select 'd' || to_char(max(h3.startTime), 'YYMMDD')
                from (select hp.playerId
                            ,coalesce(greatest(max(hp.handId)-%s,1),1) as maxminusx
                      from HandsPlayers hp
                      where hp.playerId = %s
                      group by hp.playerId) hp2
                inner join HandsPlayers hp3 on (    hp3.handId <= hp2.maxminusx
                                                and hp3.playerId = hp2.playerId)
                inner join Hands h          on (h.id = hp3.handId)
                """
        elif db_server == 'sqlite': # untested guess at query:
            self.query['get_date_nhands_ago'] = """
                select 'd' || strftime(max(h3.startTime), 'YYMMDD')
                from (select hp.playerId
                            ,coalesce(greatest(max(hp.handId)-%s,1),1) as maxminusx
                      from HandsPlayers hp
                      where hp.playerId = %s
                      group by hp.playerId) hp2
                inner join HandsPlayers hp3 on (    hp3.handId <= hp2.maxminusx
                                                and hp3.playerId = hp2.playerId)
                inner join Hands h          on (h.id = hp3.handId)
                """

        # used in Gui*PlayerStats:
        self.query['getPlayerId'] = """SELECT id from Players where name = %s"""

        self.query['getPlayerIdBySite'] = """SELECT id from Players where name = %s AND siteId = %s"""

        # used in *Filters:
        #self.query['getLimits'] = already defined further up
        self.query['getLimits2'] = """SELECT DISTINCT type, limitType, bigBlind 
                                      from Gametypes
                                      ORDER by type, limitType DESC, bigBlind DESC"""
        self.query['getLimits3'] = """select DISTINCT type
                                           , gt.limitType
                                           , case type
                                                 when 'ring' then bigBlind 
-                                                else buyin
-                                            end as bb_or_buyin
                                      from Gametypes gt
                                      cross join TourneyTypes tt
                                      order by type, gt.limitType DESC, bb_or_buyin DESC"""
        self.query['getCashLimits'] = """select DISTINCT type
                                           , limitType
                                           , bigBlind as bb_or_buyin
                                      from Gametypes gt
                                      WHERE type = 'ring'
                                      order by type, limitType DESC, bb_or_buyin DESC"""
        #FIXME: Some stats not added to DetailedStats (miss raise to steal)
        if db_server == 'mysql':
            self.query['playerDetailedStats'] = """
                     select  <hgametypeId>                                                          AS hgametypeid
                            ,<playerName>                                                           AS pname
                            ,gt.base
                            ,gt.category
                            ,upper(gt.limitType)                                                    AS limittype
                            ,s.name
                            ,min(gt.bigBlind)                                                       AS minbigblind
                            ,max(gt.bigBlind)                                                       AS maxbigblind
                            /*,<hcgametypeId>                                                         AS gtid*/
                            ,<position>                                                             AS plposition
                            ,count(1)                                                               AS n
                            ,100.0*sum(cast(hp.street0VPI as <signed>integer))/count(1)             AS vpip
                            ,100.0*sum(cast(hp.street0Aggr as <signed>integer))/count(1)            AS pfr
                            ,case when sum(cast(hp.street0_3Bchance as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street0_3Bdone as <signed>integer))/sum(cast(hp.street0_3Bchance as <signed>integer))
                             end                                                                    AS pf3
                            ,case when sum(cast(hp.street0_4Bchance as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street0_4Bdone as <signed>integer))/sum(cast(hp.street0_4Bchance as <signed>integer))
                             end                                                                    AS pf4
                            ,case when sum(cast(hp.street0_FoldTo3Bchance as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street0_FoldTo3Bdone as <signed>integer))/sum(cast(hp.street0_FoldTo3Bchance as <signed>integer))
                             end                                                                    AS pff3
                            ,case when sum(cast(hp.street0_FoldTo4Bchance as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street0_FoldTo4Bdone as <signed>integer))/sum(cast(hp.street0_FoldTo4Bchance as <signed>integer))
                             end                                                                    AS pff4

                            ,case when sum(cast(hp.raiseFirstInChance as <signed>integer)) = 0 then -999
                                  else 100.0 * sum(cast(hp.raisedFirstIn as <signed>integer)) / 
                                       sum(cast(hp.raiseFirstInChance as <signed>integer))
                             end                                                                    AS rfi
                            ,case when sum(case hp.position
                                           when 'S' then cast(hp.raiseFirstInChance as <signed>integer)
                                           when '0' then cast(hp.raiseFirstInChance as <signed>integer)
                                           when '1' then cast(hp.raiseFirstInChance as <signed>integer)
                                           else 0
                                           end
                                          ) = 0 then -999
                                  else 100.0 * 
                                       sum(case hp.position
                                           when 'S' then cast(hp.raisedFirstIn as <signed>integer)
                                           when '0' then cast(hp.raisedFirstIn as <signed>integer)
                                           when '1' then cast(hp.raisedFirstIn as <signed>integer)
                                           else 0
                                           end
                                          ) / 
                                       sum(case hp.position
                                           when 'S' then cast(hp.raiseFirstInChance as <signed>integer)
                                           when '0' then cast(hp.raiseFirstInChance as <signed>integer)
                                           when '1' then cast(hp.raiseFirstInChance as <signed>integer)
                                           else 0
                                           end
                                          )
                             end                                                                    AS steals
                            ,case when sum(cast(hp.success_Steal as <signed>integer)) = 0 then -999
                                  else 100.0 * 
                                       sum(cast(hp.success_Steal as <signed>integer))
                                           / 
                                       sum(case hp.position
                                           when 'S' then cast(hp.raisedFirstIn as <signed>integer)
                                           when '0' then cast(hp.raisedFirstIn as <signed>integer)
                                           when '1' then cast(hp.raisedFirstIn as <signed>integer)
                                           else 0
                                           end
                                          )
                             end                                                                    AS suc_steal
                            ,100.0*sum(cast(hp.street1Seen as <signed>integer))/count(1)            AS saw_f
                            ,100.0*sum(cast(hp.sawShowdown as <signed>integer))/count(1)            AS sawsd
                            ,case when sum(cast(hp.street1Seen as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.sawShowdown as <signed>integer))/sum(cast(hp.street1Seen as <signed>integer))
                             end                                                                    AS wtsdwsf
                            ,case when sum(cast(hp.sawShowdown as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.wonAtSD as <signed>integer))/sum(cast(hp.sawShowdown as <signed>integer))
                             end                                                                    AS wmsd
                            ,case when sum(cast(hp.street1Seen as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street1Aggr as <signed>integer))/sum(cast(hp.street1Seen as <signed>integer))
                             end                                                                    AS flafq
                            ,case when sum(cast(hp.street2Seen as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street2Aggr as <signed>integer))/sum(cast(hp.street2Seen as <signed>integer))
                             end                                                                    AS tuafq
                            ,case when sum(cast(hp.street3Seen as <signed>integer)) = 0 then -999
                                 else 100.0*sum(cast(hp.street3Aggr as <signed>integer))/sum(cast(hp.street3Seen as <signed>integer))
                             end                                                                    AS rvafq
                            ,case when sum(cast(hp.street1Seen as <signed>integer))+sum(cast(hp.street2Seen as <signed>integer))+sum(cast(hp.street3Seen as <signed>integer)) = 0 then -999
                                 else 100.0*(sum(cast(hp.street1Aggr as <signed>integer))+sum(cast(hp.street2Aggr as <signed>integer))+sum(cast(hp.street3Aggr as <signed>integer)))
                                          /(sum(cast(hp.street1Seen as <signed>integer))+sum(cast(hp.street2Seen as <signed>integer))+sum(cast(hp.street3Seen as <signed>integer)))
                             end                                                                    AS pofafq
                            ,case when sum(cast(hp.street1Calls as <signed>integer))+ sum(cast(hp.street2Calls as <signed>integer))+ sum(cast(hp.street3Calls as <signed>integer))+ sum(cast(hp.street4Calls as <signed>integer)) = 0 then -999
                                 else (sum(cast(hp.street1Aggr as <signed>integer)) + sum(cast(hp.street2Aggr as <signed>integer)) + sum(cast(hp.street3Aggr as <signed>integer)) + sum(cast(hp.street4Aggr as <signed>integer)))
                                     /(0.0+sum(cast(hp.street1Calls as <signed>integer))+ sum(cast(hp.street2Calls as <signed>integer))+ sum(cast(hp.street3Calls as <signed>integer))+ sum(cast(hp.street4Calls as <signed>integer)))
                             end                                                                    AS aggfac
                            ,100.0*(sum(cast(hp.street1Aggr as <signed>integer)) + sum(cast(hp.street2Aggr as <signed>integer)) + sum(cast(hp.street3Aggr as <signed>integer)) + sum(cast(hp.street4Aggr as <signed>integer))) 
                                       / ((sum(cast(hp.foldToOtherRaisedStreet1 as <signed>integer))+ sum(cast(hp.foldToOtherRaisedStreet2 as <signed>integer))+ sum(cast(hp.foldToOtherRaisedStreet3 as <signed>integer))+ sum(cast(hp.foldToOtherRaisedStreet4 as <signed>integer))) +
                                       (sum(cast(hp.street1Calls as <signed>integer))+ sum(cast(hp.street2Calls as <signed>integer))+ sum(cast(hp.street3Calls as <signed>integer))+ sum(cast(hp.street4Calls as <signed>integer))) +
                                       (sum(cast(hp.street1Aggr as <signed>integer)) + sum(cast(hp.street2Aggr as <signed>integer)) + sum(cast(hp.street3Aggr as <signed>integer)) + sum(cast(hp.street4Aggr as <signed>integer))) )
                                                                                                    AS aggfrq
                            ,100.0*(sum(cast(hp.street1CBDone as <signed>integer)) + sum(cast(hp.street2CBDone as <signed>integer)) + sum(cast(hp.street3CBDone as <signed>integer)) + sum(cast(hp.street4CBDone as <signed>integer))) 
                                       / (sum(cast(hp.street1CBChance as <signed>integer))+ sum(cast(hp.street2CBChance as <signed>integer))+ sum(cast(hp.street3CBChance as <signed>integer))+ sum(cast(hp.street4CBChance as <signed>integer))) 
                                                                                                    AS conbet
                            ,sum(hp.totalProfit)/100.0                                              AS net
                            ,sum(hp.rake)/100.0                                                     AS rake
                            ,100.0*avg(hp.totalProfit/(gt.bigBlind+0.0))                            AS bbper100
                            ,avg(hp.totalProfit)/100.0                                              AS profitperhand
                            ,100.0*avg((hp.totalProfit+hp.rake)/(gt.bigBlind+0.0))                  AS bb100xr
                            ,avg((hp.totalProfit+hp.rake)/100.0)                                    AS profhndxr
                            ,avg(h.seats+0.0)                                                       AS avgseats
                            ,variance(hp.totalProfit/100.0)                                         AS variance
                      from HandsPlayers hp
                           inner join Hands h       on  (h.id = hp.handId)
                           inner join Gametypes gt  on  (gt.Id = h.gametypeId)
                           inner join Sites s       on  (s.Id = gt.siteId)
                           inner join Players p     on  (p.Id = hp.playerId)
                      where hp.playerId in <player_test>
                      <game_test>
                      <site_test>
                      /*and   hp.tourneysPlayersId IS NULL*/
                      and   h.seats <seats_test>
                      <flagtest>
                      <gtbigBlind_test>
                      and   date_format(h.startTime, '%Y-%m-%d %T') <datestest>
                      group by hgametypeId
                              ,pname
                              ,gt.base
                              ,gt.category
                              <groupbyseats>
                              ,plposition
                              ,upper(gt.limitType)
                              ,s.name
                      having 1 = 1 <havingclause>
                      order by pname
                              ,gt.base
                              ,gt.category
                              <orderbyseats>
                              ,case <position> when 'B' then 'B'
                                               when 'S' then 'S'
                                               else concat('Z', <position>)
                               end
                              <orderbyhgametypeId>
                              ,upper(gt.limitType) desc
                              ,maxbigblind desc
                              ,s.name
                      """
        elif db_server == 'postgresql':
            self.query['playerDetailedStats'] = """
                     select  <hgametypeId>                                                          AS hgametypeid
                            ,<playerName>                                                           AS pname
                            ,gt.base
                            ,gt.category
                            ,upper(gt.limitType)                                                    AS limittype
                            ,s.name
                            ,min(gt.bigBlind)                                                       AS minbigblind
                            ,max(gt.bigBlind)                                                       AS maxbigblind
                            /*,<hcgametypeId>                                                       AS gtid*/
                            ,<position>                                                             AS plposition
                            ,count(1)                                                               AS n
                            ,100.0*sum(cast(hp.street0VPI as <signed>integer))/count(1)             AS vpip
                            ,100.0*sum(cast(hp.street0Aggr as <signed>integer))/count(1)            AS pfr
                            ,case when sum(cast(hp.street0_3Bchance as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street0_3Bdone as <signed>integer))/sum(cast(hp.street0_3Bchance as <signed>integer))
                             end                                                                    AS pf3
                            ,case when sum(cast(hp.street0_4Bchance as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street0_4Bdone as <signed>integer))/sum(cast(hp.street0_4Bchance as <signed>integer))
                             end                                                                    AS pf4
                            ,case when sum(cast(hp.street0_FoldTo3Bchance as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street0_FoldTo3Bdone as <signed>integer))/sum(cast(hp.street0_FoldTo3Bchance as <signed>integer))
                             end                                                                    AS pff3
                            ,case when sum(cast(hp.street0_FoldTo4Bchance as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street0_FoldTo4Bdone as <signed>integer))/sum(cast(hp.street0_FoldTo4Bchance as <signed>integer))
                             end                                                                    AS pff4
                            ,case when sum(cast(hp.raiseFirstInChance as <signed>integer)) = 0 then -999
                                  else 100.0 * sum(cast(hp.raisedFirstIn as <signed>integer)) / 
                                       sum(cast(hp.raiseFirstInChance as <signed>integer))
                             end                                                                    AS rfi
                            ,case when sum(case hp.position
                                           when 'S' then cast(hp.raiseFirstInChance as <signed>integer)
                                           when '0' then cast(hp.raiseFirstInChance as <signed>integer)
                                           when '1' then cast(hp.raiseFirstInChance as <signed>integer)
                                           else 0
                                           end
                                          ) = 0 then -999
                                  else 100.0 * 
                                       sum(case hp.position
                                           when 'S' then cast(hp.raisedFirstIn as <signed>integer)
                                           when '0' then cast(hp.raisedFirstIn as <signed>integer)
                                           when '1' then cast(hp.raisedFirstIn as <signed>integer)
                                           else 0
                                           end
                                          ) / 
                                       sum(case hp.position
                                           when 'S' then cast(hp.raiseFirstInChance as <signed>integer)
                                           when '0' then cast(hp.raiseFirstInChance as <signed>integer)
                                           when '1' then cast(hp.raiseFirstInChance as <signed>integer)
                                           else 0
                                           end
                                          )
                             end                                                                    AS steals
                            ,case when sum(cast(hp.success_Steal as <signed>integer)) = 0 then -999
                                  else 100.0 * 
                                       sum(cast(hp.success_Steal as <signed>integer))
                                           / 
                                       sum(case hp.position
                                           when 'S' then cast(hp.raisedFirstIn as <signed>integer)
                                           when '0' then cast(hp.raisedFirstIn as <signed>integer)
                                           when '1' then cast(hp.raisedFirstIn as <signed>integer)
                                           else 0
                                           end
                                          )
                             end                                                                    AS suc_steal
                            ,100.0*sum(cast(hp.street1Seen as <signed>integer))/count(1)            AS saw_f
                            ,100.0*sum(cast(hp.sawShowdown as <signed>integer))/count(1)            AS sawsd
                            ,case when sum(cast(hp.street1Seen as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.sawShowdown as <signed>integer))/sum(cast(hp.street1Seen as <signed>integer))
                             end                                                                    AS wtsdwsf
                            ,case when sum(cast(hp.sawShowdown as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.wonAtSD as <signed>integer))/sum(cast(hp.sawShowdown as <signed>integer))
                             end                                                                    AS wmsd
                            ,case when sum(cast(hp.street1Seen as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street1Aggr as <signed>integer))/sum(cast(hp.street1Seen as <signed>integer))
                             end                                                                    AS flafq
                            ,case when sum(cast(hp.street2Seen as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street2Aggr as <signed>integer))/sum(cast(hp.street2Seen as <signed>integer))
                             end                                                                    AS tuafq
                            ,case when sum(cast(hp.street3Seen as <signed>integer)) = 0 then -999
                                 else 100.0*sum(cast(hp.street3Aggr as <signed>integer))/sum(cast(hp.street3Seen as <signed>integer))
                             end                                                                    AS rvafq
                            ,case when sum(cast(hp.street1Seen as <signed>integer))+sum(cast(hp.street2Seen as <signed>integer))+sum(cast(hp.street3Seen as <signed>integer)) = 0 then -999
                                 else 100.0*(sum(cast(hp.street1Aggr as <signed>integer))+sum(cast(hp.street2Aggr as <signed>integer))+sum(cast(hp.street3Aggr as <signed>integer)))
                                          /(sum(cast(hp.street1Seen as <signed>integer))+sum(cast(hp.street2Seen as <signed>integer))+sum(cast(hp.street3Seen as <signed>integer)))
                             end                                                                    AS pofafq
                            ,case when sum(cast(hp.street1Calls as <signed>integer))+ sum(cast(hp.street2Calls as <signed>integer))+ sum(cast(hp.street3Calls as <signed>integer))+ sum(cast(hp.street4Calls as <signed>integer)) = 0 then -999
                                 else (sum(cast(hp.street1Aggr as <signed>integer)) + sum(cast(hp.street2Aggr as <signed>integer)) + sum(cast(hp.street3Aggr as <signed>integer)) + sum(cast(hp.street4Aggr as <signed>integer)))
                                     /(0.0+sum(cast(hp.street1Calls as <signed>integer))+ sum(cast(hp.street2Calls as <signed>integer))+ sum(cast(hp.street3Calls as <signed>integer))+ sum(cast(hp.street4Calls as <signed>integer)))
                             end                                                                    AS aggfac
                            ,100.0*(sum(cast(hp.street1Aggr as <signed>integer)) + sum(cast(hp.street2Aggr as <signed>integer)) + sum(cast(hp.street3Aggr as <signed>integer)) + sum(cast(hp.street4Aggr as <signed>integer))) 
                                       / ((sum(cast(hp.foldToOtherRaisedStreet1 as <signed>integer))+ sum(cast(hp.foldToOtherRaisedStreet2 as <signed>integer))+ sum(cast(hp.foldToOtherRaisedStreet3 as <signed>integer))+ sum(cast(hp.foldToOtherRaisedStreet4 as <signed>integer))) +
                                       (sum(cast(hp.street1Calls as <signed>integer))+ sum(cast(hp.street2Calls as <signed>integer))+ sum(cast(hp.street3Calls as <signed>integer))+ sum(cast(hp.street4Calls as <signed>integer))) +
                                       (sum(cast(hp.street1Aggr as <signed>integer)) + sum(cast(hp.street2Aggr as <signed>integer)) + sum(cast(hp.street3Aggr as <signed>integer)) + sum(cast(hp.street4Aggr as <signed>integer))) )
                                                                                                    AS aggfrq
                            ,100.0*(sum(cast(hp.street1CBDone as <signed>integer)) + sum(cast(hp.street2CBDone as <signed>integer)) + sum(cast(hp.street3CBDone as <signed>integer)) + sum(cast(hp.street4CBDone as <signed>integer))) 
                                       / (sum(cast(hp.street1CBChance as <signed>integer))+ sum(cast(hp.street2CBChance as <signed>integer))+ sum(cast(hp.street3CBChance as <signed>integer))+ sum(cast(hp.street4CBChance as <signed>integer))) 
                                                                                                    AS conbet
                            ,sum(hp.totalProfit)/100.0                                              AS net
                            ,sum(hp.rake)/100.0                                                     AS rake
                            ,100.0*avg(hp.totalProfit/(gt.bigBlind+0.0))                            AS bbper100
                            ,avg(hp.totalProfit)/100.0                                              AS profitperhand
                            ,100.0*avg((hp.totalProfit+hp.rake)/(gt.bigBlind+0.0))                  AS bb100xr
                            ,avg((hp.totalProfit+hp.rake)/100.0)                                    AS profhndxr
                            ,avg(h.seats+0.0)                                                       AS avgseats
                            ,variance(hp.totalProfit/100.0)                                         AS variance
                      from HandsPlayers hp
                           inner join Hands h       on  (h.id = hp.handId)
                           inner join Gametypes gt  on  (gt.Id = h.gametypeId)
                           inner join Sites s       on  (s.Id = gt.siteId)
                           inner join Players p     on  (p.Id = hp.playerId)
                      where hp.playerId in <player_test>
                      <game_test>
                      <site_test>
                      /*and   hp.tourneysPlayersId IS NULL*/
                      and   h.seats <seats_test>
                      <flagtest>
                      <gtbigBlind_test>
                      and   to_char(h.startTime, 'YYYY-MM-DD HH24:MI:SS') <datestest>
                      group by hgametypeId
                              ,pname
                              ,gt.base
                              ,gt.category
                              <groupbyseats>
                              ,plposition
                              ,upper(gt.limitType)
                              ,s.name
                      having 1 = 1 <havingclause>
                      order by pname
                              ,gt.base
                              ,gt.category
                              <orderbyseats>
                              ,case <position> when 'B' then 'B'
                                               when 'S' then 'S'
                                               when '0' then 'Y'
                                               else 'Z'||<position>
                               end
                              <orderbyhgametypeId>
                              ,upper(gt.limitType) desc
                              ,maxbigblind desc
                              ,s.name
                      """
        elif db_server == 'sqlite':
            self.query['playerDetailedStats'] = """
                     select  <hgametypeId>                                                          AS hgametypeid
                            ,<playerName>                                                           AS pname
                            ,gt.base
                            ,gt.category                                                            AS category
                            ,upper(gt.limitType)                                                    AS limittype
                            ,s.name                                                                 AS name
                            ,min(gt.bigBlind)                                                       AS minbigblind
                            ,max(gt.bigBlind)                                                       AS maxbigblind
                            /*,<hcgametypeId>                                                       AS gtid*/
                            ,<position>                                                             AS plposition
                            ,count(1)                                                               AS n
                            ,100.0*sum(cast(hp.street0VPI as <signed>integer))/count(1)             AS vpip
                            ,100.0*sum(cast(hp.street0Aggr as <signed>integer))/count(1)            AS pfr
                            ,case when sum(cast(hp.street0_3Bchance as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street0_3Bdone as <signed>integer))/sum(cast(hp.street0_3Bchance as <signed>integer))
                             end                                                                    AS pf3
                            ,case when sum(cast(hp.street0_4Bchance as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street0_4Bdone as <signed>integer))/sum(cast(hp.street0_4Bchance as <signed>integer))
                             end                                                                    AS pf4
                            ,case when sum(cast(hp.street0_FoldTo3Bchance as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street0_FoldTo3Bdone as <signed>integer))/sum(cast(hp.street0_FoldTo3Bchance as <signed>integer))
                             end                                                                    AS pff3
                            ,case when sum(cast(hp.street0_FoldTo4Bchance as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street0_FoldTo4Bdone as <signed>integer))/sum(cast(hp.street0_FoldTo4Bchance as <signed>integer))
                             end                                                                    AS pff4
                            ,case when sum(cast(hp.raiseFirstInChance as <signed>integer)) = 0 then -999
                                  else 100.0 * sum(cast(hp.raisedFirstIn as <signed>integer)) / 
                                       sum(cast(hp.raiseFirstInChance as <signed>integer))
                             end                                                                    AS rfi
                            ,case when sum(case hp.position
                                           when 'S' then cast(hp.raiseFirstInChance as <signed>integer)
                                           when '0' then cast(hp.raiseFirstInChance as <signed>integer)
                                           when '1' then cast(hp.raiseFirstInChance as <signed>integer)
                                           else 0
                                           end
                                          ) = 0 then -999
                                  else 100.0 * 
                                       sum(case hp.position
                                           when 'S' then cast(hp.raisedFirstIn as <signed>integer)
                                           when '0' then cast(hp.raisedFirstIn as <signed>integer)
                                           when '1' then cast(hp.raisedFirstIn as <signed>integer)
                                           else 0
                                           end
                                          ) / 
                                       sum(case hp.position
                                           when 'S' then cast(hp.raiseFirstInChance as <signed>integer)
                                           when '0' then cast(hp.raiseFirstInChance as <signed>integer)
                                           when '1' then cast(hp.raiseFirstInChance as <signed>integer)
                                           else 0
                                           end
                                          )
                             end                                                                    AS steals
                            ,case when sum(cast(hp.success_Steal as <signed>integer)) = 0 then -999
                                  else 100.0 * 
                                       sum(cast(hp.success_Steal as <signed>integer))
                                           / 
                                       sum(case hp.position
                                           when 'S' then cast(hp.raisedFirstIn as <signed>integer)
                                           when '0' then cast(hp.raisedFirstIn as <signed>integer)
                                           when '1' then cast(hp.raisedFirstIn as <signed>integer)
                                           else 0
                                           end
                                          )
                             end                                                                    AS suc_steal
                            ,100.0*sum(cast(hp.street1Seen as <signed>integer))/count(1)            AS saw_f
                            ,100.0*sum(cast(hp.sawShowdown as <signed>integer))/count(1)            AS sawsd
                            ,case when sum(cast(hp.street1Seen as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.sawShowdown as <signed>integer))/sum(cast(hp.street1Seen as <signed>integer))
                             end                                                                    AS wtsdwsf
                            ,case when sum(cast(hp.sawShowdown as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.wonAtSD as <signed>integer))/sum(cast(hp.sawShowdown as <signed>integer))
                             end                                                                    AS wmsd
                            ,case when sum(cast(hp.street1Seen as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street1Aggr as <signed>integer))/sum(cast(hp.street1Seen as <signed>integer))
                             end                                                                    AS flafq
                            ,case when sum(cast(hp.street2Seen as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street2Aggr as <signed>integer))/sum(cast(hp.street2Seen as <signed>integer))
                             end                                                                    AS tuafq
                            ,case when sum(cast(hp.street3Seen as <signed>integer)) = 0 then -999
                                 else 100.0*sum(cast(hp.street3Aggr as <signed>integer))/sum(cast(hp.street3Seen as <signed>integer))
                             end                                                                    AS rvafq
                            ,case when sum(cast(hp.street1Seen as <signed>integer))+sum(cast(hp.street2Seen as <signed>integer))+sum(cast(hp.street3Seen as <signed>integer)) = 0 then -999
                                 else 100.0*(sum(cast(hp.street1Aggr as <signed>integer))+sum(cast(hp.street2Aggr as <signed>integer))+sum(cast(hp.street3Aggr as <signed>integer)))
                                          /(sum(cast(hp.street1Seen as <signed>integer))+sum(cast(hp.street2Seen as <signed>integer))+sum(cast(hp.street3Seen as <signed>integer)))
                             end                                                                    AS pofafq
                            ,case when sum(cast(hp.street1Calls as <signed>integer))+ sum(cast(hp.street2Calls as <signed>integer))+ sum(cast(hp.street3Calls as <signed>integer))+ sum(cast(hp.street4Calls as <signed>integer)) = 0 then -999
                                 else (sum(cast(hp.street1Aggr as <signed>integer)) + sum(cast(hp.street2Aggr as <signed>integer)) + sum(cast(hp.street3Aggr as <signed>integer)) + sum(cast(hp.street4Aggr as <signed>integer)))
                                     /(0.0+sum(cast(hp.street1Calls as <signed>integer))+ sum(cast(hp.street2Calls as <signed>integer))+ sum(cast(hp.street3Calls as <signed>integer))+ sum(cast(hp.street4Calls as <signed>integer)))
                             end                                                                    AS aggfac
                            ,100.0*(sum(cast(hp.street1Aggr as <signed>integer)) + sum(cast(hp.street2Aggr as <signed>integer)) + sum(cast(hp.street3Aggr as <signed>integer)) + sum(cast(hp.street4Aggr as <signed>integer))) 
                                       / ((sum(cast(hp.foldToOtherRaisedStreet1 as <signed>integer))+ sum(cast(hp.foldToOtherRaisedStreet2 as <signed>integer))+ sum(cast(hp.foldToOtherRaisedStreet3 as <signed>integer))+ sum(cast(hp.foldToOtherRaisedStreet4 as <signed>integer))) +
                                       (sum(cast(hp.street1Calls as <signed>integer))+ sum(cast(hp.street2Calls as <signed>integer))+ sum(cast(hp.street3Calls as <signed>integer))+ sum(cast(hp.street4Calls as <signed>integer))) +
                                       (sum(cast(hp.street1Aggr as <signed>integer)) + sum(cast(hp.street2Aggr as <signed>integer)) + sum(cast(hp.street3Aggr as <signed>integer)) + sum(cast(hp.street4Aggr as <signed>integer))) )
                                                                                                    AS aggfrq
                            ,100.0*(sum(cast(hp.street1CBDone as <signed>integer)) + sum(cast(hp.street2CBDone as <signed>integer)) + sum(cast(hp.street3CBDone as <signed>integer)) + sum(cast(hp.street4CBDone as <signed>integer))) 
                                       / (sum(cast(hp.street1CBChance as <signed>integer))+ sum(cast(hp.street2CBChance as <signed>integer))+ sum(cast(hp.street3CBChance as <signed>integer))+ sum(cast(hp.street4CBChance as <signed>integer))) 
                                                                                                    AS conbet
                            ,sum(hp.totalProfit)/100.0                                              AS net
                            ,sum(hp.rake)/100.0                                                     AS rake
                            ,100.0*avg(hp.totalProfit/(gt.bigBlind+0.0))                            AS bbper100
                            ,avg(hp.totalProfit)/100.0                                              AS profitperhand
                            ,100.0*avg((hp.totalProfit+hp.rake)/(gt.bigBlind+0.0))                  AS bb100xr
                            ,avg((hp.totalProfit+hp.rake)/100.0)                                    AS profhndxr
                            ,avg(h.seats+0.0)                                                       AS avgseats
                            ,variance(hp.totalProfit/100.0)                                         AS variance
                      from HandsPlayers hp
                           inner join Hands h       on  (h.id = hp.handId)
                           inner join Gametypes gt  on  (gt.Id = h.gametypeId)
                           inner join Sites s       on  (s.Id = gt.siteId)
                           inner join Players p     on  (p.Id = hp.playerId)
                      where hp.playerId in <player_test>
                      <game_test>
                      <site_test>
                      /*and   hp.tourneysPlayersId IS NULL*/
                      and   h.seats <seats_test>
                      <flagtest>
                      <gtbigBlind_test>
                      and   datetime(h.startTime) <datestest>
                      group by hgametypeId
                              ,hp.playerId
                              ,gt.base
                              ,gt.category
                              <groupbyseats>
                              ,plposition
                              ,upper(gt.limitType)
                              ,s.name
                      having 1 = 1 <havingclause>
                      order by hp.playerId
                              ,gt.base
                              ,gt.category
                              <orderbyseats>
                              ,case <position> when 'B' then 'B'
                                               when 'S' then 'S'
                                               when '0' then 'Y'
                                               else 'Z'||<position>
                               end
                              <orderbyhgametypeId>
                              ,upper(gt.limitType) desc
                              ,max(gt.bigBlind) desc
                              ,s.name
                      """

        #FIXME: 3/4bet and foldTo don't added four tournaments yet
        if db_server == 'mysql':
            self.query['tourneyPlayerDetailedStats'] = """
                      select s.name                                                                 AS siteName
                            ,t.tourneyTypeId                                                        AS tourneyTypeId
                            ,tt.currency                                                            AS currency
                            ,(CASE
                                WHEN tt.currency = 'USD' THEN tt.buyIn/100.0
                                WHEN tt.currency = 'EUR' THEN tt.buyIn/100.0
                                ELSE tt.buyIn
                              END)                                                                  AS buyIn
                            ,tt.fee/100.0                                                           AS fee
                            ,tt.category                                                            AS category
                            ,tt.limitType                                                           AS limitType
                            ,p.name                                                                 AS playerName
                            ,COUNT(1)                                                               AS tourneyCount
                            ,SUM(CASE WHEN tp.rank > 0 THEN 0 ELSE 1 END)                           AS unknownRank
                            ,SUM(CASE WHEN winnings > 0 THEN 1 ELSE 0 END)/(COUNT(1) - SUM(CASE WHEN tp.rank > 0 THEN 0 ELSE 1 END)) AS itm
                            ,SUM(CASE WHEN rank = 1 THEN 1 ELSE 0 END)                              AS _1st
                            ,SUM(CASE WHEN rank = 2 THEN 1 ELSE 0 END)                              AS _2nd
                            ,SUM(CASE WHEN rank = 3 THEN 1 ELSE 0 END)                              AS _3rd
                            ,SUM(tp.winnings)/100.0                                                 AS won
                            ,SUM(CASE WHEN tt.currency = 'USD' THEN (tt.buyIn+tt.fee)/100.0 ELSE tt.buyIn END) AS spent
                            ,SUM(tp.winnings)/SUM(tt.buyin+tt.fee)*100.0-100                        AS roi
                            ,SUM(tp.winnings-(tt.buyin+tt.fee))/100.0/(COUNT(1)-SUM(CASE WHEN tp.rank > 0 THEN 0 ELSE 1 END)) AS profitPerTourney
                      from TourneysPlayers tp
                           inner join Tourneys t        on  (t.id = tp.tourneyId)
                           inner join TourneyTypes tt   on  (tt.Id = t.tourneyTypeId)
                           inner join Sites s           on  (s.Id = tt.siteId)
                           inner join Players p         on  (p.Id = tp.playerId)
                      where tp.playerId in <nametest> <sitetest>
                      and   date_format(t.startTime, '%Y-%m-%d %T') <datestest>
                      group by tourneyTypeId, playerName
                      order by tourneyTypeId
                              ,playerName
                              ,siteName"""
        elif db_server == 'postgresql':
            # sc: itm and profitPerTourney changed to "ELSE 0" to avoid divide by zero error as temp fix
            # proper fix should use coalesce() or case ... when ... to work in all circumstances
            self.query['tourneyPlayerDetailedStats'] = """
                      select s.name                                                                 AS siteName
                            ,t.tourneyTypeId                                                        AS tourneyTypeId
                            ,tt.currency                                                            AS currency
                            ,(CASE
                                WHEN tt.currency = 'USD' THEN tt.buyIn/100.0
                                WHEN tt.currency = 'EUR' THEN tt.buyIn/100.0
                                ELSE tt.buyIn
                              END)                                                                  AS buyIn
                            ,tt.fee/100.0                                                           AS fee
                            ,tt.category                                                            AS category
                            ,tt.limitType                                                           AS limitType
                            ,p.name                                                                 AS playerName
                            ,COUNT(1)                                                               AS tourneyCount
                            ,SUM(CASE WHEN tp.rank > 0 THEN 0 ELSE 1 END)                           AS unknownRank
                            ,SUM(CASE WHEN winnings > 0 THEN 1 ELSE 0 END)
                             /(COUNT(1) - SUM(CASE WHEN tp.rank > 0 THEN 0 ELSE 0 END))             AS itm
                            ,SUM(CASE WHEN rank = 1 THEN 1 ELSE 0 END)                              AS _1st
                            ,SUM(CASE WHEN rank = 2 THEN 1 ELSE 0 END)                              AS _2nd
                            ,SUM(CASE WHEN rank = 3 THEN 1 ELSE 0 END)                              AS _3rd
                            ,SUM(tp.winnings)/100.0                                                 AS won
                            ,SUM(CASE WHEN tt.currency = 'USD' THEN (tt.buyIn+tt.fee)/100.0 ELSE tt.buyIn END) AS spent
                            ,SUM(tp.winnings)/SUM(tt.buyin+tt.fee)*100.0-100                        AS roi
                            ,SUM(tp.winnings-(tt.buyin+tt.fee))/100.0
                             /(COUNT(1)-SUM(CASE WHEN tp.rank > 0 THEN 0 ELSE 0 END))               AS profitPerTourney
                      from TourneysPlayers tp
                           inner join Tourneys t        on  (t.id = tp.tourneyId)
                           inner join TourneyTypes tt   on  (tt.Id = t.tourneyTypeId)
                           inner join Sites s           on  (s.Id = tt.siteId)
                           inner join Players p         on  (p.Id = tp.playerId)
                      where tp.playerId in <nametest> <sitetest>
                      and   to_char(t.startTime, 'YYYY-MM-DD HH24:MI:SS') <datestest>
                      group by tourneyTypeId, s.name, playerName, tt.currency, tt.buyin, tt.fee
                             , tt.category, tt.limitType
                      order by tourneyTypeId
                              ,playerName
                              ,siteName"""
        elif db_server == 'sqlite':
            self.query['tourneyPlayerDetailedStats'] = """
                      select s.name                                                                 AS siteName
                            ,t.tourneyTypeId                                                        AS tourneyTypeId
                            ,tt.currency                                                            AS currency
                            ,(CASE
                                WHEN tt.currency = 'USD' THEN tt.buyIn/100.0
                                WHEN tt.currency = 'EUR' THEN tt.buyIn/100.0
                                ELSE tt.buyIn
                              END)                                                                  AS buyIn
                            ,tt.fee/100.0                                                           AS fee
                            ,tt.category                                                            AS category
                            ,tt.limitType                                                           AS limitType
                            ,p.name                                                                 AS playerName
                            ,COUNT(1)                                                               AS tourneyCount
                            ,SUM(CASE WHEN tp.rank > 0 THEN 0 ELSE 1 END)                           AS unknownRank
                            ,SUM(CASE WHEN winnings > 0 THEN 1 ELSE 0 END)/(COUNT(1) - SUM(CASE WHEN tp.rank > 0 THEN 0 ELSE 1 END)) AS itm
                            ,SUM(CASE WHEN rank = 1 THEN 1 ELSE 0 END)                              AS _1st
                            ,SUM(CASE WHEN rank = 2 THEN 1 ELSE 0 END)                              AS _2nd
                            ,SUM(CASE WHEN rank = 3 THEN 1 ELSE 0 END)                              AS _3rd
                            ,SUM(tp.winnings)/100.0                                                 AS won
                            ,SUM(CASE WHEN tt.currency = 'USD' THEN (tt.buyIn+tt.fee)/100.0 ELSE tt.buyIn END) AS spent
                            ,SUM(tp.winnings)/SUM(tt.buyin+tt.fee)*100.0-100                        AS roi
                            ,SUM(tp.winnings-(tt.buyin+tt.fee))/100.0/(COUNT(1)-SUM(CASE WHEN tp.rank > 0 THEN 0 ELSE 1 END)) AS profitPerTourney
                      from TourneysPlayers tp
                           inner join Tourneys t        on  (t.id = tp.tourneyId)
                           inner join TourneyTypes tt   on  (tt.Id = t.tourneyTypeId)
                           inner join Sites s           on  (s.Id = tt.siteId)
                           inner join Players p         on  (p.Id = tp.playerId)
                      where tp.playerId in <nametest> <sitetest>
                      and   datetime(t.startTime) <datestest>
                      group by tourneyTypeId, playerName
                      order by tourneyTypeId
                              ,playerName
                              ,siteName"""

        if db_server == 'mysql':
            self.query['playerStats'] = """
                SELECT
                      concat(upper(stats.limitType), ' '
                            ,concat(upper(substring(stats.category,1,1)),substring(stats.category,2) ), ' '
                            ,stats.name, ' '
                            ,cast(stats.bigBlindDesc as char)
                            )                                                      AS Game
                     ,stats.n
                     ,stats.vpip
                     ,stats.pfr
                     ,stats.pf3
                     ,stats.pf4
                     ,stats.pff3
                     ,stats.pff4
                     ,stats.steals
                     ,stats.saw_f
                     ,stats.sawsd
                     ,stats.wtsdwsf
                     ,stats.wmsd
                     ,stats.FlAFq
                     ,stats.TuAFq
                     ,stats.RvAFq
                     ,stats.PoFAFq
                     ,stats.Net
                     ,stats.BBper100
                     ,stats.Profitperhand
                     ,case when hprof2.variance = -999 then '-'
                           else format(hprof2.variance, 2)
                      end                                                          AS Variance
                     ,stats.AvgSeats
                FROM
                    (select /* stats from hudcache */
                            gt.base
                           ,gt.category
                           ,upper(gt.limitType) as limitType
                           ,s.name
                           ,<selectgt.bigBlind>                                             AS bigBlindDesc
                           ,<hcgametypeId>                                                  AS gtId
                           ,sum(HDs)                                                        AS n
                           ,format(100.0*sum(street0VPI)/sum(HDs),1)                        AS vpip
                           ,format(100.0*sum(street0Aggr)/sum(HDs),1)                       AS pfr
                           ,case when sum(street0_3Bchance) = 0 then '0'
                                 else format(100.0*sum(street0_3Bdone)/sum(street0_3Bchance),1)
                            end                                                             AS pf3
                           ,case when sum(street0_4Bchance) = 0 then '0'
                                 else format(100.0*sum(street0_4Bdone)/sum(street0_4Bchance),1)
                            end                                                             AS pf4
                           ,case when sum(street0_FoldTo3Bchance) = 0 then '0'
                                 else format(100.0*sum(street0_FoldTo3Bdone)/sum(street0_FoldTo3Bchance),1)
                            end                                                             AS pff3
                           ,case when sum(street0_FoldTo4Bchance) = 0 then '0'
                                 else format(100.0*sum(street0_FoldTo4Bdone)/sum(street0_FoldTo4Bchance),1)
                            end                                                             AS pff4
                           ,case when sum(raiseFirstInChance) = 0 then '-'
                                 else format(100.0*sum(raisedFirstIn)/sum(raiseFirstInChance),1)
                            end                                                             AS steals
                           ,format(100.0*sum(street1Seen)/sum(HDs),1)                       AS saw_f
                           ,format(100.0*sum(sawShowdown)/sum(HDs),1)                       AS sawsd
                           ,case when sum(street1Seen) = 0 then '-'
                                 else format(100.0*sum(sawShowdown)/sum(street1Seen),1)
                            end                                                             AS wtsdwsf
                           ,case when sum(sawShowdown) = 0 then '-'
                                 else format(100.0*sum(wonAtSD)/sum(sawShowdown),1)
                            end                                                             AS wmsd
                           ,case when sum(street1Seen) = 0 then '-'
                                 else format(100.0*sum(street1Aggr)/sum(street1Seen),1)
                            end                                                             AS FlAFq
                           ,case when sum(street2Seen) = 0 then '-'
                                 else format(100.0*sum(street2Aggr)/sum(street2Seen),1)
                            end                                                             AS TuAFq
                           ,case when sum(street3Seen) = 0 then '-'
                                else format(100.0*sum(street3Aggr)/sum(street3Seen),1)
                            end                                                             AS RvAFq
                           ,case when sum(street1Seen)+sum(street2Seen)+sum(street3Seen) = 0 then '-'
                                else format(100.0*(sum(street1Aggr)+sum(street2Aggr)+sum(street3Aggr))
                                         /(sum(street1Seen)+sum(street2Seen)+sum(street3Seen)),1)
                            end                                                             AS PoFAFq
                           ,format(sum(totalProfit)/100.0,2)                                AS Net
                           ,format((sum(totalProfit/(gt.bigBlind+0.0))) / (sum(HDs)/100.0),2)
                                                                                            AS BBper100
                           ,format( (sum(totalProfit)/100.0) / sum(HDs), 4)                 AS Profitperhand
                           ,format( sum(activeSeats*HDs)/(sum(HDs)+0.0), 2)                 AS AvgSeats
                     from Gametypes gt
                          inner join Sites s on s.Id = gt.siteId
                          inner join HudCache hc on hc.gametypeId = gt.Id
                     where hc.playerId in <player_test>
                     and   <gtbigBlind_test>
                     and   hc.activeSeats <seats_test>
                     and   concat( '20', substring(hc.styleKey,2,2), '-', substring(hc.styleKey,4,2), '-'
                                 , substring(hc.styleKey,6,2) ) <datestest>
                     group by gt.base
                          ,gt.category
                          ,upper(gt.limitType)
                          ,s.name
                          <groupbygt.bigBlind>
                          ,gtId
                    ) stats
                inner join
                    ( select # profit from handsplayers/handsactions
                             hprof.gtId, sum(hprof.profit) sum_profit,
                             avg(hprof.profit/100.0) profitperhand,
                             case when hprof.gtId = -1 then -999
                                  else variance(hprof.profit/100.0)
                             end as variance
                      from
                          (select hp.handId, <hgametypeId> as gtId, hp.totalProfit as profit
                           from HandsPlayers hp
                           inner join Hands h        ON h.id            = hp.handId
                           where hp.playerId in <player_test>
                           and   hp.tourneysPlayersId IS NULL
                           and   date_format(h.startTime, '%Y-%m-%d') <datestest>
                           group by hp.handId, gtId, hp.totalProfit
                          ) hprof
                      group by hprof.gtId
                     ) hprof2
                    on hprof2.gtId = stats.gtId
                order by stats.category, stats.limittype, stats.bigBlindDesc desc <orderbyseats>"""
        #elif db_server == 'sqlite': #TODO
        #    self.query['playerStats'] = """ """
        else:  # assume postgres
            self.query['playerStats'] = """
                SELECT upper(stats.limitType) || ' '
                       || initcap(stats.category) || ' '
                       || stats.name || ' '
                       || stats.bigBlindDesc                                          AS Game
                      ,stats.n
                      ,stats.vpip
                      ,stats.pfr
                      ,stats.pf3
                      ,stats.pf4
                      ,stats.pff3
                      ,stats.pff4
                      ,stats.steals
                      ,stats.saw_f
                      ,stats.sawsd
                      ,stats.wtsdwsf
                      ,stats.wmsd
                      ,stats.FlAFq
                      ,stats.TuAFq
                      ,stats.RvAFq
                      ,stats.PoFAFq
                      ,stats.Net
                      ,stats.BBper100
                      ,stats.Profitperhand
                      ,case when hprof2.variance = -999 then '-'
                            else to_char(hprof2.variance, '0D00')
                       end                                                          AS Variance
                      ,AvgSeats
                FROM
                    (select gt.base
                           ,gt.category
                           ,upper(gt.limitType)                                             AS limitType
                           ,s.name
                           ,<selectgt.bigBlind>                                             AS bigBlindDesc
                           ,<hcgametypeId>                                                  AS gtId
                           ,sum(HDs) as n
                           ,to_char(100.0*sum(street0VPI)/sum(HDs),'990D0')                 AS vpip
                           ,to_char(100.0*sum(street0Aggr)/sum(HDs),'90D0')                 AS pfr
                           ,case when sum(street0_3Bchance) = 0 then '0'
                                 else to_char(100.0*sum(street0_3Bdone)/sum(street0_3Bchance),'90D0')
                            end                                                             AS pf3
                           ,case when sum(raiseFirstInChance) = 0 then '-'
                                 else to_char(100.0*sum(raisedFirstIn)/sum(raiseFirstInChance),'90D0')
                            end                                                             AS steals
                           ,to_char(100.0*sum(street1Seen)/sum(HDs),'90D0')                 AS saw_f
                           ,to_char(100.0*sum(sawShowdown)/sum(HDs),'90D0')                 AS sawsd
                           ,case when sum(street1Seen) = 0 then '-'
                                 else to_char(100.0*sum(sawShowdown)/sum(street1Seen),'90D0')
                            end                                                             AS wtsdwsf
                           ,case when sum(sawShowdown) = 0 then '-'
                                 else to_char(100.0*sum(wonAtSD)/sum(sawShowdown),'90D0')
                            end                                                             AS wmsd
                           ,case when sum(street1Seen) = 0 then '-'
                                 else to_char(100.0*sum(street1Aggr)/sum(street1Seen),'90D0')
                            end                                                             AS FlAFq
                           ,case when sum(street2Seen) = 0 then '-'
                                 else to_char(100.0*sum(street2Aggr)/sum(street2Seen),'90D0')
                            end                                                             AS TuAFq
                           ,case when sum(street3Seen) = 0 then '-'
                                else to_char(100.0*sum(street3Aggr)/sum(street3Seen),'90D0')
                            end                                                             AS RvAFq
                           ,case when sum(street1Seen)+sum(street2Seen)+sum(street3Seen) = 0 then '-'
                                else to_char(100.0*(sum(street1Aggr)+sum(street2Aggr)+sum(street3Aggr))
                                         /(sum(street1Seen)+sum(street2Seen)+sum(street3Seen)),'90D0')
                            end                                                             AS PoFAFq
                           ,round(sum(totalProfit)/100.0,2)                                 AS Net
                           ,to_char((sum(totalProfit/(gt.bigBlind+0.0))) / (sum(HDs)/100.0), '990D00')
                                                                                            AS BBper100
                           ,to_char(sum(totalProfit/100.0) / (sum(HDs)+0.0), '990D0000')    AS Profitperhand
                           ,to_char(sum(activeSeats*HDs)/(sum(HDs)+0.0),'90D00')            AS AvgSeats
                     from Gametypes gt
                          inner join Sites s on s.Id = gt.siteId
                          inner join HudCache hc on hc.gametypeId = gt.Id
                     where hc.playerId in <player_test>
                     and   <gtbigBlind_test>
                     and   hc.activeSeats <seats_test>
                     and   '20' || SUBSTR(hc.styleKey,2,2) || '-' || SUBSTR(hc.styleKey,4,2) || '-'
                           || SUBSTR(hc.styleKey,6,2) <datestest>
                     group by gt.base
                          ,gt.category
                          ,upper(gt.limitType)
                          ,s.name
                          <groupbygt.bigBlind>
                          ,gtId
                    ) stats
                inner join
                    ( select
                             hprof.gtId, sum(hprof.profit) AS sum_profit,
                             avg(hprof.profit/100.0) AS profitperhand,
                             case when hprof.gtId = -1 then -999
                                  else variance(hprof.profit/100.0)
                             end as variance
                      from
                          (select hp.handId, <hgametypeId> as gtId, hp.totalProfit as profit
                           from HandsPlayers hp
                           inner join Hands h   ON (h.id = hp.handId)
                           where hp.playerId in <player_test>
                           and   hp.tourneysPlayersId IS NULL
                           and   to_char(h.startTime, 'YYYY-MM-DD') <datestest>
                           group by hp.handId, gtId, hp.totalProfit
                          ) hprof
                      group by hprof.gtId
                     ) hprof2
                    on hprof2.gtId = stats.gtId
                order by stats.base, stats.limittype, stats.bigBlindDesc desc <orderbyseats>"""

        if db_server == 'mysql':
            self.query['playerStatsByPosition'] = """
                SELECT
                      concat(upper(stats.limitType), ' '
                            ,concat(upper(substring(stats.category,1,1)),substring(stats.category,2) ), ' '
                            ,stats.name, ' '
                            ,cast(stats.bigBlindDesc as char)
                            )                                                      AS Game
                     ,case when stats.PlPosition = -2 then 'BB'
                           when stats.PlPosition = -1 then 'SB'
                           when stats.PlPosition =  0 then 'Btn'
                           when stats.PlPosition =  1 then 'CO'
                           when stats.PlPosition =  2 then 'MP'
                           when stats.PlPosition =  5 then 'EP'
                           else 'xx'
                      end                                                          AS PlPosition
                     ,stats.n
                     ,stats.vpip
                     ,stats.pfr
                     ,stats.pf3
                     ,stats.pf4
                     ,stats.pff3
                     ,stats.pff4
                     ,stats.steals
                     ,stats.saw_f
                     ,stats.sawsd
                     ,stats.wtsdwsf
                     ,stats.wmsd
                     ,stats.FlAFq
                     ,stats.TuAFq
                     ,stats.RvAFq
                     ,stats.PoFAFq
                     ,stats.Net
                     ,stats.BBper100
                     ,stats.Profitperhand
                     ,case when hprof2.variance = -999 then '-'
                           else format(hprof2.variance, 2)
                      end                                                          AS Variance
                     ,stats.AvgSeats
                FROM
                    (select /* stats from hudcache */
                            gt.base
                           ,gt.category
                           ,upper(gt.limitType)                                             AS limitType
                           ,s.name
                           ,<selectgt.bigBlind>                                             AS bigBlindDesc
                           ,<hcgametypeId>                                                  AS gtId
                           ,case when hc.position = 'B' then -2
                                 when hc.position = 'S' then -1
                                 when hc.position = 'D' then  0
                                 when hc.position = 'C' then  1
                                 when hc.position = 'M' then  2
                                 when hc.position = 'E' then  5
                                 else 9
                            end                                                             as PlPosition
                           ,sum(HDs)                                                        AS n
                           ,format(100.0*sum(street0VPI)/sum(HDs),1)                        AS vpip
                           ,format(100.0*sum(street0Aggr)/sum(HDs),1)                       AS pfr
                           ,case when sum(street0_3Bchance) = 0 then '0'
                                 else format(100.0*sum(street0_3Bdone)/sum(street0_3Bchance),1)
                            end                                                             AS pf3
                           ,case when sum(street0_4Bchance) = 0 then '0'
                                 else format(100.0*sum(street0_4Bdone)/sum(street0_4Bchance),1)
                            end                                                             AS pf4
                           ,case when sum(street0_FoldTo3Bchance) = 0 then '0'
                                 else format(100.0*sum(street0_FoldTo3Bdone)/sum(street0_FoldTo3Bchance),1)
                            end                                                             AS pff3
                           ,case when sum(street0_FoldTo4Bchance) = 0 then '0'
                                 else format(100.0*sum(street0_FoldTo4Bdone)/sum(street0_FoldTo4Bchance),1)
                            end                                                             AS pff4
                           ,case when sum(raiseFirstInChance) = 0 then '-'
                                 else format(100.0*sum(raisedFirstIn)/sum(raiseFirstInChance),1)
                            end                                                             AS steals
                           ,format(100.0*sum(street1Seen)/sum(HDs),1)                       AS saw_f
                           ,format(100.0*sum(sawShowdown)/sum(HDs),1)                       AS sawsd
                           ,case when sum(street1Seen) = 0 then '-'
                                 else format(100.0*sum(sawShowdown)/sum(street1Seen),1)
                            end                                                             AS wtsdwsf
                           ,case when sum(sawShowdown) = 0 then '-'
                                 else format(100.0*sum(wonAtSD)/sum(sawShowdown),1)
                            end                                                             AS wmsd
                           ,case when sum(street1Seen) = 0 then '-'
                                 else format(100.0*sum(street1Aggr)/sum(street1Seen),1)
                            end                                                             AS FlAFq
                           ,case when sum(street2Seen) = 0 then '-'
                                 else format(100.0*sum(street2Aggr)/sum(street2Seen),1)
                            end                                                             AS TuAFq
                           ,case when sum(street3Seen) = 0 then '-'
                                else format(100.0*sum(street3Aggr)/sum(street3Seen),1)
                            end                                                             AS RvAFq
                           ,case when sum(street1Seen)+sum(street2Seen)+sum(street3Seen) = 0 then '-'
                                else format(100.0*(sum(street1Aggr)+sum(street2Aggr)+sum(street3Aggr))
                                         /(sum(street1Seen)+sum(street2Seen)+sum(street3Seen)),1)
                            end                                                             AS PoFAFq
                           ,format(sum(totalProfit)/100.0,2)                                AS Net
                           ,format((sum(totalProfit/(gt.bigBlind+0.0))) / (sum(HDs)/100.0),2)
                                                                                            AS BBper100
                           ,format( (sum(totalProfit)/100.0) / sum(HDs), 4)                 AS Profitperhand
                           ,format( sum(activeSeats*HDs)/(sum(HDs)+0.0), 2)                 AS AvgSeats
                     from Gametypes gt
                          inner join Sites s on s.Id = gt.siteId
                          inner join HudCache hc on hc.gametypeId = gt.Id
                     where hc.playerId in <player_test>
                     and   <gtbigBlind_test>
                     and   hc.activeSeats <seats_test>
                     and   concat( '20', substring(hc.styleKey,2,2), '-', substring(hc.styleKey,4,2), '-'
                                 , substring(hc.styleKey,6,2) ) <datestest>
                     group by gt.base
                          ,gt.category
                          ,upper(gt.limitType)
                          ,s.name
                          <groupbygt.bigBlind>
                          ,gtId
                          <groupbyseats>
                          ,PlPosition
                    ) stats
                inner join
                    ( select # profit from handsplayers/handsactions
                             hprof.gtId,
                             case when hprof.position = 'B' then -2
                                  when hprof.position = 'S' then -1
                                  when hprof.position in ('3','4') then 2
                                  when hprof.position in ('6','7') then 5
                                  else hprof.position
                             end                                      as PlPosition,
                             sum(hprof.profit) as sum_profit,
                             avg(hprof.profit/100.0) as profitperhand,
                             case when hprof.gtId = -1 then -999
                                  else variance(hprof.profit/100.0)
                             end as variance
                      from
                          (select hp.handId, <hgametypeId> as gtId, hp.position
                                , hp.totalProfit as profit
                           from HandsPlayers hp
                           inner join Hands h  ON  (h.id = hp.handId)
                           where hp.playerId in <player_test>
                           and   hp.tourneysPlayersId IS NULL
                           and   date_format(h.startTime, '%Y-%m-%d') <datestest>
                           group by hp.handId, gtId, hp.position, hp.totalProfit
                          ) hprof
                      group by hprof.gtId, PlPosition
                     ) hprof2
                    on (    hprof2.gtId = stats.gtId
                        and hprof2.PlPosition = stats.PlPosition)
                order by stats.category, stats.limitType, stats.bigBlindDesc desc
                         <orderbyseats>, cast(stats.PlPosition as signed)
                """
        elif db_server == 'sqlite':
            self.query['playerStatsByPosition'] = ""#TODO
        else:  # assume postgresql
            self.query['playerStatsByPosition'] = """
                select /* stats from hudcache */
                       upper(stats.limitType) || ' '
                       || upper(substr(stats.category,1,1)) || substr(stats.category,2) || ' '
                       || stats.name || ' '
                       || stats.bigBlindDesc                                        AS Game
                      ,case when stats.PlPosition = -2 then 'BB'
                            when stats.PlPosition = -1 then 'SB'
                            when stats.PlPosition =  0 then 'Btn'
                            when stats.PlPosition =  1 then 'CO'
                            when stats.PlPosition =  2 then 'MP'
                            when stats.PlPosition =  5 then 'EP'
                            else 'xx'
                       end                                                          AS PlPosition
                      ,stats.n
                      ,stats.vpip
                      ,stats.pfr
                      ,stats.pf3
                      ,stats.pf4
                      ,stats.pff3
                      ,stats.pff4
                      ,stats.steals
                      ,stats.saw_f
                      ,stats.sawsd
                      ,stats.wtsdwsf
                      ,stats.wmsd
                      ,stats.FlAFq
                      ,stats.TuAFq
                      ,stats.RvAFq
                      ,stats.PoFAFq
                      ,stats.Net
                      ,stats.BBper100
                      ,stats.Profitperhand
                      ,case when hprof2.variance = -999 then '-'
                            else to_char(hprof2.variance, '0D00')
                       end                                                          AS Variance
                      ,stats.AvgSeats
                FROM
                    (select /* stats from hudcache */
                            gt.base
                           ,gt.category
                           ,upper(gt.limitType)                                             AS limitType
                           ,s.name
                           ,<selectgt.bigBlind>                                             AS bigBlindDesc
                           ,<hcgametypeId>                                                  AS gtId
                           ,case when hc.position = 'B' then -2
                                 when hc.position = 'S' then -1
                                 when hc.position = 'D' then  0
                                 when hc.position = 'C' then  1
                                 when hc.position = 'M' then  2
                                 when hc.position = 'E' then  5
                                 else 9
                            end                                                             AS PlPosition
                           ,sum(HDs)                                                        AS n
                           ,to_char(round(100.0*sum(street0VPI)/sum(HDs)),'990D0')          AS vpip
                           ,to_char(round(100.0*sum(street0Aggr)/sum(HDs)),'90D0')          AS pfr
                           ,case when sum(street0_3Bchance) = 0 then '0'
                                 else to_char(100.0*sum(street0_3Bdone)/sum(street0_3Bchance),'90D0')
                            end                                                             AS pf3
                           ,case when sum(street0_4Bchance) = 0 then '0'
                                 else to_char(100.0*sum(street0_4Bdone)/sum(street0_4Bchance),'90D0')
                            end                                                             AS pf4
                           ,case when sum(street0_FoldTo3Bchance) = 0 then '0'
                                 else to_char(100.0*sum(street0_FoldTo3Bdone)/sum(street0_FoldTo3Bchance),'90D0')
                            end                                                             AS pff3
                           ,case when sum(street0_FoldTo4Bchance) = 0 then '0'
                                 else to_char(100.0*sum(street0_FoldTo4Bdone)/sum(street0_FoldTo4Bchance),'90D0')
                            end                                                             AS pff4
                           ,case when sum(raiseFirstInChance) = 0 then '-'
                                 else to_char(100.0*sum(raisedFirstIn)/sum(raiseFirstInChance),'90D0')
                            end                                                             AS steals
                           ,to_char(round(100.0*sum(street1Seen)/sum(HDs)),'90D0')          AS saw_f
                           ,to_char(round(100.0*sum(sawShowdown)/sum(HDs)),'90D0')          AS sawsd
                           ,case when sum(street1Seen) = 0 then '-'
                                 else to_char(round(100.0*sum(sawShowdown)/sum(street1Seen)),'90D0')
                            end                                                             AS wtsdwsf
                           ,case when sum(sawShowdown) = 0 then '-'
                                 else to_char(round(100.0*sum(wonAtSD)/sum(sawShowdown)),'90D0')
                            end                                                             AS wmsd
                           ,case when sum(street1Seen) = 0 then '-'
                                 else to_char(round(100.0*sum(street1Aggr)/sum(street1Seen)),'90D0')
                            end                                                             AS FlAFq
                           ,case when sum(street2Seen) = 0 then '-'
                                 else to_char(round(100.0*sum(street2Aggr)/sum(street2Seen)),'90D0')
                            end                                                             AS TuAFq
                           ,case when sum(street3Seen) = 0 then '-'
                                else to_char(round(100.0*sum(street3Aggr)/sum(street3Seen)),'90D0')
                            end                                                             AS RvAFq
                           ,case when sum(street1Seen)+sum(street2Seen)+sum(street3Seen) = 0 then '-'
                                else to_char(round(100.0*(sum(street1Aggr)+sum(street2Aggr)+sum(street3Aggr))
                                         /(sum(street1Seen)+sum(street2Seen)+sum(street3Seen))),'90D0')
                            end                                                             AS PoFAFq
                           ,to_char(sum(totalProfit)/100.0,'9G999G990D00')                  AS Net
                           ,case when sum(HDs) = 0 then '0'
                                 else to_char(sum(totalProfit/(gt.bigBlind+0.0)) / (sum(HDs)/100.0), '990D00')
                            end                                                             AS BBper100
                           ,case when sum(HDs) = 0 then '0'
                                 else to_char( (sum(totalProfit)/100.0) / sum(HDs), '90D0000')
                            end                                                             AS Profitperhand
                           ,to_char(sum(activeSeats*HDs)/(sum(HDs)+0.0),'90D00')            AS AvgSeats
                     from Gametypes gt
                          inner join Sites s     on (s.Id = gt.siteId)
                          inner join HudCache hc on (hc.gametypeId = gt.Id)
                     where hc.playerId in <player_test>
                     and   <gtbigBlind_test>
                     and   hc.activeSeats <seats_test>
                     and   '20' || SUBSTR(hc.styleKey,2,2) || '-' || SUBSTR(hc.styleKey,4,2) || '-'
                           || SUBSTR(hc.styleKey,6,2) <datestest>
                     group by gt.base
                          ,gt.category
                          ,upper(gt.limitType)
                          ,s.name
                          <groupbygt.bigBlind>
                          ,gtId
                          <groupbyseats>
                          ,PlPosition
                    ) stats
                inner join
                    ( select /* profit from handsplayers/handsactions */
                             hprof.gtId,
                             case when hprof.position = 'B' then -2
                                  when hprof.position = 'S' then -1
                                  when hprof.position in ('3','4') then 2
                                  when hprof.position in ('6','7') then 5
                                  else cast(hprof.position as smallint)
                             end                                      as PlPosition,
                             sum(hprof.profit) as sum_profit,
                             avg(hprof.profit/100.0) as profitperhand,
                             case when hprof.gtId = -1 then -999
                                  else variance(hprof.profit/100.0)
                             end as variance
                      from
                          (select hp.handId, <hgametypeId> as gtId, hp.position
                                , hp.totalProfit as profit
                           from HandsPlayers hp
                           inner join Hands h  ON  (h.id = hp.handId)
                           where hp.playerId in <player_test>
                           and   hp.tourneysPlayersId IS NULL
                           and   to_char(h.startTime, 'YYYY-MM-DD') <datestest>
                           group by hp.handId, gametypeId, hp.position, hp.totalProfit
                          ) hprof
                      group by hprof.gtId, PlPosition
                    ) hprof2
                    on (    hprof2.gtId = stats.gtId
                        and hprof2.PlPosition = stats.PlPosition)
                order by stats.category, stats.limitType, stats.bigBlindDesc desc
                         <orderbyseats>, cast(stats.PlPosition as smallint)
                """

        ####################################
        # Cash Game Graph query
        ####################################
        self.query['getRingProfitAllHandsPlayerIdSite'] = """
            SELECT hp.handId, hp.totalProfit, hp.sawShowdown
            FROM HandsPlayers hp
            INNER JOIN Players pl      ON  (pl.id = hp.playerId)
            INNER JOIN Hands h         ON  (h.id  = hp.handId)
            INNER JOIN Gametypes gt    ON  (gt.id = h.gametypeId)
            WHERE pl.id in <player_test>
            AND   pl.siteId in <site_test>
            AND   h.startTime > '<startdate_test>'
            AND   h.startTime < '<enddate_test>'
            <limit_test>
            <game_test>
            AND   gt.type = 'ring'
            GROUP BY h.startTime, hp.handId, hp.sawShowdown, hp.totalProfit
            ORDER BY h.startTime"""

        self.query['getRingProfitAllHandsPlayerIdSiteInBB'] = """
            SELECT hp.handId, ( hp.totalProfit / ( gt.bigBlind  * 2 ) ) * 100 , hp.sawShowdown
            FROM HandsPlayers hp
            INNER JOIN Players pl      ON  (pl.id = hp.playerId)
            INNER JOIN Hands h         ON  (h.id  = hp.handId)
            INNER JOIN Gametypes gt    ON  (gt.id = h.gametypeId)
            WHERE pl.id in <player_test>
            AND   pl.siteId in <site_test>
            AND   h.startTime > '<startdate_test>'
            AND   h.startTime < '<enddate_test>'
            <limit_test>
            <game_test>
            AND   hp.tourneysPlayersId IS NULL
            GROUP BY h.startTime, hp.handId, hp.sawShowdown, ( hp.totalProfit / ( gt.bigBlind  * 2 ) ) * 100
            ORDER BY h.startTime"""

        self.query['getRingProfitAllHandsPlayerIdSiteInDollars'] = """
            SELECT hp.handId, hp.totalProfit, hp.sawShowdown
            FROM HandsPlayers hp
            INNER JOIN Players pl      ON  (pl.id = hp.playerId)
            INNER JOIN Hands h         ON  (h.id  = hp.handId)
            INNER JOIN Gametypes gt    ON  (gt.id = h.gametypeId)
            WHERE pl.id in <player_test>
            AND   pl.siteId in <site_test>
            AND   h.startTime > '<startdate_test>'
            AND   h.startTime < '<enddate_test>'
            <limit_test>
            <game_test>
            AND   hp.tourneysPlayersId IS NULL
            GROUP BY h.startTime, hp.handId, hp.sawShowdown, hp.totalProfit
            ORDER BY h.startTime"""



        ####################################
        # Tourney Results query
        ####################################
        self.query['tourneyResults'] = """
            SELECT tp.tourneyId, (coalesce(tp.winnings,0) - coalesce(tt.buyIn,0) - coalesce(tt.fee,0)) as profit, tp.koCount, tp.rebuyCount, tp.addOnCount, tt.buyIn, tt.fee, t.siteTourneyNo
            FROM TourneysPlayers tp
            INNER JOIN Players pl      ON  (pl.id = tp.playerId)
            INNER JOIN Tourneys t         ON  (t.id  = tp.tourneyId)
            INNER JOIN TourneyTypes tt    ON  (tt.id = t.tourneyTypeId)
            WHERE pl.id in <player_test>
            AND   pl.siteId in <site_test>
            AND   t.startTime > '<startdate_test>'
            AND   t.startTime < '<enddate_test>'
            GROUP BY t.startTime, tp.tourneyId, tp.winningsCurrency,
                     tp.winnings, tp.koCount,
                     tp.rebuyCount, tp.addOnCount,
                     tt.buyIn, tt.fee
            ORDER BY t.startTime"""

            #AND   gt.type = 'ring'
            #<limit_test>
            #<game_test>

        ####################################
        # Session stats query
        ####################################
        if db_server == 'mysql':
            self.query['sessionStats'] = """
                SELECT UNIX_TIMESTAMP(h.startTime) as time, hp.handId, hp.startCash, hp.winnings, hp.totalProfit
                FROM HandsPlayers hp
                 INNER JOIN Hands h       on  (h.id = hp.handId)
                 INNER JOIN Gametypes gt  on  (gt.Id = h.gametypeId)
                 INNER JOIN Sites s       on  (s.Id = gt.siteId)
                 INNER JOIN Players p     on  (p.Id = hp.playerId)
                WHERE hp.playerId in <player_test>
                 AND  date_format(h.startTime, '%Y-%m-%d') <datestest>
                 AND  gt.type LIKE 'ring'
                ORDER by time"""
        elif db_server == 'postgresql':
            self.query['sessionStats'] = """
                SELECT EXTRACT(epoch from h.startTime) as time, hp.handId, hp.startCash, hp.winnings, hp.totalProfit
                FROM HandsPlayers hp
                 INNER JOIN Hands h       on  (h.id = hp.handId)
                 INNER JOIN Gametypes gt  on  (gt.Id = h.gametypeId)
                 INNER JOIN Sites s       on  (s.Id = gt.siteId)
                 INNER JOIN Players p     on  (p.Id = hp.playerId)
                WHERE hp.playerId in <player_test>
                 AND  h.startTime <datestest>
                 AND  gt.type LIKE 'ring'
                ORDER by time"""
        elif db_server == 'sqlite':
            self.query['sessionStats'] = """
                SELECT STRFTIME('<ampersand_s>', h.startTime) as time, hp.handId, hp.startCash, hp.winnings, hp.totalProfit
                FROM HandsPlayers hp
                 INNER JOIN Hands h       on  (h.id = hp.handId)
                 INNER JOIN Gametypes gt  on  (gt.Id = h.gametypeId)
                 INNER JOIN Sites s       on  (s.Id = gt.siteId)
                 INNER JOIN Players p     on  (p.Id = hp.playerId)
                WHERE hp.playerId in <player_test>
                 AND  h.startTime <datestest>
                 AND  gt.type is 'ring'
                ORDER by time"""


        ####################################
        # Queries to rebuild/modify hudcache
        ####################################
      
        self.query['clearHudCache'] = """DELETE FROM HudCache"""
       
        if db_server == 'mysql':
            self.query['rebuildHudCache'] = """
                INSERT INTO HudCache
                (gametypeId
                ,playerId
                ,activeSeats
                ,position
                <tourney_insert_clause>
                ,styleKey
                ,HDs
                ,wonWhenSeenStreet1
                ,wonWhenSeenStreet2
                ,wonWhenSeenStreet3
                ,wonWhenSeenStreet4
                ,wonAtSD
                ,street0VPI
                ,street0Aggr
                ,street0_3BChance
                ,street0_3BDone
                ,street0_4BChance
                ,street0_4BDone
                ,street0_C4BChance
                ,street0_C4BDone
                ,street0_FoldTo3BChance
                ,street0_FoldTo3BDone
                ,street0_FoldTo4BChance
                ,street0_FoldTo4BDone
                ,street0_SqueezeChance
                ,street0_SqueezeDone
                ,raiseToStealChance
                ,raiseToStealDone
                ,success_Steal
                ,street1Seen
                ,street2Seen
                ,street3Seen
                ,street4Seen
                ,sawShowdown
                ,street1Aggr
                ,street2Aggr
                ,street3Aggr
                ,street4Aggr
                ,otherRaisedStreet0
                ,otherRaisedStreet1
                ,otherRaisedStreet2
                ,otherRaisedStreet3
                ,otherRaisedStreet4
                ,foldToOtherRaisedStreet0
                ,foldToOtherRaisedStreet1
                ,foldToOtherRaisedStreet2
                ,foldToOtherRaisedStreet3
                ,foldToOtherRaisedStreet4
                ,raiseFirstInChance
                ,raisedFirstIn
                ,foldBbToStealChance
                ,foldedBbToSteal
                ,foldSbToStealChance
                ,foldedSbToSteal
                ,street1CBChance
                ,street1CBDone
                ,street2CBChance
                ,street2CBDone
                ,street3CBChance
                ,street3CBDone
                ,street4CBChance
                ,street4CBDone
                ,foldToStreet1CBChance
                ,foldToStreet1CBDone
                ,foldToStreet2CBChance
                ,foldToStreet2CBDone
                ,foldToStreet3CBChance
                ,foldToStreet3CBDone
                ,foldToStreet4CBChance
                ,foldToStreet4CBDone
                ,totalProfit
                ,street1CheckCallRaiseChance
                ,street1CheckCallRaiseDone
                ,street2CheckCallRaiseChance
                ,street2CheckCallRaiseDone
                ,street3CheckCallRaiseChance
                ,street3CheckCallRaiseDone
                ,street4CheckCallRaiseChance
                ,street4CheckCallRaiseDone
                ,street0Calls
                ,street1Calls
                ,street2Calls
                ,street3Calls
                ,street4Calls
                ,street0Bets
                ,street1Bets
                ,street2Bets
                ,street3Bets
                ,street4Bets
                ,street0Raises
                ,street1Raises
                ,street2Raises
                ,street3Raises
                ,street4Raises
                )
                SELECT h.gametypeId
                      ,hp.playerId
                      ,h.seats
                      ,case when hp.position = 'B' then 'B'
                            when hp.position = 'S' then 'S'
                            when hp.position = '0' then 'D'
                            when hp.position = '1' then 'C'
                            when hp.position = '2' then 'M'
                            when hp.position = '3' then 'M'
                            when hp.position = '4' then 'M'
                            when hp.position = '5' then 'E'
                            when hp.position = '6' then 'E'
                            when hp.position = '7' then 'E'
                            when hp.position = '8' then 'E'
                            when hp.position = '9' then 'E'
                            else 'E'
                       end                                            AS hc_position
                      <tourney_select_clause>
                      ,date_format(h.startTime, 'd%y%m%d')
                      ,count(1)
                      ,sum(wonWhenSeenStreet1)
                      ,sum(wonWhenSeenStreet2)
                      ,sum(wonWhenSeenStreet3)
                      ,sum(wonWhenSeenStreet4)
                      ,sum(wonAtSD)
                      ,sum(street0VPI)
                      ,sum(street0Aggr)
                      ,sum(street0_3BChance)
                      ,sum(street0_3BDone)
                      ,sum(street0_4BChance)
                      ,sum(street0_4BDone)
                      ,sum(street0_C4BChance)
                      ,sum(street0_C4BDone)
                      ,sum(street0_FoldTo3BChance)
                      ,sum(street0_FoldTo3BDone)
                      ,sum(street0_FoldTo4BChance)
                      ,sum(street0_FoldTo4BDone)
                      ,sum(street0_SqueezeChance)
                      ,sum(street0_SqueezeDone)
                      ,sum(raiseToStealChance)
                      ,sum(raiseToStealDone)
                      ,sum(success_Steal)
                      ,sum(street1Seen)
                      ,sum(street2Seen)
                      ,sum(street3Seen)
                      ,sum(street4Seen)
                      ,sum(sawShowdown)
                      ,sum(street1Aggr)
                      ,sum(street2Aggr)
                      ,sum(street3Aggr)
                      ,sum(street4Aggr)
                      ,sum(otherRaisedStreet0)
                      ,sum(otherRaisedStreet1)
                      ,sum(otherRaisedStreet2)
                      ,sum(otherRaisedStreet3)
                      ,sum(otherRaisedStreet4)
                      ,sum(foldToOtherRaisedStreet0)
                      ,sum(foldToOtherRaisedStreet1)
                      ,sum(foldToOtherRaisedStreet2)
                      ,sum(foldToOtherRaisedStreet3)
                      ,sum(foldToOtherRaisedStreet4)
                      ,sum(raiseFirstInChance)
                      ,sum(raisedFirstIn)
                      ,sum(foldBbToStealChance)
                      ,sum(foldedBbToSteal)
                      ,sum(foldSbToStealChance)
                      ,sum(foldedSbToSteal)
                      ,sum(street1CBChance)
                      ,sum(street1CBDone)
                      ,sum(street2CBChance)
                      ,sum(street2CBDone)
                      ,sum(street3CBChance)
                      ,sum(street3CBDone)
                      ,sum(street4CBChance)
                      ,sum(street4CBDone)
                      ,sum(foldToStreet1CBChance)
                      ,sum(foldToStreet1CBDone)
                      ,sum(foldToStreet2CBChance)
                      ,sum(foldToStreet2CBDone)
                      ,sum(foldToStreet3CBChance)
                      ,sum(foldToStreet3CBDone)
                      ,sum(foldToStreet4CBChance)
                      ,sum(foldToStreet4CBDone)
                      ,sum(totalProfit)
                      ,sum(street1CheckCallRaiseChance)
                      ,sum(street1CheckCallRaiseDone)
                      ,sum(street2CheckCallRaiseChance)
                      ,sum(street2CheckCallRaiseDone)
                      ,sum(street3CheckCallRaiseChance)
                      ,sum(street3CheckCallRaiseDone)
                      ,sum(street4CheckCallRaiseChance)
                      ,sum(street4CheckCallRaiseDone)
                      ,sum(street0Calls)
                      ,sum(street1Calls)
                      ,sum(street2Calls)
                      ,sum(street3Calls)
                      ,sum(street4Calls)
                      ,sum(street0Bets)
                      ,sum(street1Bets)
                      ,sum(street2Bets)
                      ,sum(street3Bets)
                      ,sum(street4Bets)
                      ,sum(hp.street0Raises)
                      ,sum(hp.street1Raises)
                      ,sum(hp.street2Raises)
                      ,sum(hp.street3Raises)
                      ,sum(hp.street4Raises)
                FROM HandsPlayers hp
                INNER JOIN Hands h ON (h.id = hp.handId)
                <tourney_join_clause>
                <where_clause>
                GROUP BY h.gametypeId
                        ,hp.playerId
                        ,h.seats
                        ,hc_position
                        <tourney_group_clause>
                        ,date_format(h.startTime, 'd%y%m%d')
"""
        elif db_server == 'postgresql':
            self.query['rebuildHudCache'] = """
                INSERT INTO HudCache
                (gametypeId
                ,playerId
                ,activeSeats
                ,position
                <tourney_insert_clause>
                ,styleKey
                ,HDs
                ,wonWhenSeenStreet1
                ,wonWhenSeenStreet2
                ,wonWhenSeenStreet3
                ,wonWhenSeenStreet4
                ,wonAtSD
                ,street0VPI
                ,street0Aggr
                ,street0_3BChance
                ,street0_3BDone
                ,street0_4BChance
                ,street0_4BDone
                ,street0_C4BChance
                ,street0_C4BDone
                ,street0_FoldTo3BChance
                ,street0_FoldTo3BDone
                ,street0_FoldTo4BChance
                ,street0_FoldTo4BDone
                ,street0_SqueezeChance
                ,street0_SqueezeDone
                ,raiseToStealChance
                ,raiseToStealDone
                ,success_Steal
                ,street1Seen
                ,street2Seen
                ,street3Seen
                ,street4Seen
                ,sawShowdown
                ,street1Aggr
                ,street2Aggr
                ,street3Aggr
                ,street4Aggr
                ,otherRaisedStreet0
                ,otherRaisedStreet1
                ,otherRaisedStreet2
                ,otherRaisedStreet3
                ,otherRaisedStreet4
                ,foldToOtherRaisedStreet0
                ,foldToOtherRaisedStreet1
                ,foldToOtherRaisedStreet2
                ,foldToOtherRaisedStreet3
                ,foldToOtherRaisedStreet4
                ,raiseFirstInChance
                ,raisedFirstIn
                ,foldBbToStealChance
                ,foldedBbToSteal
                ,foldSbToStealChance
                ,foldedSbToSteal
                ,street1CBChance
                ,street1CBDone
                ,street2CBChance
                ,street2CBDone
                ,street3CBChance
                ,street3CBDone
                ,street4CBChance
                ,street4CBDone
                ,foldToStreet1CBChance
                ,foldToStreet1CBDone
                ,foldToStreet2CBChance
                ,foldToStreet2CBDone
                ,foldToStreet3CBChance
                ,foldToStreet3CBDone
                ,foldToStreet4CBChance
                ,foldToStreet4CBDone
                ,totalProfit
                ,street1CheckCallRaiseChance
                ,street1CheckCallRaiseDone
                ,street2CheckCallRaiseChance
                ,street2CheckCallRaiseDone
                ,street3CheckCallRaiseChance
                ,street3CheckCallRaiseDone
                ,street4CheckCallRaiseChance
                ,street4CheckCallRaiseDone
                ,street0Calls
                ,street1Calls
                ,street2Calls
                ,street3Calls
                ,street4Calls
                ,street0Bets
                ,street1Bets
                ,street2Bets
                ,street3Bets
                ,street4Bets
                ,street0Raises
                ,street1Raises
                ,street2Raises
                ,street3Raises
                ,street4Raises
                )
                SELECT h.gametypeId
                      ,hp.playerId
                      ,h.seats
                      ,case when hp.position = 'B' then 'B'
                            when hp.position = 'S' then 'S'
                            when hp.position = '0' then 'D'
                            when hp.position = '1' then 'C'
                            when hp.position = '2' then 'M'
                            when hp.position = '3' then 'M'
                            when hp.position = '4' then 'M'
                            when hp.position = '5' then 'E'
                            when hp.position = '6' then 'E'
                            when hp.position = '7' then 'E'
                            when hp.position = '8' then 'E'
                            when hp.position = '9' then 'E'
                            else 'E'
                       end                                            AS hc_position
                      <tourney_select_clause>
                      ,'d' || to_char(h.startTime, 'YYMMDD')
                      ,count(1)
                      ,sum(wonWhenSeenStreet1)
                      ,sum(wonWhenSeenStreet2)
                      ,sum(wonWhenSeenStreet3)
                      ,sum(wonWhenSeenStreet4)
                      ,sum(wonAtSD)
                      ,sum(CAST(street0VPI as integer))
                      ,sum(CAST(street0Aggr as integer))
                      ,sum(CAST(street0_3BChance as integer))
                      ,sum(CAST(street0_3BDone as integer))
                      ,sum(CAST(street0_4BChance as integer))
                      ,sum(CAST(street0_4BDone as integer))
                      ,sum(CAST(street0_C4BChance as integer))
                      ,sum(CAST(street0_C4BDone as integer))
                      ,sum(CAST(street0_FoldTo3BChance as integer))
                      ,sum(CAST(street0_FoldTo3BDone as integer))
                      ,sum(CAST(street0_FoldTo4BChance as integer))
                      ,sum(CAST(street0_FoldTo4BDone as integer))
                      ,sum(CAST(street0_SqueezeChance as integer))
                      ,sum(CAST(street0_SqueezeDone as integer))
                      ,sum(CAST(raiseToStealChance as integer))
                      ,sum(CAST(raiseToStealDone as integer))
                      ,sum(CAST(success_Steal as integer))
                      ,sum(CAST(street1Seen as integer))
                      ,sum(CAST(street2Seen as integer))
                      ,sum(CAST(street3Seen as integer))
                      ,sum(CAST(street4Seen as integer))
                      ,sum(CAST(sawShowdown as integer))
                      ,sum(CAST(street1Aggr as integer))
                      ,sum(CAST(street2Aggr as integer))
                      ,sum(CAST(street3Aggr as integer))
                      ,sum(CAST(street4Aggr as integer))
                      ,sum(CAST(otherRaisedStreet0 as integer))
                      ,sum(CAST(otherRaisedStreet1 as integer))
                      ,sum(CAST(otherRaisedStreet2 as integer))
                      ,sum(CAST(otherRaisedStreet3 as integer))
                      ,sum(CAST(otherRaisedStreet4 as integer))
                      ,sum(CAST(foldToOtherRaisedStreet0 as integer))
                      ,sum(CAST(foldToOtherRaisedStreet1 as integer))
                      ,sum(CAST(foldToOtherRaisedStreet2 as integer))
                      ,sum(CAST(foldToOtherRaisedStreet3 as integer))
                      ,sum(CAST(foldToOtherRaisedStreet4 as integer))
                      ,sum(CAST(raiseFirstInChance as integer))
                      ,sum(CAST(raisedFirstIn as integer))
                      ,sum(CAST(foldBbToStealChance as integer))
                      ,sum(CAST(foldedBbToSteal as integer))
                      ,sum(CAST(foldSbToStealChance as integer))
                      ,sum(CAST(foldedSbToSteal as integer))
                      ,sum(CAST(street1CBChance as integer))
                      ,sum(CAST(street1CBDone as integer))
                      ,sum(CAST(street2CBChance as integer))
                      ,sum(CAST(street2CBDone as integer))
                      ,sum(CAST(street3CBChance as integer))
                      ,sum(CAST(street3CBDone as integer))
                      ,sum(CAST(street4CBChance as integer))
                      ,sum(CAST(street4CBDone as integer))
                      ,sum(CAST(foldToStreet1CBChance as integer))
                      ,sum(CAST(foldToStreet1CBDone as integer))
                      ,sum(CAST(foldToStreet2CBChance as integer))
                      ,sum(CAST(foldToStreet2CBDone as integer))
                      ,sum(CAST(foldToStreet3CBChance as integer))
                      ,sum(CAST(foldToStreet3CBDone as integer))
                      ,sum(CAST(foldToStreet4CBChance as integer))
                      ,sum(CAST(foldToStreet4CBDone as integer))
                      ,sum(CAST(totalProfit as integer))
                      ,sum(CAST(street1CheckCallRaiseChance as integer))
                      ,sum(CAST(street1CheckCallRaiseDone as integer))
                      ,sum(CAST(street2CheckCallRaiseChance as integer))
                      ,sum(CAST(street2CheckCallRaiseDone as integer))
                      ,sum(CAST(street3CheckCallRaiseChance as integer))
                      ,sum(CAST(street3CheckCallRaiseDone as integer))
                      ,sum(CAST(street4CheckCallRaiseChance as integer))
                      ,sum(CAST(street4CheckCallRaiseDone as integer))
                      ,sum(CAST(street0Calls as integer))
                      ,sum(CAST(street1Calls as integer))
                      ,sum(CAST(street2Calls as integer))
                      ,sum(CAST(street3Calls as integer))
                      ,sum(CAST(street4Calls as integer))
                      ,sum(CAST(street0Bets as integer))
                      ,sum(CAST(street1Bets as integer))
                      ,sum(CAST(street2Bets as integer))
                      ,sum(CAST(street3Bets as integer))
                      ,sum(CAST(street4Bets as integer))
                      ,sum(CAST(hp.street0Raises as integer))
                      ,sum(CAST(hp.street1Raises as integer))
                      ,sum(CAST(hp.street2Raises as integer))
                      ,sum(CAST(hp.street3Raises as integer))
                      ,sum(CAST(hp.street4Raises as integer))
                FROM HandsPlayers hp
                INNER JOIN Hands h ON (h.id = hp.handId)
                <tourney_join_clause>
                <where_clause>
                GROUP BY h.gametypeId
                        ,hp.playerId
                        ,h.seats
                        ,hc_position
                        <tourney_group_clause>
                        ,to_char(h.startTime, 'YYMMDD')
"""
        else:   # assume sqlite
            self.query['rebuildHudCache'] = """
                INSERT INTO HudCache
                (gametypeId
                ,playerId
                ,activeSeats
                ,position
                <tourney_insert_clause>
                ,styleKey
                ,HDs
                ,wonWhenSeenStreet1
                ,wonWhenSeenStreet2
                ,wonWhenSeenStreet3
                ,wonWhenSeenStreet4
                ,wonAtSD
                ,street0VPI
                ,street0Aggr
                ,street0_3BChance
                ,street0_3BDone
                ,street0_4BChance
                ,street0_4BDone
                ,street0_C4BChance
                ,street0_C4BDone
                ,street0_FoldTo3BChance
                ,street0_FoldTo3BDone
                ,street0_FoldTo4BChance
                ,street0_FoldTo4BDone
                ,street0_SqueezeChance
                ,street0_SqueezeDone
                ,raiseToStealChance
                ,raiseToStealDone
                ,success_Steal
                ,street1Seen
                ,street2Seen
                ,street3Seen
                ,street4Seen
                ,sawShowdown
                ,street1Aggr
                ,street2Aggr
                ,street3Aggr
                ,street4Aggr
                ,otherRaisedStreet0
                ,otherRaisedStreet1
                ,otherRaisedStreet2
                ,otherRaisedStreet3
                ,otherRaisedStreet4
                ,foldToOtherRaisedStreet0
                ,foldToOtherRaisedStreet1
                ,foldToOtherRaisedStreet2
                ,foldToOtherRaisedStreet3
                ,foldToOtherRaisedStreet4
                ,raiseFirstInChance
                ,raisedFirstIn
                ,foldBbToStealChance
                ,foldedBbToSteal
                ,foldSbToStealChance
                ,foldedSbToSteal
                ,street1CBChance
                ,street1CBDone
                ,street2CBChance
                ,street2CBDone
                ,street3CBChance
                ,street3CBDone
                ,street4CBChance
                ,street4CBDone
                ,foldToStreet1CBChance
                ,foldToStreet1CBDone
                ,foldToStreet2CBChance
                ,foldToStreet2CBDone
                ,foldToStreet3CBChance
                ,foldToStreet3CBDone
                ,foldToStreet4CBChance
                ,foldToStreet4CBDone
                ,totalProfit
                ,street1CheckCallRaiseChance
                ,street1CheckCallRaiseDone
                ,street2CheckCallRaiseChance
                ,street2CheckCallRaiseDone
                ,street3CheckCallRaiseChance
                ,street3CheckCallRaiseDone
                ,street4CheckCallRaiseChance
                ,street4CheckCallRaiseDone
                ,street0Calls
                ,street1Calls
                ,street2Calls
                ,street3Calls
                ,street4Calls
                ,street0Bets
                ,street1Bets
                ,street2Bets
                ,street3Bets
                ,street4Bets
                ,street0Raises
                ,street1Raises
                ,street2Raises
                ,street3Raises
                ,street4Raises
                )
                SELECT h.gametypeId
                      ,hp.playerId
                      ,h.seats
                      ,case when hp.position = 'B' then 'B'
                            when hp.position = 'S' then 'S'
                            when hp.position = '0' then 'D'
                            when hp.position = '1' then 'C'
                            when hp.position = '2' then 'M'
                            when hp.position = '3' then 'M'
                            when hp.position = '4' then 'M'
                            when hp.position = '5' then 'E'
                            when hp.position = '6' then 'E'
                            when hp.position = '7' then 'E'
                            when hp.position = '8' then 'E'
                            when hp.position = '9' then 'E'
                            else 'E'
                       end                                            AS hc_position
                      <tourney_select_clause>
                      ,'d' || substr(strftime('%Y%m%d', h.startTime),3,7)
                      ,count(1)
                      ,sum(wonWhenSeenStreet1)
                      ,sum(wonWhenSeenStreet2)
                      ,sum(wonWhenSeenStreet3)
                      ,sum(wonWhenSeenStreet4)
                      ,sum(wonAtSD)
                      ,sum(CAST(street0VPI as integer))
                      ,sum(CAST(street0Aggr as integer))
                      ,sum(CAST(street0_3BChance as integer))
                      ,sum(CAST(street0_3BDone as integer))
                      ,sum(CAST(street0_4BChance as integer))
                      ,sum(CAST(street0_4BDone as integer))
                      ,sum(CAST(street0_C4BChance as integer))
                      ,sum(CAST(street0_C4BDone as integer))
                      ,sum(CAST(street0_FoldTo3BChance as integer))
                      ,sum(CAST(street0_FoldTo3BDone as integer))
                      ,sum(CAST(street0_FoldTo4BChance as integer))
                      ,sum(CAST(street0_FoldTo4BDone as integer))
                      ,sum(CAST(street0_SqueezeChance as integer))
                      ,sum(CAST(street0_SqueezeDone as integer))
                      ,sum(CAST(raiseToStealChance as integer))
                      ,sum(CAST(raiseToStealDone as integer))
                      ,sum(CAST(success_Steal as integer))
                      ,sum(CAST(street1Seen as integer))
                      ,sum(CAST(street2Seen as integer))
                      ,sum(CAST(street3Seen as integer))
                      ,sum(CAST(street4Seen as integer))
                      ,sum(CAST(sawShowdown as integer))
                      ,sum(CAST(street1Aggr as integer))
                      ,sum(CAST(street2Aggr as integer))
                      ,sum(CAST(street3Aggr as integer))
                      ,sum(CAST(street4Aggr as integer))
                      ,sum(CAST(otherRaisedStreet0 as integer))
                      ,sum(CAST(otherRaisedStreet1 as integer))
                      ,sum(CAST(otherRaisedStreet2 as integer))
                      ,sum(CAST(otherRaisedStreet3 as integer))
                      ,sum(CAST(otherRaisedStreet4 as integer))
                      ,sum(CAST(foldToOtherRaisedStreet0 as integer))
                      ,sum(CAST(foldToOtherRaisedStreet1 as integer))
                      ,sum(CAST(foldToOtherRaisedStreet2 as integer))
                      ,sum(CAST(foldToOtherRaisedStreet3 as integer))
                      ,sum(CAST(foldToOtherRaisedStreet4 as integer))
                      ,sum(CAST(raiseFirstInChance as integer))
                      ,sum(CAST(raisedFirstIn as integer))
                      ,sum(CAST(foldBbToStealChance as integer))
                      ,sum(CAST(foldedBbToSteal as integer))
                      ,sum(CAST(foldSbToStealChance as integer))
                      ,sum(CAST(foldedSbToSteal as integer))
                      ,sum(CAST(street1CBChance as integer))
                      ,sum(CAST(street1CBDone as integer))
                      ,sum(CAST(street2CBChance as integer))
                      ,sum(CAST(street2CBDone as integer))
                      ,sum(CAST(street3CBChance as integer))
                      ,sum(CAST(street3CBDone as integer))
                      ,sum(CAST(street4CBChance as integer))
                      ,sum(CAST(street4CBDone as integer))
                      ,sum(CAST(foldToStreet1CBChance as integer))
                      ,sum(CAST(foldToStreet1CBDone as integer))
                      ,sum(CAST(foldToStreet2CBChance as integer))
                      ,sum(CAST(foldToStreet2CBDone as integer))
                      ,sum(CAST(foldToStreet3CBChance as integer))
                      ,sum(CAST(foldToStreet3CBDone as integer))
                      ,sum(CAST(foldToStreet4CBChance as integer))
                      ,sum(CAST(foldToStreet4CBDone as integer))
                      ,sum(CAST(totalProfit as integer))
                      ,sum(CAST(street1CheckCallRaiseChance as integer))
                      ,sum(CAST(street1CheckCallRaiseDone as integer))
                      ,sum(CAST(street2CheckCallRaiseChance as integer))
                      ,sum(CAST(street2CheckCallRaiseDone as integer))
                      ,sum(CAST(street3CheckCallRaiseChance as integer))
                      ,sum(CAST(street3CheckCallRaiseDone as integer))
                      ,sum(CAST(street4CheckCallRaiseChance as integer))
                      ,sum(CAST(street4CheckCallRaiseDone as integer))
                      ,sum(CAST(street0Calls as integer))
                      ,sum(CAST(street1Calls as integer))
                      ,sum(CAST(street2Calls as integer))
                      ,sum(CAST(street3Calls as integer))
                      ,sum(CAST(street4Calls as integer))
                      ,sum(CAST(street0Bets as integer))
                      ,sum(CAST(street1Bets as integer))
                      ,sum(CAST(street2Bets as integer))
                      ,sum(CAST(street3Bets as integer))
                      ,sum(CAST(street4Bets as integer))
                      ,sum(CAST(hp.street0Raises as integer))
                      ,sum(CAST(hp.street1Raises as integer))
                      ,sum(CAST(hp.street2Raises as integer))
                      ,sum(CAST(hp.street3Raises as integer))
                      ,sum(CAST(hp.street4Raises as integer))
                FROM HandsPlayers hp
                INNER JOIN Hands h ON (h.id = hp.handId)
                <tourney_join_clause>
                <where_clause>
                GROUP BY h.gametypeId
                        ,hp.playerId
                        ,h.seats
                        ,hc_position
                        <tourney_group_clause>
                        ,'d' || substr(strftime('%Y%m%d', h.startTime),3,7)
"""

        self.query['insert_hudcache'] = """
            insert into HudCache (
                gametypeId,
                playerId,
                activeSeats,
                position,
                tourneyTypeId,
                styleKey,
                HDs,
                street0VPI,
                street0Aggr,
                street0_3BChance,
                street0_3BDone,
                street0_4BChance,
                street0_4BDone,
                street0_C4BChance,
                street0_C4BDone,
                street0_FoldTo3BChance,
                street0_FoldTo3BDone,
                street0_FoldTo4BChance,
                street0_FoldTo4BDone,
                street0_SqueezeChance,
                street0_SqueezeDone,
                raiseToStealChance,
                raiseToStealDone,
                success_Steal,
                street1Seen,
                street2Seen,
                street3Seen,
                street4Seen,
                sawShowdown,
                street1Aggr,
                street2Aggr,
                street3Aggr,
                street4Aggr,
                otherRaisedStreet0,
                otherRaisedStreet1,
                otherRaisedStreet2,
                otherRaisedStreet3,
                otherRaisedStreet4,
                foldToOtherRaisedStreet0,
                foldToOtherRaisedStreet1,
                foldToOtherRaisedStreet2,
                foldToOtherRaisedStreet3,
                foldToOtherRaisedStreet4,
                wonWhenSeenStreet1,
                wonWhenSeenStreet2,
                wonWhenSeenStreet3,
                wonWhenSeenStreet4,
                wonAtSD,
                raiseFirstInChance,
                raisedFirstIn,
                foldBbToStealChance,
                foldedBbToSteal,
                foldSbToStealChance,
                foldedSbToSteal,
                street1CBChance,
                street1CBDone,
                street2CBChance,
                street2CBDone,
                street3CBChance,
                street3CBDone,
                street4CBChance,
                street4CBDone,
                foldToStreet1CBChance,
                foldToStreet1CBDone,
                foldToStreet2CBChance,
                foldToStreet2CBDone,
                foldToStreet3CBChance,
                foldToStreet3CBDone,
                foldToStreet4CBChance,
                foldToStreet4CBDone,
                totalProfit,
                street1CheckCallRaiseChance,
                street1CheckCallRaiseDone,
                street2CheckCallRaiseChance,
                street2CheckCallRaiseDone,
                street3CheckCallRaiseChance,
                street3CheckCallRaiseDone,
                street4CheckCallRaiseChance,
                street4CheckCallRaiseDone,
                street0Calls,
                street1Calls,
                street2Calls,
                street3Calls,
                street4Calls,
                street0Bets,
                street1Bets,
                street2Bets,
                street3Bets,
                street4Bets,
                street0Raises,
                street1Raises,
                street2Raises,
                street3Raises,
                street4Raises)
            values (%s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s)"""

        self.query['update_hudcache'] = """
            UPDATE HudCache SET
            HDs=HDs+%s,
            street0VPI=street0VPI+%s,
            street0Aggr=street0Aggr+%s,
            street0_3BChance=street0_3BChance+%s,
            street0_3BDone=street0_3BDone+%s,
            street0_4BChance=street0_4BChance+%s,
            street0_4BDone=street0_4BDone+%s,
            street0_C4BChance=street0_C4BChance+%s,
            street0_C4BDone=street0_C4BDone+%s,
            street0_FoldTo3BChance=street0_FoldTo3BChance+%s,
            street0_FoldTo3BDone=street0_FoldTo3BDone+%s,
            street0_FoldTo4BChance=street0_FoldTo4BChance+%s,
            street0_FoldTo4BDone=street0_FoldTo4BDone+%s,
            street0_SqueezeChance=street0_SqueezeChance+%s,
            street0_SqueezeDone=street0_SqueezeDone+%s,
            raiseToStealChance=raiseToStealChance+%s,
            raiseToStealDone=raiseToStealDone+%s,
            success_Steal=success_Steal+%s,
            street1Seen=street1Seen+%s,
            street2Seen=street2Seen+%s,
            street3Seen=street3Seen+%s,
            street4Seen=street4Seen+%s,
            sawShowdown=sawShowdown+%s,
            street1Aggr=street1Aggr+%s,
            street2Aggr=street2Aggr+%s,
            street3Aggr=street3Aggr+%s,
            street4Aggr=street4Aggr+%s,
            otherRaisedStreet0=otherRaisedStreet0+%s,
            otherRaisedStreet1=otherRaisedStreet1+%s,
            otherRaisedStreet2=otherRaisedStreet2+%s,
            otherRaisedStreet3=otherRaisedStreet3+%s,
            otherRaisedStreet4=otherRaisedStreet4+%s,
            foldToOtherRaisedStreet0=foldToOtherRaisedStreet0+%s,
            foldToOtherRaisedStreet1=foldToOtherRaisedStreet1+%s,
            foldToOtherRaisedStreet2=foldToOtherRaisedStreet2+%s,
            foldToOtherRaisedStreet3=foldToOtherRaisedStreet3+%s,
            foldToOtherRaisedStreet4=foldToOtherRaisedStreet4+%s,
            wonWhenSeenStreet1=wonWhenSeenStreet1+%s,
            wonWhenSeenStreet2=wonWhenSeenStreet2+%s,
            wonWhenSeenStreet3=wonWhenSeenStreet3+%s,
            wonWhenSeenStreet4=wonWhenSeenStreet4+%s,
            wonAtSD=wonAtSD+%s,
            raiseFirstInChance=raiseFirstInChance+%s,
            raisedFirstIn=raisedFirstIn+%s,
            foldBbToStealChance=foldBbToStealChance+%s,
            foldedBbToSteal=foldedBbToSteal+%s,
            foldSbToStealChance=foldSbToStealChance+%s,
            foldedSbToSteal=foldedSbToSteal+%s,
            street1CBChance=street1CBChance+%s,
            street1CBDone=street1CBDone+%s,
            street2CBChance=street2CBChance+%s,
            street2CBDone=street2CBDone+%s,
            street3CBChance=street3CBChance+%s,
            street3CBDone=street3CBDone+%s,
            street4CBChance=street4CBChance+%s,
            street4CBDone=street4CBDone+%s,
            foldToStreet1CBChance=foldToStreet1CBChance+%s,
            foldToStreet1CBDone=foldToStreet1CBDone+%s,
            foldToStreet2CBChance=foldToStreet2CBChance+%s,
            foldToStreet2CBDone=foldToStreet2CBDone+%s,
            foldToStreet3CBChance=foldToStreet3CBChance+%s,
            foldToStreet3CBDone=foldToStreet3CBDone+%s,
            foldToStreet4CBChance=foldToStreet4CBChance+%s,
            foldToStreet4CBDone=foldToStreet4CBDone+%s,
            totalProfit=totalProfit+%s,
            street1CheckCallRaiseChance=street1CheckCallRaiseChance+%s,
            street1CheckCallRaiseDone=street1CheckCallRaiseDone+%s,
            street2CheckCallRaiseChance=street2CheckCallRaiseChance+%s,
            street2CheckCallRaiseDone=street2CheckCallRaiseDone+%s,
            street3CheckCallRaiseChance=street3CheckCallRaiseChance+%s,
            street3CheckCallRaiseDone=street3CheckCallRaiseDone+%s,
            street4CheckCallRaiseChance=street4CheckCallRaiseChance+%s,
            street4CheckCallRaiseDone=street4CheckCallRaiseDone+%s,
            street0Calls=street0Calls+%s,
            street1Calls=street1Calls+%s,
            street2Calls=street2Calls+%s,
            street3Calls=street3Calls+%s,
            street4Calls=street4Calls+%s,
            street0Bets=street0Bets+%s, 
            street1Bets=street1Bets+%s,
            street2Bets=street2Bets+%s, 
            street3Bets=street3Bets+%s,
            street4Bets=street4Bets+%s, 
            street0Raises=street0Raises+%s,
            street1Raises=street1Raises+%s,
            street2Raises=street2Raises+%s,
            street3Raises=street3Raises+%s,
            street4Raises=street4Raises+%s
        WHERE gametypeId+0=%s
            AND   playerId=%s
            AND   activeSeats=%s
            AND   position=%s
            AND   (case when tourneyTypeId is NULL then 1 else 
                   (case when tourneyTypeId+0=%s then 1 else 0 end) end)=1
            AND   styleKey=%s"""
            
        self.query['get_hero_hudcache_start'] = """select min(hc.styleKey)
                                                   from HudCache hc
                                                   where hc.playerId in <playerid_list>
                                                   and   hc.styleKey like 'd%'"""
            
        ####################################
        # Queries to rebuild/modify sessionscache
        ####################################
        
        self.query['clearSessionsCache'] = """DELETE FROM SessionsCache"""
        
        self.query['rebuildSessionsCache'] = """
                    SELECT Hands.id as id,
                    Hands.startTime as startTime,
                    HandsPlayers.playerId as playerId,
                    Hands.gametypeId as gametypeId,
                    Gametypes.type as game,
                    HandsPlayers.totalProfit as totalProfit,
                    Tourneys.tourneyTypeId as tourneyTypeId
                    FROM Gametypes, HandsPlayers, Hands
                    LEFT JOIN Tourneys ON Hands.tourneyId = Tourneys.tourneyTypeId
                    WHERE HandsPlayers.handId = Hands.id
                    AND   Hands.gametypeId = Gametypes.id
                    AND (case when HandsPlayers.playerId = <where_clause> then 1 else 0 end) = 1
                    ORDER BY Hands.startTime ASC"""
                    
        self.query['rebuildSessionsCacheSum'] = """
                    SELECT Tourneys.id as id,
                    Tourneys.startTime as startTime,
                    TourneysPlayers.playerId,
                    TourneyTypes.id as tourneyTypeId,
                    TourneysPlayers.winnings as winnings,
                    TourneysPlayers.winningsCurrency as winningsCurrency,
                    TourneyTypes.currency as buyinCurrency,
                    TourneyTypes.buyIn as buyIn,
                    TourneyTypes.fee as fee,
                    case when TourneyTypes.rebuy then TourneyTypes.rebuyCost else 0 end as rebuyCost,
                    case when TourneyTypes.rebuy then TourneyTypes.rebuyFee else 0 end as rebuyFee,
                    case when TourneyTypes.addOn then TourneyTypes.addOnCost else 0 end as addOnCost,
                    case when TourneyTypes.addOn then TourneyTypes.addOnFee else 0 end as addOnFee,
                    case when TourneyTypes.knockout then TourneyTypes.koBounty else 0 end as koBounty
                    FROM  Tourneys, TourneyTypes, TourneysPlayers
                    WHERE Tourneys.tourneyTypeId = TourneyTypes.id
                    AND   Tourneys.id = TourneysPlayers.tourneyId
                    AND (case when TourneysPlayers.playerId = <where_clause> then 1 else 0 end) = 1
                    ORDER BY Tourneys.startTime ASC"""
            
        self.query['select_prepSC'] = """
                    SELECT sessionId as id,
                    sessionStart,
                    sessionEnd,
                    count(sessionId) as count
                    FROM SessionsCache
                    WHERE sessionEnd>=%s
                    AND sessionStart<=%s
                    GROUP BY sessionId, sessionStart, sessionEnd"""
                    
        self.query['update_prepSC'] = """
                    UPDATE SessionsCache SET 
                    sessionStart=%s,
                    sessionEnd=%s
                    WHERE sessionId=%s"""
                    
        self.query['update_SC'] = """
                    UPDATE SessionsCache SET 
                    sessionStart=%s,
                    sessionEnd=%s,
                    gameStart=%s,
                    gameEnd=%s,
                    hands=hands+%s,
                    tourneys=tourneys+%s, 
                    totalProfit=totalProfit+%s
                    WHERE id=%s"""
                    
        self.query['select_SC'] = """
                    SELECT id,
                    sessionStart,
                    sessionEnd,
                    gameStart,
                    gameEnd,
                    sessionId,
                    date,
                    type,
                    gametypeId,
                    tourneyTypeId,
                    playerId,
                    hands,
                    tourneys,
                    totalProfit
                    FROM SessionsCache
                    WHERE gameEnd>=%s
                    AND gameStart<=%s
                    AND date=%s
                    AND type=%s
                    AND (case when gametypeId is NULL then 1 else 
                        (case when gametypeId=%s then 1 else 0 end) end)=1
                    AND (case when tourneyTypeId is NULL then 1 else 
                        (case when tourneyTypeId=%s then 1 else 0 end) end)=1
                    AND playerId=%s"""
                    
        self.query['insert_SC'] = """
                    insert into SessionsCache (
                    sessionStart,
                    sessionEnd,
                    gameStart,
                    gameEnd,
                    sessionId,
                    date,
                    type,
                    gametypeId,
                    tourneyTypeId,
                    playerId,
                    hands,
                    tourneys,
                    totalProfit)
                    values (%s, %s, %s, %s, %s, %s, %s, 
                            %s, %s, %s, %s, %s, %s)"""
                            
        self.query['update_Hands_gsid'] = """
                    UPDATE Hands SET
                    gameSessionId=%s
                    WHERE gameSessionId=%s"""
                            
        self.query['update_Hands_sid'] = """
                    UPDATE Hands SET
                    sessionId=%s
                    WHERE sessionId=%s"""
                    
        self.query['update_SC_sid'] = """
                    UPDATE SessionsCache SET
                    sessionStart=%s,
                    sessionEnd=%s,
                    sessionId=%s
                    WHERE sessionId=%s"""
                    
        self.query['delete_SC'] = """
                    DELETE FROM SessionsCache
                    WHERE id=%s"""
        
        ####################################
        # Database management queries
        ####################################

        if db_server == 'mysql':
            self.query['analyze'] = """
            analyze table Autorates, GameTypes, Hands, HandsPlayers, HudCache, Players
                        , Settings, Sites, Tourneys, TourneysPlayers, TourneyTypes
            """
        elif db_server == 'postgresql':
            self.query['analyze'] = "analyze"
        elif db_server == 'sqlite':
            self.query['analyze'] = "analyze"
            
        if db_server == 'mysql':
            self.query['selectLock'] = """
                        SELECT locked 
                        FROM InsertLock 
                        WHERE locked=True 
                        LOCK IN SHARE MODE"""
            
        if db_server == 'mysql':
            self.query['switchLock'] = """
                        UPDATE InsertLock SET
                        locked=%s
                        WHERE id=%s"""
                        
        if db_server == 'mysql':               
            self.query['missedLock'] = """
                        UPDATE InsertLock SET
                        missed=missed+%s
                        WHERE id=%s"""

        if db_server == 'mysql':
            self.query['lockForInsert'] = """
                lock tables Hands write, HandsPlayers write, HandsActions write, Players write
                          , HudCache write, GameTypes write, Sites write, Tourneys write
                          , TourneysPlayers write, TourneyTypes write, Autorates write
                """
        elif db_server == 'postgresql':
            self.query['lockForInsert'] = ""
        elif db_server == 'sqlite':
            self.query['lockForInsert'] = ""

        if db_server == 'mysql':
            self.query['vacuum'] = """optimize table Hands, HandsPlayers, HandsActions, Players
                                                   , HudCache, GameTypes, Sites, Tourneys
                                                   , TourneysPlayers, TourneyTypes, Autorates
                                      """
        elif db_server == 'postgresql':
            self.query['vacuum'] = """ vacuum """
        elif db_server == 'sqlite':
            self.query['vacuum'] = """ vacuum """

        self.query['getGametypeFL'] = """SELECT id
                                           FROM Gametypes
                                           WHERE siteId=%s
                                           AND   type=%s
                                           AND   category=%s
                                           AND   limitType=%s
                                           AND   smallBet=%s
                                           AND   bigBet=%s
        """

        self.query['getGametypeNL'] = """SELECT id
                                           FROM Gametypes
                                           WHERE siteId=%s
                                           AND   type=%s
                                           AND   category=%s
                                           AND   limitType=%s
                                           AND   currency=%s
                                           AND   smallBlind=%s
                                           AND   bigBlind=%s
        """

        self.query['insertGameTypes'] = """INSERT INTO Gametypes
                                              (siteId, currency, type, base, category, limitType
                                              ,hiLo, smallBlind, bigBlind, smallBet, bigBet)
                                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

        self.query['isAlreadyInDB'] = """SELECT id FROM Hands 
                                         WHERE gametypeId=%s AND siteHandNo=%s
        """
        
        self.query['getTourneyTypeIdByTourneyNo'] = """SELECT tt.id,
                                                              tt.buyin,
                                                              tt.fee,
                                                              tt.maxSeats,
                                                              tt.knockout,
                                                              tt.rebuy,
                                                              tt.addOn,
                                                              tt.speed,
                                                              tt.shootout,
                                                              tt.matrix
                                                    FROM TourneyTypes tt 
                                                    INNER JOIN Tourneys t ON (t.tourneyTypeId = tt.id) 
                                                    WHERE t.siteTourneyNo=%s AND tt.siteId=%s
        """
        
        self.query['getTourneyTypeId'] = """SELECT  id
                                            FROM TourneyTypes
                                            WHERE siteId=%s
                                            AND currency=%s
                                            AND buyin=%s
                                            AND fee=%s
                                            AND category=%s
                                            AND limitType=%s
                                            AND maxSeats=%s
                                            AND knockout=%s
                                            AND rebuy=%s
                                            AND addOn=%s
                                            AND speed=%s
                                            AND shootout=%s
                                            AND matrix=%s
        """

        self.query['insertTourneyType'] = """INSERT INTO TourneyTypes
                                                  (siteId, currency, buyin, fee, category, limitType, maxSeats, buyInChips, knockout, koBounty, rebuy,
                                                  addOn ,speed, shootout, matrix, added, addedCurrency)
                                              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        self.query['getTourneyByTourneyNo'] = """SELECT t.*
                                        FROM Tourneys t
                                        INNER JOIN TourneyTypes tt ON (t.tourneyTypeId = tt.id)
                                        WHERE tt.siteId=%s AND t.siteTourneyNo=%s
        """

        self.query['getTourneyInfo'] = """SELECT tt.*, t.*
                                        FROM Tourneys t
                                        INNER JOIN TourneyTypes tt ON (t.tourneyTypeId = tt.id)
                                        INNER JOIN Sites s ON (tt.siteId = s.id)
                                        WHERE s.name=%s AND t.siteTourneyNo=%s
        """

        self.query['getSiteTourneyNos'] = """SELECT t.siteTourneyNo
                                        FROM Tourneys t
                                        INNER JOIN TourneyTypes tt ON (t.tourneyTypeId = tt.id)
                                        INNER JOIN Sites s ON (tt.siteId = s.id)
                                        WHERE tt.siteId=%s
        """

        self.query['getTourneyPlayerInfo'] = """SELECT tp.*
                                        FROM Tourneys t
                                        INNER JOIN TourneyTypes tt ON (t.tourneyTypeId = tt.id)
                                        INNER JOIN Sites s ON (tt.siteId = s.id)
                                        INNER JOIN TourneysPlayers tp ON (tp.tourneyId = t.id)
                                        INNER JOIN Players p ON (p.id = tp.playerId)
                                        WHERE s.name=%s AND t.siteTourneyNo=%s AND p.name=%s
        """
        
        self.query['insertTourney'] = """INSERT INTO Tourneys
                                            (tourneyTypeId, siteTourneyNo, entries, prizepool,
                                             startTime, endTime, tourneyName, matrixIdProcessed,
                                             totalRebuyCount, totalAddOnCount)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        self.query['updateTourney'] = """UPDATE Tourneys
                                             SET entries = %s,
                                                 prizepool = %s,
                                                 startTime = %s,
                                                 endTime = %s,
                                                 tourneyName = %s,
                                                 matrixIdProcessed = %s,
                                                 totalRebuyCount = %s,
                                                 totalAddOnCount = %s,
                                                 comment = %s,
                                                 commentTs = %s
                                        WHERE id=%s
        """
        
        self.query['getTourneysPlayersByIds'] = """SELECT *
                                                FROM TourneysPlayers
                                                WHERE tourneyId=%s AND playerId+0=%s            
        """

        self.query['updateTourneysPlayer'] = """UPDATE TourneysPlayers
                                                 SET rank = %s,
                                                     winnings = %s,
                                                     winningsCurrency = %s,
                                                     rebuyCount = %s,
                                                     addOnCount = %s,
                                                     koCount = %s
                                                 WHERE id=%s
        """

        self.query['insertTourneysPlayer'] = """INSERT INTO TourneysPlayers
                                                    (tourneyId, playerId, rank, winnings, winningsCurrency, rebuyCount, addOnCount, koCount)
                                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        self.query['selectHandsPlayersWithWrongTTypeId'] = """SELECT id
                                                              FROM HandsPlayers 
                                                              WHERE tourneyTypeId <> %s AND (TourneysPlayersId+0=%s)
        """

#            self.query['updateHandsPlayersForTTypeId2'] = """UPDATE HandsPlayers 
#                                                            SET tourneyTypeId= %s
#                                                            WHERE (TourneysPlayersId+0=%s)
#            """

        self.query['updateHandsPlayersForTTypeId'] = """UPDATE HandsPlayers 
                                                         SET tourneyTypeId= %s
                                                         WHERE (id=%s)
        """


        self.query['handsPlayersTTypeId_joiner'] = " OR TourneysPlayersId+0="
        self.query['handsPlayersTTypeId_joiner_id'] = " OR id="

        self.query['store_hand'] = """insert into Hands (
                                            tablename,
                                            sitehandno,
                                            tourneyId,
                                            gametypeid,
                                            sessionId,
                                            gameSessionId,
                                            startTime,
                                            importtime,
                                            seats,
                                            maxseats,
                                            texture,
                                            playersVpi,
                                            boardcard1,
                                            boardcard2,
                                            boardcard3,
                                            boardcard4,
                                            boardcard5,
                                            playersAtStreet1,
                                            playersAtStreet2,
                                            playersAtStreet3,
                                            playersAtStreet4,
                                            playersAtShowdown,
                                            street0Raises,
                                            street1Raises,
                                            street2Raises,
                                            street3Raises,
                                            street4Raises,
                                            street1Pot,
                                            street2Pot,
                                            street3Pot,
                                            street4Pot,
                                            showdownPot
                                             )
                                             values
                                              (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                               %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                               %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""


        self.query['store_hands_players'] = """insert into HandsPlayers (
                handId,
                playerId,
                startCash,
                seatNo,
                sitout,
                card1,
                card2,
                card3,
                card4,
                card5,
                card6,
                card7,
                card8,
                card9,
                card10,
                card11,
                card12,
                card13,
                card14,
                card15,
                card16,
                card17,
                card18,
                card19,
                card20,
                winnings,
                rake,
                totalProfit,
                street0VPI,
                street1Seen,
                street2Seen,
                street3Seen,
                street4Seen,
                sawShowdown,
                wonAtSD,
                street0Aggr,
                street1Aggr,
                street2Aggr,
                street3Aggr,
                street4Aggr,
                street1CBChance,
                street2CBChance,
                street3CBChance,
                street4CBChance,
                street1CBDone,
                street2CBDone,
                street3CBDone,
                street4CBDone,
                wonWhenSeenStreet1,
                wonWhenSeenStreet2,
                wonWhenSeenStreet3,
                wonWhenSeenStreet4,
                street0Calls,
                street1Calls,
                street2Calls,
                street3Calls,
                street4Calls,
                street0Bets,
                street1Bets,
                street2Bets,
                street3Bets,
                street4Bets,
                position,
                tourneysPlayersId,
                startCards,
                street0_3BChance,
                street0_3BDone,
                street0_4BChance,
                street0_4BDone,
                street0_C4BChance,
                street0_C4BDone,
                street0_FoldTo3BChance,
                street0_FoldTo3BDone,
                street0_FoldTo4BChance,
                street0_FoldTo4BDone,
                street0_SqueezeChance,
                street0_SqueezeDone,
                raiseToStealChance,
                raiseToStealDone,
                success_Steal,
                otherRaisedStreet0,
                otherRaisedStreet1,
                otherRaisedStreet2,
                otherRaisedStreet3,
                otherRaisedStreet4,
                foldToOtherRaisedStreet0,
                foldToOtherRaisedStreet1,
                foldToOtherRaisedStreet2,
                foldToOtherRaisedStreet3,
                foldToOtherRaisedStreet4,
                raiseFirstInChance,
                raisedFirstIn,
                foldBbToStealChance,
                foldedBbToSteal,
                foldSbToStealChance,
                foldedSbToSteal,
                foldToStreet1CBChance,
                foldToStreet1CBDone,
                foldToStreet2CBChance,
                foldToStreet2CBDone,
                foldToStreet3CBChance,
                foldToStreet3CBDone,
                foldToStreet4CBChance,
                foldToStreet4CBDone,
                street1CheckCallRaiseChance,
                street1CheckCallRaiseDone,
                street2CheckCallRaiseChance,
                street2CheckCallRaiseDone,
                street3CheckCallRaiseChance,
                street3CheckCallRaiseDone,
                street4CheckCallRaiseChance,
                street4CheckCallRaiseDone,
                street0Raises,
                street1Raises,
                street2Raises,
                street3Raises,
                street4Raises
               )
               values (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s
                )"""

        self.query['store_hands_actions'] = """insert into HandsActions (
                        handId,
                        playerId,
                        street,
                        actionNo,
                        streetActionNo,
                        actionId,
                        amount,
                        raiseTo,
                        amountCalled,
                        numDiscarded,
                        cardsDiscarded,
                        allIn
               )
               values (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s
                )"""
        
        ################################
        # Counts for DB stats window
        ################################
        self.query['getHandCount'] = "SELECT COUNT(*) FROM Hands"
        self.query['getTourneyCount'] = "SELECT COUNT(*) FROM Tourneys"
        self.query['getTourneyTypeCount'] = "SELECT COUNT(*) FROM TourneyTypes"
        
        ################################
        # queries for dumpDatabase
        ################################
        for table in (u'Autorates', u'Backings', u'Gametypes', u'Hands', u'HandsActions', u'HandsPlayers', u'HudCache', u'Players', u'RawHands', u'RawTourneys', u'Settings', u'Sites', u'TourneyTypes', u'Tourneys', u'TourneysPlayers'):
            self.query['get'+table] = u"SELECT * FROM "+table
        
        ################################
        # placeholders and substitution stuff
        ################################
        if db_server == 'mysql':
            self.query['placeholder'] = u'%s'
        elif db_server == 'postgresql':
            self.query['placeholder'] = u'%s'
        elif db_server == 'sqlite':
            self.query['placeholder'] = u'?'


        # If using sqlite, use the ? placeholder instead of %s
        if db_server == 'sqlite':
            for k,q in self.query.iteritems():
                self.query[k] = re.sub('%s','?',q)

if __name__== "__main__":
#    just print the default queries and exit
    s = Sql()
    for key in s.query:
        print "For query " + key + ", sql ="
        print s.query[key]
