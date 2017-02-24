# Elisio

## Introduction

The Elisio project is an attempt to teach computers to scan Latin verses, and to share the results publicly with those who are interested.
Scanning a Latin verse means, in this technical context, to analyze its structural variation of light and heavy syllables.
While this is an ancient art, practiced by the Romans themselves and almost ever since, this kind of data is hard to digitalize manually.

With this scanning engine, we want to allow users to do batch scans of Latin verses,
in hopes that they can eventually retrieve previously unknown information from this heavily stylized use of the Latin language.

## Approach

In scanning a verse, this is a very high-level description of the approach that we took:

1. split the verse into words
2. analyze the letters: remove reading marks, resolve writing conventions (v => u)
3. combine letters into sounds (qu is one sound, *muta cum liquida* also for our purposes)
4. combine sounds into syllables, taking into account the possible ambiguity of semivowels
5. try to determine syllable weights based on the basic weight rules
6. try to see, from the syllable count, whether the verse can legally be a hexameter, pentameter, ... verse
7. try to determine the full verse from the known weights
  a. if this succeeds, store the resulting verse structure and word structures in the database
  b. if this fails, use knowledge in the database from words from successfully parsed verses to determine more known syllables and reanalyze

## Problems and limitations

A small but persistent minority of verses in the extant corpus will probably never be scannable by this algorithm without human intervention.
The problematic types of verses include:

* verses with rare (usually Greek) names, especially if they defy the normal weight rules
* verses with words that must be scanned in non-intuitive ways (e.g. Verg. Aen. I, 2: La-vin-ia is trisyllabic)
* half-verses, most commonly in Vergilius
* verses that have a hiatus
* verses with verb forms that may derive from either volvo or volui (perfect tenses of velle)

Less severe problems include:
* rare words in verses where information is already scarce
* hypermetric verses, again most commonly in Vergilius
* words that have lots of possible declensions (adjectives and verbs), which makes exact word hits less likely

The unique-word problem can be mitigated, hopefully, by teaching Elisio to recognize declensions and conjugations.
This work is ongoing as of February 2017.

The verse analysis algorithm is currently only implemented for hexameters and pentameters.
The lyrical meters, and the scanning horror of the dramatic meters, are not on the realistic roadmap for now.

## Technology

The Elisio engine is built using the programming language Python.
For everything except database access, the implementation should be as framework-agnostic as possible.
For the database itself, and for everything related to the front-end (web service and default client web application), Django is used.
You will need a Django version that supports database migrations (1.7 and up).

The project naturally requires a database connection (see [the BUILDING file](./BUILDING.md));
there are no inherent restrictions on which database to use
except those introduced by Django itself - and the availability of database connectors in Python 3.

## License

Elisio is released under the Affero General Public License (AGPL), a strong copyleft license which still gives third parties
considerable freedom to use the source code contained in this project.
If you are considering forking Elisio or using some of its algorithms,
please check [the license terms](./LICENSE.md) to make yourself acquainted with your rights and obligations.

**Ignorance is not a valid excuse.**

## Further developments

If you're feeling Pythonic, you can look at [the CONTRIBUTING file](./CONTRIBUTING.md) for the contributor guide,
and read [the TODO file](./TODO.md) to see the high-level features we'd like to work on next.

## Building

Please refer to [the BUILDING file](./BUILDING.md) for instructions on how to import and build your own version of the project.

## Major contributors

This project was started by Benoit Lagae as a hobby assignment, coming from his background in Latin linguistics
and his Master's thesis research. The engine and the REST interface are his work.
