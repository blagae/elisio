Elisio
==

Introduction
===
The Elisio project is an attempt to teach computers to scan Latin verses, and to share the results with those who are interested.
Scanning a verse means, in this technical context, to analyze its structural alternation of light and heavy syllables.
While this is an ancient art, practised by the Romans themselves and almost ever since, this kind of data is hard to digitalize manually.

With this scanning engine, we want to allow users to do batch scans of Latin verses, in hopes that that they can eventually retrieve previously unknown information from this heavily stylized use of the Latin language.

Approach
===
In scanning a verse, this is the high-level approach that we took:
# split the verse into words
# analyze the letters: remove reading marks, resolve writing conventions (v => u)
# combine letters into sounds (qu is one sound, muta cum liquida also for our purposes)
# combine sounds into syllables, taking into account the possible ambiguity of semivowels
# try to determine syllable weights based on the basic weight rules
# try to determine the full verse from the known weights
## if this succeeds, store the resulting verse structure and word structures in the database
## if this fails, use knowledge in database from words from succeeding verses to determine more known syllables and reanalyze

Problems and limitations
===

A small but vocal minority of verses in the extant corpus will probably never be scannable by this algorithm without human intervention.
The problematic types of verses include:

* verses with rare (usually Greek) names
* verses with words that must be scanned in non-intuitive ways (e.g. Verg. Aen. I, 2: La-vin-ia)
* half-verses, most commonly in Vergilius
* verses that have a hiatus

Less severe problems include:
* rare words in verses where information is already scarce
* words that have lots of possible declensions (adjectives and verbs) so that exact word hits are more rare

The verse analysis algorithm is currently only implemented for hexameters; a pentameter algorithm is ready but not implemented yet. The lyrical meters, and the programming horror of the dramatic meters, are not on the roadmap for now.

License
===

Elisio is released under the AGPL, a strong copyleft license which still gives third parties considerable freedom to use the source code contained in this project. If you are considering forking Elisio or using some of its algorithms, please check the license terms to make yourself acquainted with your rights and obligations. Ignorance is not a valid excuse.

Further developments
===

If you're feeling Pythonic, you can read the TODO.md file to see the high-level features we'd like to work on next.

Building
===

Please refer to BUILDING.md for instructions on how to import and build your own version of the project.
