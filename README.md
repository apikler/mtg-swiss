# mtg-swiss

This is a script that generates pairings for a swiss-system tournament. The original
use case was to keep track of 5 rounds of a Magic the Gathering tournament with about 30
players that plays out over the course of one round per week.

Features:

* Writes the tournament state to disk in between rounds; no need to keep anything running
* After every round, generates two CSV files that you can import into Google Sheets or Powerpoint:
  * One rankings file that displays the complete rankings (with tiebreakers) of all the players
    after the previous round
  * A "scorecard" that contains pairings for the next round, and lets players enter their results
    for the round whenever they play their match.
* Supports dropping players after each round
* Supports arbitrary manual changes to the auto-generated pairings, if needed

The script implements the algorithm described [here](https://www.wizards.com/dci/downloads/swiss_pairings.pdf) 
and [here](https://www.wizards.com/dci/downloads/tiebreakers.pdf) (for tiebreakers).

## Requirements

Python 3.

## Usage

Note: The following commands assume that you're in a Linux (bash) shell, but it should work
just as well under Windows with the proper syntax substitutions.

### Creating a new tournament

It's helpful to create a new directory for each tournament you run, as the script will output
several files that it's helpful to have in one place. 

To create a new tournament that we're going to call "tourney" in a directory called "tourney_dir"
(you'll need to create tourney_dir yourself first, the script won't do it for you):

```
$ python new_tournament.py --save_to=tourney_dir tourney alice bob carol dan erin frank grace
```

The first argument after the directory is the name of the tournament, and then it's one arg per player name.

This immediately outputs the pairings for round 1 in the terminal. It also creates two files in tourney_dir:

* `scorecard.csv`: CSV file that contains the same pairings that you can import into Google Sheets 
  that lets the players record their scores for the matches.
* `tourney_round0.mtg`: Binary file that contains the state of the tournament. You should read this as: the
  state of the tournament after round 0. In this case that sounds a bit weird, but it just contains the state
  of the tournament at the very start, meaning just the player names and not much else.

In this example there are 7 players, so one person will get a bye.

Note that the tournament file does not contain the pairings for the upcoming round (in this case that's the
pairings for round 1). This is by design so that you can modify the pairings manually if you need to.

### Recording results for a round

Once everyone has played their matches for round 1, it's time to record the results and generate pairings
for round 2.

For this you'll want to create a file (let's call it results_round1.txt) with the following syntax:

grace:2,frank:0
carol:1,alice:2
bob:2,dan:0,-dan
erin:2

Here's how to interpret this:

* Grace played Frank and won 2-0
* Carol played Alice and lost 1-2
* Bob played Dan, won 2-0, and then Dan drops from the tournament
* Erin had a bye, which counts as a 2-0 win.

Note that you have to specify the full pairings here because they were not stored in tourney_round0.mtg.

Once you have your results file, this is how you generate pairings for round 2:

```
python record_results.py tourney_dir/tourney_round0.mtg tourney_dir/results_round1.txt
```

The first argument is a path to the tournament state file for just before this last round was played. The
second argument is a path to the results_round1.txt file you just created.

This will output pairings for round 2 in the terminal, as well as several files:

* A new `scorecard.csv` for round 2 results
* `rankings.csv`, which you can import into Google Sheets/Powerpoint and which contains a full ranking
  of players, including tiebreakers. (This is pretty boring after round 1 but gets more involved in 
  later rounds.)
* `tourney_round1.mtg`, the state of the tournament after round 1. 

The way to think of the above command is that you took the state of the tournament at the start ("round 0"),
added to it the results from round 1, and got as the output the state of the tournament after round 1.

In this example, since Dan dropped from the tournament, he will not appear in the round 2 pairings, and because
there are 6 people remaining, there will be no bye in this round. Dan will continue to appear in the rankings
CSV files, though.

Then to generate pairings for round 3, you'll need to create a new results_round2.txt file and run this command:

```
python record_results.py tourney_dir/tourney_round1.mtg tourney_dir/results_round2.txt
```

## Additional notes

The tournament state files contain all the previous pairings in the tournament up to that point. The script
guarantees that in newly generated pairings, no two people will be paired up who have already played each other,
and if there is a bye, the person who gets it will not have had previously had a bye in the tournament.

When creating results.txt files, you don't need to worry too much about forgetting a player or making a typo. In either
case (not getting results for a player in the tournament, or getting results for an unexpected name) the script
will error and you can fix your mistake.
